import os

path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\html_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add extra responsive rules to ensure Chart.js canvases don't stretch the grid
css_patch = """.grid-4 > div, .grid-3 > div, .grid-2 > div { min-width: 0; }"""
new_css_patch = """.grid-4 > div, .grid-3 > div, .grid-2 > div { min-width: 0; max-width: 100%; overflow: hidden; }
        .chart-box { position: relative; width: 100%; max-width: 100%; overflow: hidden; }"""

if ".grid-4 > div, .grid-3 > div, .grid-2 > div { min-width: 0; }" in content:
    content = content.replace(css_patch, new_css_patch)

# Also ensure .chart-box is defined if it's currently just { position: relative; }
content = content.replace("/* Chart container */\n        .chart-box { position: relative; }", "/* Chart container */\n        .chart-box { position: relative; width: 100%; overflow: hidden; }")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied extra CSS patches for Chart.js responsiveness.")
