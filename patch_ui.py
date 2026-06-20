import os

path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\html_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add import
if "from telmus import __version__" not in content:
    content = content.replace("from telmus.core.result import ScanResult, CompareResult", "from telmus.core.result import ScanResult, CompareResult\nfrom telmus import __version__ as telmus_version")

# 2. Fix CSS grids to prevent overflow
css_target = """.grid-2 { display: grid; grid-template-columns: 1fr; gap: 1rem; }
        @media (min-width: 1024px) { .grid-2 { grid-template-columns: repeat(2, 1fr); } }"""
css_replacement = """.grid-2 { display: grid; grid-template-columns: 1fr; gap: 1rem; }
        @media (min-width: 1024px) { .grid-2 { grid-template-columns: repeat(2, 1fr); } }
        .grid-4 > div, .grid-3 > div, .grid-2 > div { min-width: 0; }"""
if ".grid-4 > div, .grid-3 > div, .grid-2 > div { min-width: 0; }" not in content:
    content = content.replace(css_target, css_replacement)

# 3. Fix version hardcoding
content = content.replace("v0.1.8", "v{telmus_version}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("html_dashboard.py patched.")
