import os
import re

# Fix app.py security issue and typing
app_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\cli\app.py"
with open(app_path, "r", encoding="utf-8") as f:
    app_code = f.read()
app_code = app_code.replace("import subprocess\n            subprocess.Popen([\"start\", html_path], shell=True)", "import webbrowser\n            webbrowser.open(html_path)")
app_code = app_code.replace("import subprocess\n        subprocess.Popen([\"start\", f\"{name}_dashboard.html\"], shell=True)", "import webbrowser\n        webbrowser.open(f\"{name}_dashboard.html\")")
app_code = app_code.replace("import subprocess\n    subprocess.Popen([\"start\", \"screen_dashboard.html\"], shell=True)", "import webbrowser\n    webbrowser.open(\"screen_dashboard.html\")")
app_code = app_code.replace("list[tuple[str, object | None, str | None]]", "typing.Sequence[tuple[str, object | None, str | None]]")
if "import typing" not in app_code:
    app_code = "import typing\n" + app_code
with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_code)

# Fix excel.py mypy issues (any -> typing.Any)
excel_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\excel.py"
with open(excel_path, "r", encoding="utf-8") as f:
    excel_code = f.read()
excel_code = excel_code.replace("def export(self, result: ScanResult, path: str) -> None:", "import typing\n    def export(self, result: ScanResult, path: str) -> None:")
excel_code = excel_code.replace(": any", ": typing.Any")
excel_code = excel_code.replace("import logging\n\nlogger = logging.getLogger(__name__)\n", "")
excel_code = "import logging\nlogger = logging.getLogger(__name__)\n" + excel_code
with open(excel_path, "w", encoding="utf-8") as f:
    f.write(excel_code)

# Fix powerbi.py mypy issues
pbi_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\powerbi.py"
with open(pbi_path, "r", encoding="utf-8") as f:
    pbi_code = f.read()
pbi_code = "import typing\nfrom telmus.core.result import ScanResult\n" + pbi_code
pbi_code = pbi_code.replace(": any", ": typing.Any")
with open(pbi_path, "w", encoding="utf-8") as f:
    f.write(pbi_code)

# Fix html_dashboard.py mypy issues
html_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\html_dashboard.py"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()
html_code = "import typing\n" + html_code
html_code = html_code.replace(": any", ": typing.Any")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)

print("Applied fixes for bandit and mypy.")
