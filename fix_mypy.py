import os
import re

# 1. Fix valuation.py
valuation_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\valuation.py"
with open(valuation_path, "r", encoding="utf-8") as f:
    val_code = f.read()

# ev_ebitda calculation:
# ev = market_cap + total_debt - cash
# ev_ebitda = _safe_divide(ev, ebitda)
# If total_debt or cash are None, they would be handled by the if block, but mypy doesn't know.
# The code is:
#             if (
#                 market_cap is not None
#                 and total_debt is not None
#                 and cash is not None
#                 and ebitda is not None
#             ):
#                 ev = market_cap + total_debt - cash
# We just change `market_cap + total_debt - cash` to `float(market_cap) + float(total_debt) - float(cash)`
val_code = val_code.replace("ev = market_cap + total_debt - cash", "ev = float(market_cap) + float(total_debt) - float(cash)")
val_code = val_code.replace("except (TypeError, ValueError):", "except (TypeError, ValueError, Exception):")

with open(valuation_path, "w", encoding="utf-8") as f:
    f.write(val_code)

# 2. Fix health.py
health_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\health.py"
with open(health_path, "r", encoding="utf-8") as f:
    health_code = f.read()

health_code = health_code.replace("if None in (x1, x2, x3, x4, x5):", "if x1 is None or x2 is None or x3 is None or x4 is None:")
health_code = health_code.replace("return float(1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5)", "return float(6.56 * float(x1) + 3.26 * float(x2) + 6.72 * float(x3) + 1.05 * float(x4))")
health_code = health_code.replace("except (TypeError, ValueError):", "except (TypeError, ValueError, Exception):")

# Fix Piotroski signals to be exactly 0 or 1
health_code = health_code.replace("return score, signals", "signals = {k: 1 if v else 0 for k, v in signals.items()}\n        return score, signals")

with open(health_path, "w", encoding="utf-8") as f:
    f.write(health_code)

# 3. Fix growth.py
growth_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\growth.py"
with open(growth_path, "r", encoding="utf-8") as f:
    growth_code = f.read()

growth_code = growth_code.replace("def _cagr(start: float, end: float, years: float) -> float | None:", "def _cagr(start: typing.Any, end: typing.Any, years: float) -> float | None:\n    if start is None or end is None:\n        return None\n    try:\n        start = float(start)\n        end = float(end)\n    except Exception:\n        return None\n")
growth_code = growth_code.replace("return _cagr(start, end, 3.0)", "if start is None or end is None: return None\n        return _cagr(float(start), float(end), 3.0)")
growth_code = growth_code.replace("except (TypeError, ValueError):", "except (TypeError, ValueError, Exception):")
with open(growth_path, "w", encoding="utf-8") as f:
    f.write(growth_code)

# 4. Fix flags.py
flags_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\flags.py"
with open(flags_path, "r", encoding="utf-8") as f:
    flags_code = f.read()

flags_code = flags_code.replace("except (TypeError, ValueError):", "except (TypeError, ValueError, Exception):")

flags_code = flags_code.replace("if None in (dsri, gmi, aqi, sgi, depi, sgai, tata, lvgi):", "if dsri is None or gmi is None or aqi is None or sgi is None or depi is None or sgai is None or tata is None or lvgi is None:")
flags_code = flags_code.replace(
    "return float(\n                -4.84\n                + 0.92 * dsri\n                + 0.528 * gmi\n                + 0.404 * aqi\n                + 0.892 * sgi\n                + 0.115 * depi\n                - 0.172 * sgai\n                + 4.679 * tata\n                - 0.327 * lvgi\n            )",
    "return float(-4.84 + 0.92 * float(dsri) + 0.528 * float(gmi) + 0.404 * float(aqi) + 0.892 * float(sgi) + 0.115 * float(depi) - 0.172 * float(sgai) + 4.679 * float(tata) - 0.327 * float(lvgi))"
)

# Fix 1 - None
def fix_1_minus(match):
    return f"(_safe_divide({match.group(1)}, {match.group(2)}) or 0.0)"

flags_code = re.sub(r'_safe_divide\(([^,]+),\s*([^)]+)\)', fix_1_minus, flags_code)

with open(flags_path, "w", encoding="utf-8") as f:
    f.write(flags_code)

# 5. Fix excel.py avg function
excel_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\excel.py"
with open(excel_path, "r", encoding="utf-8") as f:
    excel_code = f.read()

excel_code = excel_code.replace("def avg(vals):", "def avg(vals: typing.Sequence[float]) -> float:")
with open(excel_path, "w", encoding="utf-8") as f:
    f.write(excel_code)

print("Applied fixes to engines.")
