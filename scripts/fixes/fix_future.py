import glob

files = [
    "telmus/cli/app.py",
    "telmus/core/scanner.py",
    "telmus/core/engines/growth.py",
    "telmus/core/engines/health.py",
    "telmus/core/engines/valuation.py",
    "telmus/exporters/html_dashboard.py"
]

for f in files:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
    content = content.replace("import typing\nfrom __future__ import annotations", "from __future__ import annotations\nimport typing")
    with open(f, "w", encoding="utf-8") as file:
        file.write(content)

print("Fixed syntax errors.")
