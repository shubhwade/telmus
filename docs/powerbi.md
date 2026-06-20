# Power BI Integration Guide

This guide explains how to use `telmus` to generate datasets optimized for **Microsoft Power BI**, import them, construct interactive financial dashboards, and automate data refreshes to monitor stock metrics over time.

---

## 1. What is Power BI Desktop?

**Power BI Desktop** is a free, professional data visualization and business intelligence application developed by Microsoft. It allows you to connect to multiple data sources, clean and transform data, and build highly interactive reports with drag-and-drop visuals.

- **Download Link**: You can download it for free directly from the [Microsoft Store](https://aka.ms/pbidesktopstore) or from the [official Power BI download page](https://powerbi.microsoft.com/desktop/).

---

## 2. Generating the Power BI CSV Files

Use `telmus` to export fundamental stock data. `telmus` outputs null values as empty fields (`""`) rather than placeholder strings (like `"n/a"`), allowing Power BI to automatically parse them as numeric types (Decimal, Integer) rather than Text.

### Standard Portfolio Export
Run this command to export general valuation, health, and growth metrics:
```bash
telmus powerbi --tickers INFY TCS WIPRO HDFCBANK RELIANCE.NS --export portfolio.csv
```

### Red Flags Export (Granular tracking)
Run this command to export flag-level details for each ticker (one row per flag per ticker):
```bash
telmus powerbi --tickers INFY TCS WIPRO --flags --export flags.csv
```

---

## 3. Importing Data into Power BI

1. Open **Power BI Desktop**.
2. On the **Home** ribbon, click on **Get Data** and select **Text/CSV**.
3. Choose your exported `portfolio.csv` (or `flags.csv`) and click **Open**.
4. In the preview window, confirm that columns are formatted properly.
5. Click **Load** (or click **Transform Data** if you wish to adjust columns, rename fields, or merge sources in the Power Query editor first).

---

## 4. Building the Visuals

Construct a premium financial dashboard using these six visuals:

### 1. Bar Chart: Piotroski F-Score by Company
* **Visual Type**: *Clustered Bar Chart* or *Clustered Column Chart*.
* **Configuration**:
  - **Y-Axis / X-Axis (Categories)**: Drag the `Ticker` field.
  - **X-Axis / Y-Axis (Values)**: Drag `Piotroski_F` and set it to **Average** (or Sum).
* **Styling**: Turn on **Data Labels** and set the bar fill color to a deep steel blue.
* **What it looks like**: A clean horizontal bar chart showing each stock on the y-axis, with its corresponding Piotroski score represented by a colored bar extending to the right (scores range from 0 to 9).

### 2. Scatter Plot: P/E Ratio vs. Revenue CAGR
* **Visual Type**: *Scatter Chart*.
* **Configuration**:
  - **X-Axis**: Drag `PE_Ratio` (Average).
  - **Y-Axis**: Drag `Revenue_CAGR_3Y` (Average).
  - **Values**: Drag `Ticker`.
  - **Size (Bubble size)**: Drag `PE_Ratio` or another volume metric (like Piotroski score) to represent valuation size.
* **What it looks like**: A 2D quadrant bubble chart. Strong growth/cheap value stocks will sit in the upper-left quadrant (low P/E, high growth), while expensive/low-growth stocks sit in the bottom-right.

### 3. Card Visuals: Core Health KPIs
* **Visual Type**: *Card* (or *Multi-row card*).
* **Visual 1**:
  - **Field**: Drag `Piotroski_F` and set to **Average**.
  - **Label**: Rename to "Avg Piotroski F-Score".
* **Visual 2**:
  - **Field**: Drag `Altman_Z` and set to **Average**.
  - **Label**: Rename to "Avg Altman Z-Score".
* **What it looks like**: Large, clean callout cards showing the average scores across your entire portfolio (e.g., a big bold **5.45** and **4.82**).

### 4. Table: Portfolio Summary & Conditional Formatting
* **Visual Type**: *Table*.
* **Configuration**:
  - Add columns: `Ticker`, `Company`, `PE_Ratio`, `Piotroski_F`, `Altman_Z`, `Highest_Concern`, `Analyst_Brief`.
* **Conditional Formatting**:
  - Right-click `Highest_Concern` (or the `Ticker` cell) in the Visualizations pane, go to **Conditional formatting** > **Background color**.
  - Set Rules based on the `Highest_Concern` field:
    - If value is `high` -> Soft Red background (`#F8D7DA`)
    - If value is `medium` -> Soft Orange background (`#FFF3CD`)
    - If value is `low` -> Soft Green background (`#D4EDDA`)
* **What it looks like**: A tabular grid with all company metrics. Cells under the concern or ticker column will be highlighted in green, yellow, or red based on their financial risk.

### 5. Donut Chart: Risk Level Distribution
* **Visual Type**: *Donut Chart*.
* **Configuration**:
  - **Legend**: Drag `Highest_Concern`.
  - **Values**: Drag `Ticker` (Count or Count Distinct).
* **Styling**: Map green to `low`, orange to `medium`, and red to `high`.
* **What it looks like**: A segmented circle showing the percentage of your portfolio in each risk category.

### 6. Line Chart: Track Scores Over Time
* **Visual Type**: *Line Chart*.
* **Configuration**:
  - **X-Axis**: Drag `Date`.
  - **Y-Axis**: Drag `Piotroski_F` (Average) or `Altman_Z` (Average).
  - **Legend**: Drag `Ticker`.
* **What it looks like**: A multi-line chart with dates on the horizontal axis and scores on the vertical axis, mapping the score changes of each company week-over-week.

---

## 5. Setting Up Auto-Refreshes & Historical Tracking

To track historical trends in Power BI, you must append weekly/monthly runs to the same dataset.

### Step 1: Scripting the Append
Instead of overwriting the CSV, write a script that runs `telmus` and appends rows to your portfolio master CSV:
```powershell
# PowerShell script (e.g., update_portfolio.ps1)
# Fetch standard metrics for this week and append to master database
telmus powerbi --tickers INFY TCS WIPRO --export temp_week.csv

# If master.csv doesn't exist, create it with headers, otherwise skip headers and append
if (-Not (Test-Path master.csv)) {
    Copy-Item temp_week.csv master.csv
} else {
    # Skip the header row (first line) and append the data to master.csv
    Get-Content temp_week.csv | Select-Object -Skip 1 | Add-Content master.csv
}
Remove-Item temp_week.csv
```

### Step 2: Task Scheduling
Schedule this script to run weekly using **Windows Task Scheduler**:
1. Open Task Scheduler and click **Create Basic Task**.
2. Set Trigger to **Weekly** (e.g., every Sunday at 6 PM).
3. Set Action to **Start a program**.
4. Program: `powershell.exe`
5. Arguments: `-File C:\path\to\update_portfolio.ps1`

### Step 3: Refreshing Power BI
Inside Power BI Desktop, clicking the **Refresh** button on the Home ribbon will reload `master.csv`, pulling in the new weekly data points. The line charts will automatically draw the new historical trends based on the `Date` column!
