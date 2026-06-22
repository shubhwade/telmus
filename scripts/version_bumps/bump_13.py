import os

path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\__init__.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("0.1.12", "0.1.13")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\pyproject.toml"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("0.1.12", "0.1.13")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\docs\changelog.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("## v0.1.12 - Compare Dashboard JS Fix", "## v0.1.13 - Dashboard Layout and Versioning Polish\n- Fixed CSS layout causing Compare dashboard bar charts to overflow horizontally\n- UI components now dynamically read system version instead of hardcoding\n\n## v0.1.12 - Compare Dashboard JS Fix")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Version bumped to 0.1.13")
