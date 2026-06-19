# Health Engine

## Piotroski F-score

The Piotroski F-score is a nine-point score that measures a company's financial strength.

| Signal | Formula | What it measures |
|---|---|---|
| ROA positive | Net Income / Total Assets > 0 | Profitability |
| CFO positive | Cash flow from operations > 0 | Cash generation |
| ROA increasing | Current ROA > Prior ROA | Improving profitability |
| Accruals | Net Income - CFO < 0 | Quality of earnings |
| Leverage decreasing | D/E current < D/E prior | Lower financial risk |
| Liquidity increasing | Current ratio current > prior | Better short-term coverage |
| No dilution | Shares outstanding not increased | Shareholder value preservation |
| Gross margin increasing | Current gross margin > prior | Margin improvement |
| Asset turnover increasing | Sales / Assets current > prior | Efficiency gain |

## Altman Z-score

The Altman Z-score estimates bankruptcy risk using five factors.

| Factor | Formula | Interpretation |
|---|---|---|
| X1 | (Current Assets - Current Liabilities) / Total Assets | Working capital ratio |
| X2 | Retained Earnings / Total Assets | Cumulative profitability |
| X3 | EBIT / Total Assets | Operating earnings |
| X4 | Market Cap / Total Liabilities | Market leverage |
| X5 | Revenue / Total Assets | Asset efficiency |

### Interpretation

- `Z > 2.99` — Safe zone
- `1.81 <= Z <= 2.99` — Grey zone
- `Z < 1.81` — Distress zone

## Examples

Healthy company output:

```json
{
  "piotroski_f": 7,
  "altman_z": 4.2,
  "debt_to_equity": 0.08,
  "current_ratio": 2.1,
  "interest_coverage": 48.3
}
```

Distressed company output:

```json
{
  "piotroski_f": 3,
  "altman_z": 1.5,
  "debt_to_equity": 3.5,
  "current_ratio": 0.8,
  "interest_coverage": 1.2
}
```
