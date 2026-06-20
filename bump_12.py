import os

# Bump to 0.1.12
files_to_bump = ["pyproject.toml", "telmus/__init__.py"]
for path in files_to_bump:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("0.1.11", "0.1.12")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

with open("docs/changelog.md", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("## v0.1.11 - HTML Dashboard Variable Hardening", "## v0.1.12 - Compare Dashboard JS Fix\n- Removed dangling JS bracket that caused syntax errors and blank compare charts\n\n## v0.1.11 - HTML Dashboard Variable Hardening")
with open("docs/changelog.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Version bumped to 0.1.12")
