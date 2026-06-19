# SDK

Use the Python SDK to embed valkit in notebooks or automation.

```python
from valkit import scan, compare

result = scan("INFY")
print(result.analyst_brief)

comparison = compare("INFY", "TCS")
print(comparison.result_a.valuation.pe_ratio)
```

For DataFrame output:

```python
from valkit.sdk.reconciler import compare_to_dataframe

comparison = compare("INFY", "TCS")
df = compare_to_dataframe(comparison)
print(df)
```
