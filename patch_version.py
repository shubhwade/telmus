import os

path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\html_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add import if not present
if "from telmus import __version__ as telmus_version" not in content:
    content = content.replace(
        "from telmus.core.result import ScanResult, CompareResult", 
        "from telmus.core.result import ScanResult, CompareResult\nfrom telmus import __version__ as telmus_version"
    )

# Replace hardcoded v0.1.8
content = content.replace("v0.1.8", "v{telmus_version}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Version strings and imports patched!")
