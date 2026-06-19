# Health Engine Reference

The health engine combines earnings quality, leverage, liquidity, and bankruptcy risk into a single review.

## Piotroski F-score

The Piotroski F-score is a nine-point score that measures financial strength.

| Signal | What it measures | Formula | Pass condition |
|---|---|---|---|
| ROA positive | Profitability | Net income / Total assets | > 0 |
| CFO positive | Cash generation | Operating cash flow > 0 | true |
| ROA increasing | Improving profitability | Current ROA > Prior ROA | true |
| Accruals | Quality of earnings | Net income - CFO < 0 | true |
| Leverage decreasing | Lower financial risk | Current D/E < Prior D/E | true |
| Liquidity increasing | Short-term coverage | Current current ratio > Prior current ratio | true |
| No dilution | Shareholder preservation | Shares outstanding not increased | true |
| Gross margin increasing | Margin improvement | Current gross margin > Prior gross margin | true |
| Asset turnover increasing | Efficiency gain | Current asset turnover > Prior asset turnover | true |

### Score interpretation

| Score | Interpretation |
|---|---|
| 0-2 | Distressed |
| 3�4 | Weak |
| 5�6 | Adequate |
| 7�9 | Strong |

## Altman Z-score

The Altman Z-score uses five weighted factors to estimate bankruptcy risk.

| Factor | Formula | Weight | What it measures |
|---|---|---|---|
| X1 | (Current assets � Current liabilities) / Total assets | 1.2 | Working capital efficiency |
| X2 | Retained earnings / Total assets | 1.4 | Cumulative profitability |
| X3 | EBIT / Total assets | 3.3 | Operating earnings |
| X4 | Market value of equity / Total liabilities | 0.6 | Market leverage |
| X5 | Revenue / Total assets | 1.0 | Asset turnover |

### Zone interpretation

- `Z > 2.99` � safe zone
- `1.81 <= Z <= 2.99` � grey zone
- `Z < 1.81` � distress zone

## Debt/Equity interpretation

- `< 0.5` � low leverage, conservative balance sheet
- `0.5�1.5` � moderate leverage
- `> 1.5` � high leverage, higher risk

Debt/equity is a core indicator of capital structure risk and should be interpreted with sector context.

## Current ratio interpretation

- `> 1.5` � healthy short-term liquidity
- `1.0�1.5` � adequate but watch working capital
- `< 1.0` � liquidity stress

The current ratio shows whether current assets are sufficient to cover current liabilities.

## Interest coverage interpretation

- `> 10` � strong coverage
- `3�10` � moderate coverage
- `< 3` � weak coverage
- `< 1` � potential distress

Interest coverage measures the ability to pay interest from operating profits.

## Real example

### Healthy company

```json
{
  "ticker": "TCS",
  "piotroski_f": 8,
  "altman_z": 4.5,
  "debt_to_equity": 0.14,
  "current_ratio": 2.2,
  "interest_coverage": 45.0
}
```

### Distressed company

```json
{
  "ticker": "EXAMPLE",
  "piotroski_f": 2,
  "altman_z": 1.3,
  "debt_to_equity": 3.8,
  "current_ratio": 0.8,
  "interest_coverage": 1.1
}
```
