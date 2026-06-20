import re

path = "telmus/exporters/html_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace radar_labels with signal_names
content = content.replace("radar_labels", "signal_names")

# Ensure all None values are replaced with 0 or "" for numeric variables
# Let's add default values in Python before injecting:
# Find: pe = result.valuation.pe_ratio
# and make sure it has 'or 0.0'
replacements = [
    ("pe = result.valuation.pe_ratio", "pe = result.valuation.pe_ratio or 0.0"),
    ("pio = result.health.piotroski_f", "pio = result.health.piotroski_f or 0"),
    ("altman = result.health.altman_z", "altman = result.health.altman_z or 0.0"),
    ("rev_cagr = result.growth.revenue_cagr_3y", "rev_cagr = result.growth.revenue_cagr_3y or 0.0"),
    ("fcf_yield = result.growth.fcf_yield", "fcf_yield = result.growth.fcf_yield or 0.0"),
    ("m_score = result.beneish_m if result.beneish_m is not None else -2.22", "m_score = result.beneish_m if result.beneish_m is not None else 0.0"),
    ("de_val = result.health.debt_to_equity", "de_val = result.health.debt_to_equity or 0.0"),
    ("cr_val = result.health.current_ratio", "cr_val = result.health.current_ratio or 0.0"),
    ("ic_val = result.health.interest_coverage", "ic_val = result.health.interest_coverage or 0.0"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied variable fixes to html_dashboard.py")
