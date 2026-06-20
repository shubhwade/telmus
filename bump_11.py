import os

# Bump to 0.1.11
files_to_bump = ["pyproject.toml", "telmus/__init__.py"]
for path in files_to_bump:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("0.1.10", "0.1.11")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

with open("docs/changelog.md", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("## v0.1.10 - Hotfix Dashboard Charts", "## v0.1.11 - HTML Dashboard Variable Hardening\n- Safely fallback missing values to 0 to prevent JavaScript errors\n- Fully mapped all radar chart labels and overlay datasets to variables correctly\n\n## v0.1.10 - Hotfix Dashboard Charts")
with open("docs/changelog.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Version bumped to 0.1.11")
