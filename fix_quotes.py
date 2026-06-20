import os

file_path = 'telmus/exporters/html_dashboard.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the double quotes
content = content.replace("''#00d4aa''", "'#00d4aa'")
content = content.replace("''#f78166''", "'#f78166'")
content = content.replace("''#e3b341''", "'#e3b341'")
content = content.replace("''#818cf8''", "'#818cf8'")

# Also fix the regex mistake that might have missed borderWidth: 0 replacement
# Let's check if the bars actually became sharp.
# In the previous view_file, line 1013 still had:
# borderWidth: 1,
# borderSkipped: 'bottom',
# maxBarThickness: 48
# So the regex replacement failed! Let's manually fix it now correctly.

import re
content = re.sub(
    r"borderWidth:\s*1,\s*borderSkipped:\s*'bottom',\s*maxBarThickness:\s*\d+",
    "borderWidth: 0, barPercentage: 0.55, categoryPercentage: 0.8, borderRadius: 0",
    content
)

content = re.sub(
    r"borderColor:\s*\[\s*peV.*?\]",
    "borderColor: 'transparent'",
    content, flags=re.DOTALL
)

# And bump version to 0.1.8 to fix PyPI
content = content.replace('0.1.7', '0.1.8')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Bump pyproject.toml
with open('pyproject.toml', 'r', encoding='utf-8') as f:
    pyproject = f.read()
pyproject = pyproject.replace('version = "0.1.7"', 'version = "0.1.8"')
with open('pyproject.toml', 'w', encoding='utf-8') as f:
    f.write(pyproject)

print("Fixed quotes, fixed regex replacement, bumped to 0.1.8")
