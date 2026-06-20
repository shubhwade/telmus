import os

val_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\valuation.py"
with open(val_path, "r", encoding="utf-8") as f:
    code = f.read()

# Add flag for negative PE/EBITDA
if "if pe_ratio is not None and pe_ratio < 0:" not in code:
    code = code.replace(
        "return ValuationResult(",
        "if pe_ratio is not None and pe_ratio < 0:\n            flag = 'negative earnings'\n        if ev_ebitda is not None and ev_ebitda < 0 and flag is None:\n            flag = 'negative ebitda'\n        return ValuationResult("
    )

with open(val_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed valuation.py")
