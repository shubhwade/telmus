import re
import os

# Fix tests
for root, _, files in os.walk("tests"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # Replace 6 Nones with 1 None, {}, and 5 Nones
            content = content.replace(
                "HealthResult(None, None, None, None, None, None)",
                "HealthResult(None, {}, None, None, None, None, None)"
            )
            # Also in test_cli.py there is a mock:
            content = content.replace(
                "health=HealthResult(piotroski_f=7, altman_z=4.0, debt_to_equity=0.1, current_ratio=2.0, interest_coverage=40.0, flag=None)",
                "health=HealthResult(piotroski_f=7, piotroski_signals={'ROA Positive': True, 'CFO Positive': True, 'ROA Improving': True, 'Low Accruals': True, 'Leverage Falling': True, 'Liquidity Rising': True, 'No Dilution': True, 'Gross Margin Rising': False, 'Asset Turnover Rising': False}, altman_z=4.0, debt_to_equity=0.1, current_ratio=2.0, interest_coverage=40.0, flag=None)"
            )
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# Bump to 0.1.9
files_to_bump = ["pyproject.toml", "telmus/__init__.py"]
for path in files_to_bump:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("0.1.8", "0.1.9")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

with open("docs/changelog.md", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("## v0.1.8 - Professional Dashboard Polish", "## v0.1.9 - Final Polish & Chart Bug Fixes\n- Full synchronization\n- Fixed piotroski chart vanishing\n\n## v0.1.8 - Professional Dashboard Polish")
with open("docs/changelog.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Tests fixed and version bumped to 0.1.9")
