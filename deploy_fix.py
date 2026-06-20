import os

# Bump to 0.1.10
files_to_bump = ["pyproject.toml", "telmus/__init__.py"]
for path in files_to_bump:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("0.1.9", "0.1.10")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

with open("docs/changelog.md", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("## v0.1.9 - Final Polish & Chart Bug Fixes", "## v0.1.10 - Hotfix Dashboard Charts\n- Fixed an f-string rendering issue preventing charts from displaying\n\n## v0.1.9 - Final Polish & Chart Bug Fixes")
with open("docs/changelog.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Version bumped to 0.1.10")
