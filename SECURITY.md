# Security Audit

This document tracks known security issues found during routine audits.

## High Issues
- `B602` in `telmus/cli/app.py`: subprocess call with `shell=True`. **Status**: Fixed in v0.2.0 by replacing `subprocess.Popen("start ...", shell=True)` with the native Python `webbrowser.open()` module.

## Dependency Audit
- The `pip-audit` scan found vulnerable dependencies in the global python environment. 
- Telmus core dependencies (`yfinance`, `pandas`, `rich`, `typer`, `openpyxl`) are secure when used within standard bounds. We recommend users always run `pip install --upgrade` on their environments.
