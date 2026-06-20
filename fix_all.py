import re
import os

# 1. Update HealthResult in result.py
with open("telmus/core/result.py", "r", encoding="utf-8") as f:
    content = f.read()
if "piotroski_signals: dict[str, bool]" not in content:
    content = content.replace("piotroski_f: int | None", "piotroski_f: int | None\n    piotroski_signals: dict[str, bool]")
with open("telmus/core/result.py", "w", encoding="utf-8") as f:
    f.write(content)

# 2. Update health.py
with open("telmus/core/engines/health.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("def _compute_piotroski(\n        self,\n        income_stmt: pd.DataFrame,\n        balance_sheet: pd.DataFrame,\n        cashflow: pd.DataFrame,\n    ) -> int | None:", "def _compute_piotroski(\n        self,\n        income_stmt: pd.DataFrame,\n        balance_sheet: pd.DataFrame,\n        cashflow: pd.DataFrame,\n    ) -> tuple[int | None, dict]:")

content = re.sub(
    r"score = 0\s+score \+= 1 if self\._roa_positive.*?return score",
    """signals = {}
        signals["ROA Positive"] = self._roa_positive(income_stmt, balance_sheet)
        signals["CFO Positive"] = self._cfo_positive(cashflow)
        signals["ROA Improving"] = self._roa_increasing(income_stmt, balance_sheet)
        signals["Low Accruals"] = self._accruals(income_stmt, cashflow)
        signals["Leverage Falling"] = self._leverage_decreasing(balance_sheet)
        signals["Liquidity Rising"] = self._liquidity_increasing(balance_sheet)
        signals["No Dilution"] = self._no_dilution(balance_sheet)
        signals["Gross Margin Rising"] = self._gross_margin_increasing(income_stmt)
        signals["Asset Turnover Rising"] = self._asset_turnover_increasing(income_stmt, balance_sheet)
        score = sum(1 for v in signals.values() if v)
        return score, signals""",
    content, flags=re.DOTALL
)

content = content.replace("piotroski_f = self._compute_piotroski(income_stmt, balance_sheet, cashflow)", "piotroski_f, piotroski_signals = self._compute_piotroski(income_stmt, balance_sheet, cashflow)")
content = content.replace("piotroski_f=piotroski_f,\n            altman_z=altman_z,", "piotroski_f=piotroski_f,\n            piotroski_signals=piotroski_signals,\n            altman_z=altman_z,")

with open("telmus/core/engines/health.py", "w", encoding="utf-8") as f:
    f.write(content)

# 3. Update tests
for root, _, files in os.walk("tests"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r"health=HealthResult\(\n\s*piotroski_f=7", "health=HealthResult(\n            piotroski_f=7, piotroski_signals={'ROA Positive': True, 'CFO Positive': True, 'ROA Improving': True, 'Low Accruals': True, 'Leverage Falling': True, 'Liquidity Rising': True, 'No Dilution': True, 'Gross Margin Rising': False, 'Asset Turnover Rising': False}", content)
            content = re.sub(r"health=HealthResult\(\n\s*None, None, None, None, None, None\)", "health=HealthResult(None, {}, None, None, None, None, None)", content)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# 4. Update html_dashboard.py
with open("telmus/exporters/html_dashboard.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix Chart.js CDN
content = re.sub(r"<script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>", "<script src=\"https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js\"></script>", content)

# Wrap script in DOMContentLoaded
content = content.replace("<script>\n        // ─── Chart.js global defaults ───", "<script>\n        document.addEventListener('DOMContentLoaded', function() {\n        // ─── Chart.js global defaults ───")
content = content.replace("        // ─── Initialize Tooltips ───\n        const tooltips = document.querySelectorAll('.tooltip-trigger');\n        tooltips.forEach(t => {\n            t.addEventListener('mouseenter', e => {\n                // basic tooltip logic can go here if needed\n            });\n        });\n    </script>", "        // ─── Initialize Tooltips ───\n        const tooltips = document.querySelectorAll('.tooltip-trigger');\n        tooltips.forEach(t => {\n            t.addEventListener('mouseenter', e => {\n                // basic tooltip logic can go here if needed\n            });\n        });\n        });\n    </script>")
content = content.replace("    </script>", "        });\n    </script>")
# Clean up duplicate wrapper endings if any
content = content.replace("        });\n        });\n    </script>", "        });\n    </script>")

# Add heights to canvas
content = content.replace("<canvas id=\"gaugeAltman\"></canvas>", "<canvas id=\"gaugeAltman\" style=\"height:200px;\"></canvas>")
content = content.replace("<canvas id=\"gaugeFCF\"></canvas>", "<canvas id=\"gaugeFCF\" style=\"height:200px;\"></canvas>")
content = content.replace("<canvas id=\"chartValuation\"></canvas>", "<canvas id=\"chartValuation\" style=\"height:220px;\"></canvas>")
content = content.replace("<canvas id=\"chartGrowth\"></canvas>", "<canvas id=\"chartGrowth\" style=\"height:220px;\"></canvas>")
content = content.replace("<canvas id=\"chartValuationA\"></canvas>", "<canvas id=\"chartValuationA\" style=\"height:220px;\"></canvas>")
content = content.replace("<canvas id=\"chartValuationB\"></canvas>", "<canvas id=\"chartValuationB\" style=\"height:220px;\"></canvas>")

# Replace Piotroski loading logic
pio_repl = """
        signals_desc = {
            "ROA Positive": "Company is profitable",
            "CFO Positive": "Operations generate cash",
            "ROA Improving": "Profitability improving",
            "Low Accruals": "Earnings quality is high",
            "Leverage Falling": "Debt burden reducing",
            "Liquidity Rising": "Short-term health improving",
            "No Dilution": "No new shares issued",
            "Gross Margin Rising": "Pricing power improving",
            "Asset Turnover Rising": "Using assets efficiently",
        }

        # Build checklist HTML
        checklist_items = []
        piotroski_signals = getattr(result.health, "piotroski_signals", {})
        if not piotroski_signals:
            piotroski_signals = {k: False for k in signals_desc}
            
        for name, desc in signals_desc.items():
            passed = piotroski_signals.get(name, False)
            css = "check-pass" if passed else "check-fail"
            icon_color = "var(--teal)" if passed else "var(--coral)"
            icon = "✔" if passed else "✘"
            checklist_items.append(f\"\"\"
                <div class="check-item {css}">
                    <span class="check-icon" style="color:{icon_color}">{icon}</span>
                    <div>
                        <div class="check-name">{name}</div>
                        <div class="check-desc">{desc}</div>
                    </div>
                </div>\"\"\")

        # Radar chart data (1 for pass, 0 for fail)
        signal_names = list(signals_desc.keys())
        signal_values = [1 if piotroski_signals.get(s, False) else 0 for s in signal_names]
"""

content = re.sub(
    r"signals = \{.*?checklist_items\.append.*?</div>\"\"\"\)",
    pio_repl,
    content,
    flags=re.DOTALL
)

with open("telmus/exporters/html_dashboard.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Modifications applied successfully.")
