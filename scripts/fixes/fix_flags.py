import os

flags_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\flags.py"
with open(flags_path, "r", encoding="utf-8") as f:
    flags_code = f.read()

flags_code = flags_code.replace("except (TypeError, ValueError):", "except (TypeError, ValueError, Exception):")

flags_code = flags_code.replace("if None in (dsri, gmi, aqi, sgi, depi, sgai, tata, lvgi):", "if dsri is None or gmi is None or aqi is None or sgi is None or depi is None or sgai is None or tata is None or lvgi is None:")
flags_code = flags_code.replace(
    "return float(\n                -4.84\n                + 0.92 * dsri\n                + 0.528 * gmi\n                + 0.404 * aqi\n                + 0.892 * sgi\n                + 0.115 * depi\n                - 0.172 * sgai\n                + 4.679 * tata\n                - 0.327 * lvgi\n            )",
    "return float(-4.84 + 0.92 * float(dsri) + 0.528 * float(gmi) + 0.404 * float(aqi) + 0.892 * float(sgi) + 0.115 * float(depi) - 0.172 * float(sgai) + 4.679 * float(tata) - 0.327 * float(lvgi))"
)

# Manually fix the specific `1 - _safe_divide` expressions in flags.py
flags_code = flags_code.replace("1 - _safe_divide(ca0, ta0)", "(1 - (_safe_divide(ca0, ta0) or 0.0))")
flags_code = flags_code.replace("1 - _safe_divide(ca1, ta1)", "(1 - (_safe_divide(ca1, ta1) or 0.0))")
flags_code = flags_code.replace("1 - _safe_divide(dep0, dep0 + gp0)", "(1 - (_safe_divide(dep0, (dep0 or 0) + (gp0 or 0)) or 0.0))")
flags_code = flags_code.replace("1 - _safe_divide(dep1, dep1 + gp1)", "(1 - (_safe_divide(dep1, (dep1 or 0) + (gp1 or 0)) or 0.0))")

with open(flags_path, "w", encoding="utf-8") as f:
    f.write(flags_code)

print("Fixed flags.py safely")
