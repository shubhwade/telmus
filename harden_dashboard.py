import re
import os

path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\html_dashboard.py"

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Make sure we don't have missing variables by ensuring `radar_labels` and `radar_data` are aliased properly if needed.
# Since we use `signal_names` and `signal_values`, we can alias them just in case some other code references them.
code = code.replace(
    "signal_names = list(signals_desc.keys())",
    "signal_names = list(signals_desc.keys())\n        radar_labels = signal_names  # fallback alias\n        radar_data = signal_values  # fallback alias\n        chart_labels = signal_names  # fallback alias\n"
)

# In `export_scan`, let's wrap data extraction in try/except as requested.
# I will do this by injecting a safe getter function.
safe_getter = """
        def _safe_get(obj, attr, default=0.0):
            try:
                val = getattr(obj, attr)
                return val if val is not None else default
            except Exception:
                return default
"""

code = code.replace("def export_scan(self, result: ScanResult, path: str) -> None:", "def export_scan(self, result: ScanResult, path: str) -> None:\n" + safe_getter)

code = code.replace("pe = result.valuation.pe_ratio or 0.0", "pe = _safe_get(result.valuation, 'pe_ratio', 0.0)")
code = code.replace("pio = result.health.piotroski_f or 0", "pio = _safe_get(result.health, 'piotroski_f', 0)")
code = code.replace("altman = result.health.altman_z or 0.0", "altman = _safe_get(result.health, 'altman_z', 0.0)")
code = code.replace("rev_cagr = result.growth.revenue_cagr_3y or 0.0", "rev_cagr = _safe_get(result.growth, 'revenue_cagr_3y', 0.0)")
code = code.replace("fcf_yield = result.growth.fcf_yield or 0.0", "fcf_yield = _safe_get(result.growth, 'fcf_yield', 0.0)")

code = code.replace("pb_val = result.valuation.pb_ratio if result.valuation.pb_ratio is not None else 0.0", "pb_val = _safe_get(result.valuation, 'pb_ratio', 0.0)")
code = code.replace("ev_val = result.valuation.ev_ebitda if result.valuation.ev_ebitda is not None else 0.0", "ev_val = _safe_get(result.valuation, 'ev_ebitda', 0.0)")

# Ensure Javascript template strings have curly braces escaped.
# Actually, the f-string already uses `{{` and `}}` correctly for JS. 
# But just to be sure, any unescaped `{` in JS functions should be double-checked.
# The code currently uses `{{` and `}}` in JS blocks correctly since it executes without SyntaxError.

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Hardened html_dashboard.py")
