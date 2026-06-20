from __future__ import annotations

import json
import datetime
from telmus.core.result import ScanResult, CompareResult


class HtmlDashboardExporter:
    def _fmt(self, val: any) -> str:
        if val is None:
            return "n/a"
        if isinstance(val, (int, float)):
            return f"{val:.2f}"
        return str(val)

    def _get_winner_details(
        self, metric_name: str, val_a: any, val_b: any, ticker_a: str, ticker_b: str
    ) -> tuple[str | None, str]:
        if val_a is None and val_b is None:
            return None, "Draw"
        if val_a is None:
            return "B", ticker_b
        if val_b is None:
            return "A", ticker_a

        try:
            a = float(val_a)
            b = float(val_b)
        except (TypeError, ValueError):
            return None, "Draw"

        lower_better = ["P/E Ratio", "P/B Ratio", "EV/EBITDA", "Debt / Equity", "Debt/Equity"]
        is_lower_better = any(lb.lower() in metric_name.lower() for lb in lower_better)

        if a == b:
            return None, "Tie"

        if is_lower_better:
            if "ratio" in metric_name.lower() or "ebitda" in metric_name.lower():
                if a < 0 and b >= 0:
                    return "B", ticker_b
                if b < 0 and a >= 0:
                    return "A", ticker_a
            return ("A", ticker_a) if a < b else ("B", ticker_b)
        else:
            return ("A", ticker_a) if a > b else ("B", ticker_b)

    def export_scan(self, result: ScanResult, path: str) -> None:
        val_labels = ['P/E Ratio', 'P/B Ratio', 'EV/EBITDA']
        val_data = [
            result.valuation.pe_ratio if result.valuation.pe_ratio is not None else 0.0,
            result.valuation.pb_ratio if result.valuation.pb_ratio is not None else 0.0,
            result.valuation.ev_ebitda if result.valuation.ev_ebitda is not None else 0.0
        ]
        
        pio_score = result.health.piotroski_f if result.health.piotroski_f is not None else 0
        
        growth_labels = ['Revenue CAGR 3Y (%)', 'PAT CAGR 3Y (%)', 'FCF Yield (%)']
        growth_data = [
            (result.growth.revenue_cagr_3y or 0.0) * 100.0,
            (result.growth.pat_cagr_3y or 0.0) * 100.0,
            (result.growth.fcf_yield or 0.0) * 100.0
        ]

        if pio_score >= 7:
            pio_color = '#14b8a6'
        elif pio_score >= 5:
            pio_color = '#f59e0b'
        else:
            pio_color = '#ef4444'

        flags_html = ""
        if not result.red_flags:
            flags_html = """
            <div class="banner banner-success">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="banner-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>No red flags detected. The company passes all safety checks.</span>
            </div>
            """
        else:
            rows = []
            for flag in result.red_flags:
                sev_lower = flag.severity.lower()
                badge_class = f"badge badge-{sev_lower}"
                rows.append(f"""
                <tr>
                    <td><strong>{flag.type}</strong></td>
                    <td>{self._fmt(flag.value)}</td>
                    <td><span class="{badge_class}">{flag.severity}</span></td>
                </tr>
                """)
            flags_html = f"""
            <div class="card" style="margin-top: 1.5rem;">
                <div class="card-title">Red Flags ({len(result.red_flags)})</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Flag Type</th>
                                <th>Value</th>
                                <th>Severity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus - {result.company} ({result.ticker}) Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0d0d0d;
            --card-bg: #171717;
            --border-color: #262626;
            --text-main: #f4f4f5;
            --text-muted: #a1a1aa;
            --teal: #0d9488;
            --teal-light: rgba(13, 148, 136, 0.15);
            --success: #14b8a6;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; width: 100%; flex: 1; }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        .logo {{ font-size: 1.8rem; font-weight: 700; color: var(--text-main); }}
        .logo-teal {{ color: var(--teal); }}
        .exchange {{ font-size: 0.9rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
        .card-header {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .company-title {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .ticker-badge {{
            background-color: var(--teal-light);
            color: var(--teal);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .brief-title {{ font-size: 0.95rem; font-weight: 600; color: var(--teal); margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        .brief-text {{ color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .card-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 1.2rem; border-left: 3px solid var(--teal); padding-left: 0.6rem; }}
        .chart-container {{ position: relative; height: 260px; width: 100%; }}
        .banner {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1.25rem 1.5rem;
            border-radius: 12px;
            border: 1px solid transparent;
            font-size: 0.95rem;
            font-weight: 500;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .banner-success {{
            background-color: rgba(20, 184, 166, 0.1);
            border-color: rgba(20, 184, 166, 0.2);
            color: var(--success);
        }}
        .banner-icon {{ width: 1.5rem; height: 1.5rem; flex-shrink: 0; }}
        .table-container {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }}
        th, td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-color); }}
        th {{ font-weight: 600; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-low {{ background-color: rgba(20, 184, 166, 0.15); color: var(--success); }}
        .badge-medium {{ background-color: rgba(245, 158, 11, 0.15); color: var(--warning); }}
        .badge-high {{ background-color: rgba(239, 68, 68, 0.15); color: var(--danger); }}
        footer {{
            text-align: center;
            padding-top: 2rem;
            margin-top: auto;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        footer a {{ color: var(--teal); text-decoration: none; font-weight: 500; }}
        footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div class="logo">
                    <span class="logo-teal">telmus</span> dashboard
                </div>
                <div class="exchange">Exchange: {result.exchange}</div>
            </div>
            <div class="card-header">
                <div class="company-title">
                    {result.company} <span class="ticker-badge">{result.ticker}</span>
                </div>
                <div style="margin-top: 1rem;">
                    <div class="brief-title">Analyst Brief</div>
                    <div class="brief-text">{result.analyst_brief}</div>
                </div>
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-title">Valuation Metrics</div>
                <div class="chart-container">
                    <canvas id="valChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Piotroski F-Score (out of 9)</div>
                <div class="chart-container">
                    <canvas id="pioChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Growth & Yield Metrics (%)</div>
                <div class="chart-container">
                    <canvas id="growthChart"></canvas>
                </div>
            </div>
        </div>

        {flags_html}

        <footer>
            Generated by <a href="https://pypi.org/project/telmus" target="_blank">telmus</a> — pypi.org/project/telmus
        </footer>
    </div>

    <script>
        // Chart 1: Valuation
        new Chart(document.getElementById('valChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(val_labels)},
                datasets: [{{
                    data: {json.dumps(val_data)},
                    backgroundColor: '#0d9488',
                    borderRadius: 6,
                    borderWidth: 0,
                    barThickness: 35
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }} }}
                }}
            }}
        }});

        // Chart 2: Piotroski F
        new Chart(document.getElementById('pioChart'), {{
            type: 'bar',
            data: {{
                labels: ['Piotroski F-Score'],
                datasets: [{{
                    data: [{pio_score}],
                    backgroundColor: '{pio_color}',
                    borderRadius: 6,
                    borderWidth: 0,
                    barThickness: 45
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }}, min: 0, max: 9, stepSize: 1 }}
                }}
            }}
        }});

        // Chart 3: Growth
        new Chart(document.getElementById('growthChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(growth_labels)},
                datasets: [{{
                    data: {json.dumps(growth_data)},
                    backgroundColor: '#6366f1',
                    borderRadius: 6,
                    borderWidth: 0,
                    barThickness: 35
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def export_compare(self, result: CompareResult, path: str) -> None:
        ticker_a = result.ticker_a
        ticker_b = result.ticker_b

        val_labels = ['P/E Ratio', 'P/B Ratio', 'EV/EBITDA']
        val_a = [
            result.result_a.valuation.pe_ratio if result.result_a.valuation.pe_ratio is not None else 0.0,
            result.result_a.valuation.pb_ratio if result.result_a.valuation.pb_ratio is not None else 0.0,
            result.result_a.valuation.ev_ebitda if result.result_a.valuation.ev_ebitda is not None else 0.0
        ]
        val_b = [
            result.result_b.valuation.pe_ratio if result.result_b.valuation.pe_ratio is not None else 0.0,
            result.result_b.valuation.pb_ratio if result.result_b.valuation.pb_ratio is not None else 0.0,
            result.result_b.valuation.ev_ebitda if result.result_b.valuation.ev_ebitda is not None else 0.0
        ]

        health_labels = ['Piotroski F', 'Altman Z', 'Debt/Equity', 'Current Ratio', 'Interest Coverage']
        health_a = [
            result.result_a.health.piotroski_f if result.result_a.health.piotroski_f is not None else 0.0,
            result.result_a.health.altman_z if result.result_a.health.altman_z is not None else 0.0,
            result.result_a.health.debt_to_equity if result.result_a.health.debt_to_equity is not None else 0.0,
            result.result_a.health.current_ratio if result.result_a.health.current_ratio is not None else 0.0,
            result.result_a.health.interest_coverage if result.result_a.health.interest_coverage is not None else 0.0
        ]
        health_b = [
            result.result_b.health.piotroski_f if result.result_b.health.piotroski_f is not None else 0.0,
            result.result_b.health.altman_z if result.result_b.health.altman_z is not None else 0.0,
            result.result_b.health.debt_to_equity if result.result_b.health.debt_to_equity is not None else 0.0,
            result.result_b.health.current_ratio if result.result_b.health.current_ratio is not None else 0.0,
            result.result_b.health.interest_coverage if result.result_b.health.interest_coverage is not None else 0.0
        ]

        growth_labels = ['Revenue CAGR (%)', 'PAT CAGR (%)', 'FCF Yield (%)']
        growth_a = [
            (result.result_a.growth.revenue_cagr_3y or 0.0) * 100.0,
            (result.result_a.growth.pat_cagr_3y or 0.0) * 100.0,
            (result.result_a.growth.fcf_yield or 0.0) * 100.0
        ]
        growth_b = [
            (result.result_b.growth.revenue_cagr_3y or 0.0) * 100.0,
            (result.result_b.growth.pat_cagr_3y or 0.0) * 100.0,
            (result.result_b.growth.fcf_yield or 0.0) * 100.0
        ]

        metrics = [
            ("P/E Ratio", result.result_a.valuation.pe_ratio, result.result_b.valuation.pe_ratio),
            ("P/B Ratio", result.result_a.valuation.pb_ratio, result.result_b.valuation.pb_ratio),
            ("EV/EBITDA", result.result_a.valuation.ev_ebitda, result.result_b.valuation.ev_ebitda),
            ("Piotroski F-Score", result.result_a.health.piotroski_f, result.result_b.health.piotroski_f),
            ("Altman Z-Score", result.result_a.health.altman_z, result.result_b.health.altman_z),
            ("Debt/Equity", result.result_a.health.debt_to_equity, result.result_b.health.debt_to_equity),
            ("Current Ratio", result.result_a.health.current_ratio, result.result_b.health.current_ratio),
            ("Interest Coverage", result.result_a.health.interest_coverage, result.result_b.health.interest_coverage),
            ("Revenue CAGR 3Y", result.result_a.growth.revenue_cagr_3y, result.result_b.growth.revenue_cagr_3y),
            ("PAT CAGR 3Y", result.result_a.growth.pat_cagr_3y, result.result_b.growth.pat_cagr_3y),
            ("FCF Yield", result.result_a.growth.fcf_yield, result.result_b.growth.fcf_yield),
        ]
        
        table_rows = []
        for name, val_a, val_b in metrics:
            win_code, win_text = self._get_winner_details(name, val_a, val_b, ticker_a, ticker_b)
            val_a_str = self._fmt(val_a)
            val_b_str = self._fmt(val_b)
            
            style_a = "class='winner'" if win_code == "A" else ""
            style_b = "class='winner'" if win_code == "B" else ""
            
            win_class = "winner-badge badge-winner" if win_code in ("A", "B") else "winner-badge badge-draw"
            
            table_rows.append(f"""
            <tr>
                <td><strong>{name}</strong></td>
                <td {style_a}>{val_a_str}</td>
                <td {style_b}>{val_b_str}</td>
                <td><span class="{win_class}">{win_text}</span></td>
            </tr>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus Comparison - {ticker_a} vs {ticker_b}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0d0d0d;
            --card-bg: #171717;
            --border-color: #262626;
            --text-main: #f4f4f5;
            --text-muted: #a1a1aa;
            --teal: #0d9488;
            --teal-light: rgba(13, 148, 136, 0.15);
            --orange: #ea580c;
            --orange-light: rgba(234, 88, 12, 0.15);
            --success: #14b8a6;
            --warning: #f59e0b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; width: 100%; flex: 1; }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{ font-size: 1.8rem; font-weight: 700; color: var(--text-main); }}
        .logo-teal {{ color: var(--teal); }}
        .compare-title {{
            font-size: 1.4rem;
            font-weight: 700;
        }}
        .badge-a {{
            background-color: var(--teal-light);
            color: var(--teal);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
        }}
        .badge-b {{
            background-color: var(--orange-light);
            color: var(--orange);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .card-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 1.2rem; border-left: 3px solid var(--teal); padding-left: 0.6rem; }}
        .chart-container {{ position: relative; height: 260px; width: 100%; }}
        .table-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .table-container {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }}
        th, td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-color); }}
        th {{ font-weight: 600; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}
        td.winner {{
            font-weight: 600;
            background-color: rgba(255, 255, 255, 0.02);
        }}
        .winner-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-winner {{
            background-color: rgba(20, 184, 166, 0.15);
            color: var(--success);
        }}
        .badge-draw {{
            background-color: rgba(255, 255, 255, 0.08);
            color: var(--text-muted);
        }}
        footer {{
            text-align: center;
            padding-top: 2rem;
            margin-top: auto;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        footer a {{ color: var(--teal); text-decoration: none; font-weight: 500; }}
        footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <span class="logo-teal">telmus</span> compare
            </div>
            <div class="compare-title">
                <span class="badge-a">{ticker_a}</span> vs <span class="badge-b">{ticker_b}</span>
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-title">Valuation Comparison</div>
                <div class="chart-container">
                    <canvas id="valChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Health Comparison</div>
                <div class="chart-container">
                    <canvas id="healthChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Growth & Yield Comparison (%)</div>
                <div class="chart-container">
                    <canvas id="growthChart"></canvas>
                </div>
            </div>
        </div>

        <div class="table-card">
            <div class="card-title">Detailed Comparison Table</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>{ticker_a}</th>
                            <th>{ticker_b}</th>
                            <th>Winner</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(table_rows)}
                    </tbody>
                </table>
            </div>
        </div>

        <footer>
            Generated by <a href="https://pypi.org/project/telmus" target="_blank">telmus</a> — pypi.org/project/telmus
        </footer>
    </div>

    <script>
        // Chart 1: Valuation Comparison
        new Chart(document.getElementById('valChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(val_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(val_a)},
                        backgroundColor: '#0d9488',
                        borderRadius: 4,
                        barThickness: 20
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(val_b)},
                        backgroundColor: '#ea580c',
                        borderRadius: 4,
                        barThickness: 20
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#f4f4f5' }} }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }} }}
                }}
            }}
        }});

        // Chart 2: Health Comparison
        new Chart(document.getElementById('healthChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(health_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(health_a)},
                        backgroundColor: '#0d9488',
                        borderRadius: 4,
                        barThickness: 15
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(health_b)},
                        backgroundColor: '#ea580c',
                        borderRadius: 4,
                        barThickness: 15
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#f4f4f5' }} }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }} }}
                }}
            }}
        }});

        // Chart 3: Growth Comparison
        new Chart(document.getElementById('growthChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(growth_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(growth_a)},
                        backgroundColor: '#0d9488',
                        borderRadius: 4,
                        barThickness: 20
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(growth_b)},
                        backgroundColor: '#ea580c',
                        borderRadius: 4,
                        barThickness: 20
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#f4f4f5' }} }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def export_screen(self, results: list[ScanResult], path: str) -> None:
        tickers = [r.ticker for r in results]
        pio_scores = [r.health.piotroski_f if r.health.piotroski_f is not None else 0 for r in results]
        pe_ratios = [r.valuation.pe_ratio if r.valuation.pe_ratio is not None else 0 for r in results]
        altman_scores = [r.health.altman_z if r.health.altman_z is not None else 0 for r in results]

        table_rows = []
        for r in results:
            pe_str = f"{r.valuation.pe_ratio:.2f}" if r.valuation.pe_ratio is not None else "n/a"
            pb_str = f"{r.valuation.pb_ratio:.2f}" if r.valuation.pb_ratio is not None else "n/a"
            alt_str = f"{r.health.altman_z:.2f}" if r.health.altman_z is not None else "n/a"
            de_str = f"{r.health.debt_to_equity:.2f}" if r.health.debt_to_equity is not None else "n/a"
            rev_str = f"{(r.growth.revenue_cagr_3y or 0.0)*100:.1f}%" if r.growth.revenue_cagr_3y is not None else "n/a"
            
            badge_class = f"badge badge-{r.highest_concern.lower()}"
            
            table_rows.append(f"""
            <tr>
                <td data-val="{r.ticker}"><strong>{r.ticker}</strong></td>
                <td data-val="{r.company}">{r.company}</td>
                <td data-val="{r.health.piotroski_f or -1}">{r.health.piotroski_f if r.health.piotroski_f is not None else 'n/a'}</td>
                <td data-val="{r.health.altman_z or -99}">{alt_str}</td>
                <td data-val="{r.valuation.pe_ratio or 9999}">{pe_str}</td>
                <td data-val="{r.valuation.pb_ratio or 9999}">{pb_str}</td>
                <td data-val="{r.health.debt_to_equity or 9999}">{de_str}</td>
                <td data-val="{r.growth.revenue_cagr_3y or -99}">{rev_str}</td>
                <td data-val="{r.highest_concern.lower()}"><span class="{badge_class}">{r.highest_concern}</span></td>
            </tr>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus - Sector Screening Results</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0d0d0d;
            --card-bg: #171717;
            --border-color: #262626;
            --text-main: #f4f4f5;
            --text-muted: #a1a1aa;
            --teal: #0d9488;
            --teal-light: rgba(13, 148, 136, 0.15);
            --success: #14b8a6;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; width: 100%; flex: 1; }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
        }}
        .logo {{ font-size: 1.8rem; font-weight: 700; color: var(--text-main); }}
        .logo-teal {{ color: var(--teal); }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .card-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 1.2rem; border-left: 3px solid var(--teal); padding-left: 0.6rem; }}
        .chart-container {{ position: relative; height: 260px; width: 100%; }}
        .table-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .table-container {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }}
        th, td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-color); }}
        th {{ font-weight: 600; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; cursor: pointer; }}
        th:hover {{ color: var(--teal); }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-low {{ background-color: rgba(20, 184, 166, 0.15); color: var(--success); }}
        .badge-medium {{ background-color: rgba(245, 158, 11, 0.15); color: var(--warning); }}
        .badge-high {{ background-color: rgba(239, 68, 68, 0.15); color: var(--danger); }}
        footer {{
            text-align: center;
            padding-top: 2rem;
            margin-top: auto;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        footer a {{ color: var(--teal); text-decoration: none; font-weight: 500; }}
        footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <span class="logo-teal">telmus</span> screening results
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-title">Piotroski F-Score Comparison</div>
                <div class="chart-container">
                    <canvas id="pioChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">P/E Ratio Comparison</div>
                <div class="chart-container">
                    <canvas id="peChart"></canvas>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Altman Z-Score Comparison</div>
                <div class="chart-container">
                    <canvas id="altmanChart"></canvas>
                </div>
            </div>
        </div>

        <div class="table-card">
            <div class="card-title">Screening Results Table (Click Headers to Sort)</div>
            <div class="table-container">
                <table id="screenTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">Ticker</th>
                            <th onclick="sortTable(1)">Company</th>
                            <th onclick="sortTable(2)">Piotroski F</th>
                            <th onclick="sortTable(3)">Altman Z</th>
                            <th onclick="sortTable(4)">P/E</th>
                            <th onclick="sortTable(5)">P/B</th>
                            <th onclick="sortTable(6)">D/E</th>
                            <th onclick="sortTable(7)">Revenue CAGR</th>
                            <th onclick="sortTable(8)">Highest Concern</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(table_rows)}
                    </tbody>
                </table>
            </div>
        </div>

        <footer>
            Generated by <a href="https://pypi.org/project/telmus" target="_blank">telmus</a> — pypi.org/project/telmus
        </footer>
    </div>

    <script>
        const tickers = {json.dumps(tickers)};

        // Chart 1: Piotroski F-Score
        new Chart(document.getElementById('pioChart'), {{
            type: 'bar',
            data: {{
                labels: tickers,
                datasets: [{{
                    label: 'Piotroski F-Score',
                    data: {json.dumps(pio_scores)},
                    backgroundColor: '#0d9488',
                    borderRadius: 4,
                    barThickness: 20
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }}, min: 0, max: 9 }}
                }}
            }}
        }});

        // Chart 2: P/E Ratio
        new Chart(document.getElementById('peChart'), {{
            type: 'bar',
            data: {{
                labels: tickers,
                datasets: [{{
                    label: 'P/E Ratio',
                    data: {json.dumps(pe_ratios)},
                    backgroundColor: '#6366f1',
                    borderRadius: 4,
                    barThickness: 20
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }} }}
                }}
            }}
        }});

        // Chart 3: Altman Z-Score
        new Chart(document.getElementById('altmanChart'), {{
            type: 'bar',
            data: {{
                labels: tickers,
                datasets: [{{
                    label: 'Altman Z-Score',
                    data: {json.dumps(altman_scores)},
                    backgroundColor: '#06b6d4',
                    borderRadius: 4,
                    barThickness: 20
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#262626' }}, ticks: {{ color: '#a1a1aa' }} }}
                }}
            }}
        }});

        // Sorting Logic
        let sortDirections = Array(9).fill(false);
        function sortTable(colIndex) {{
            const table = document.getElementById("screenTable");
            let rows, switching, i, x, y, shouldSwitch;
            const dirAsc = !sortDirections[colIndex];
            sortDirections = Array(9).fill(false);
            sortDirections[colIndex] = dirAsc;
            
            switching = true;
            while (switching) {{
                switching = false;
                rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[colIndex];
                    y = rows[i+1].getElementsByTagName("TD")[colIndex];
                    
                    let xVal = x.getAttribute("data-val") || x.innerText.toLowerCase().trim();
                    let yVal = y.getAttribute("data-val") || y.innerText.toLowerCase().trim();
                    
                    let xNum = parseFloat(xVal);
                    let yNum = parseFloat(yVal);
                    if (!isNaN(xNum) && !isNaN(yNum)) {{
                        xVal = xNum;
                        yVal = yNum;
                    }}
                    
                    if (dirAsc) {{
                        if (xVal > yVal) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }} else {{
                        if (xVal < yVal) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }}
                }}
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                }}
            }}
        }}
    </script>
</body>
</html>
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
