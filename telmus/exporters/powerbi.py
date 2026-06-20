from __future__ import annotations
import typing
from telmus.core.result import ScanResult

import csv
import datetime
from telmus.core.scanner import TelmusScanner


class PowerBIExporter:
    def export_portfolio(self, tickers: list[str], path: str) -> None:
        scanner = TelmusScanner()
        today = datetime.date.today().isoformat()

        headers = [
            "Date",
            "Ticker",
            "Company",
            "Exchange",
            "PE_Ratio",
            "PB_Ratio",
            "EV_EBITDA",
            "Sector_Comparison",
            "Piotroski_F",
            "Altman_Z",
            "Debt_Equity",
            "Current_Ratio",
            "Interest_Coverage",
            "Revenue_CAGR_3Y",
            "PAT_CAGR_3Y",
            "Margin_Trend",
            "FCF_Yield",
            "Beneish_M",
            "Red_Flag_Count",
            "Highest_Concern",
            "Analyst_Brief",
        ]

        scanned_results = []
        for ticker in tickers:
            res = scanner.scan(ticker)
            scanned_results.append(res)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for res in scanned_results:
                writer.writerow([
                    today,
                    res.ticker,
                    res.company,
                    res.exchange,
                    self._csv_val(res.valuation.pe_ratio),
                    self._csv_val(res.valuation.pb_ratio),
                    self._csv_val(res.valuation.ev_ebitda),
                    self._csv_val(res.valuation.vs_sector),
                    self._csv_val(res.health.piotroski_f),
                    self._csv_val(res.health.altman_z),
                    self._csv_val(res.health.debt_to_equity),
                    self._csv_val(res.health.current_ratio),
                    self._csv_val(res.health.interest_coverage),
                    self._csv_val(res.growth.revenue_cagr_3y),
                    self._csv_val(res.growth.pat_cagr_3y),
                    self._csv_val(res.growth.margin_trend),
                    self._csv_val(res.growth.fcf_yield),
                    self._csv_val(res.beneish_m),
                    len(res.red_flags),
                    res.highest_concern,
                    res.analyst_brief,
                ])

        # Now generate HTML report
        if path.lower().endswith(".csv"):
            html_path = path[:-4] + "_report.html"
        else:
            html_path = path + "_report.html"

        self._generate_html_report(scanned_results, html_path)

    def export_flags(self, tickers: list[str], path: str) -> None:
        scanner = TelmusScanner()
        today = datetime.date.today().isoformat()

        headers = ["Date", "Ticker", "Flag_Type", "Flag_Value", "Flag_Severity"]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for ticker in tickers:
                res = scanner.scan(ticker)
                if not res.red_flags:
                    writer.writerow([today, res.ticker, "none", "", ""])
                else:
                    for flag in res.red_flags:
                        writer.writerow([
                            today,
                            res.ticker,
                            flag.type,
                            self._csv_val(flag.value),
                            flag.severity,
                        ])

    def _csv_val(self, val: typing.Any) -> any:
        if val is None:
            return ""
        return val

    def _generate_table_html(self, rows: list[dict[str, any]]) -> str:
        html = []
        for r in rows:
            badge_class = f"badge badge-{r['highest_concern']}"
            html.append(f"""
                <tr>
                    <td style="font-weight: 600;">{r['ticker']}</td>
                    <td>{r['company']}</td>
                    <td>{r['pe']}</td>
                    <td>{r['pb']}</td>
                    <td>{r['piotroski']}</td>
                    <td>{r['altman']}</td>
                    <td><span class="{badge_class}">{r['highest_concern']}</span></td>
                    <td class="brief-cell" title="{r['brief']}">{r['brief']}</td>
                </tr>
            """)
        return "\n".join(html)

    def _generate_html_report(self, results: list[ScanResult], html_path: str) -> None:
        import json
        
        # Extract data for simple charts
        tickers = [r.ticker for r in results]
        piotroski_f = [r.health.piotroski_f if r.health.piotroski_f is not None else 0 for r in results]
        pe_ratios = [r.valuation.pe_ratio if r.valuation.pe_ratio is not None else 0 for r in results]
        altman_z = [r.health.altman_z if r.health.altman_z is not None else 0 for r in results]
        
        # Normalize scores for Radar chart
        radar_datasets = []
        vibrant_colors = [
            {"border": "rgba(99, 102, 241, 1)", "bg": "rgba(99, 102, 241, 0.2)"},    # Indigo
            {"border": "rgba(236, 72, 153, 1)", "bg": "rgba(236, 72, 153, 0.2)"},    # Pink
            {"border": "rgba(16, 185, 129, 1)", "bg": "rgba(16, 185, 129, 0.2)"},    # Emerald
            {"border": "rgba(245, 158, 11, 1)", "bg": "rgba(245, 158, 11, 0.2)"},    # Amber
            {"border": "rgba(6, 182, 212, 1)", "bg": "rgba(6, 182, 212, 0.2)"},      # Cyan
            {"border": "rgba(139, 92, 246, 1)", "bg": "rgba(139, 92, 246, 0.2)"},    # Purple
        ]
        
        for idx, res in enumerate(results):
            f_val = res.health.piotroski_f
            z_val = res.health.altman_z
            pe_val = res.valuation.pe_ratio
            rev_cagr = res.growth.revenue_cagr_3y
            de_val = res.health.debt_to_equity

            # Health (max 9)
            h_score = round((f_val / 9.0) * 10.0, 2) if f_val is not None else 0.0
            # Safety
            s_score = round(min(max(z_val, 0.0) / 3.0, 1.0) * 10.0, 2) if z_val is not None else 0.0
            # Valuation
            if pe_val is not None and pe_val > 0:
                v_score = round(max(0.0, min(10.0, (40.0 - pe_val) / 3.0)), 2)
            else:
                v_score = 0.0
            # Growth
            g_score = round(max(0.0, min(10.0, (rev_cagr or 0.0) * 50.0)), 2)
            # Leverage
            if de_val is not None:
                l_score = round(max(0.0, min(10.0, 10.0 - (de_val * 5.0))), 2)
            else:
                l_score = 10.0

            color_pair = vibrant_colors[idx % len(vibrant_colors)]
            radar_datasets.append({
                "label": res.ticker,
                "data": [h_score, s_score, v_score, g_score, l_score],
                "borderColor": color_pair["border"],
                "backgroundColor": color_pair["bg"],
                "borderWidth": 2,
                "pointBackgroundColor": color_pair["border"]
            })

        table_rows = []
        for r in results:
            pe_str = f"{r.valuation.pe_ratio:.2f}" if r.valuation.pe_ratio is not None else "n/a"
            pb_str = f"{r.valuation.pb_ratio:.2f}" if r.valuation.pb_ratio is not None else "n/a"
            alt_str = f"{r.health.altman_z:.2f}" if r.health.altman_z is not None else "n/a"
            table_rows.append({
                "ticker": r.ticker,
                "company": r.company,
                "pe": pe_str,
                "pb": pb_str,
                "piotroski": r.health.piotroski_f if r.health.piotroski_f is not None else "n/a",
                "altman": alt_str,
                "highest_concern": r.highest_concern.lower() if r.highest_concern else "low",
                "brief": r.analyst_brief or ""
            })

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus - Portfolio Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #09090b;
            --card-bg: #18181b;
            --border-color: #27272a;
            --text-main: #f4f4f5;
            --text-muted: #a1a1aa;
            --primary: #6366f1;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            padding: 2rem;
            min-height: 100vh;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        .logo {{
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.05em;
        }}
        .gradient-text {{
            background: linear-gradient(135deg, #a78bfa 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .date {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        .grid-top {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .grid-bottom {{
            display: grid;
            grid-template-columns: 1fr 1.5fr;
            gap: 1.5rem;
        }}
        @media (max-width: 1024px) {{
            .grid-bottom {{
                grid-template-columns: 1fr;
            }}
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        .card-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-main);
        }}
        .chart-container {{
            position: relative;
            height: 250px;
            width: 100%;
        }}
        .chart-container-large {{
            position: relative;
            height: 380px;
            width: 100%;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        tr:hover td {{
            background-color: rgba(255, 255, 255, 0.02);
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-low {{
            background-color: rgba(16, 185, 129, 0.15);
            color: var(--success);
        }}
        .badge-medium {{
            background-color: rgba(245, 158, 11, 0.15);
            color: var(--warning);
        }}
        .badge-high {{
            background-color: rgba(239, 68, 68, 0.15);
            color: var(--danger);
        }}
        .brief-cell {{
            font-size: 0.8rem;
            color: var(--text-muted);
            max-width: 250px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <span class="gradient-text">telmus</span> Portfolio Analysis
        </div>
        <div class="date">Report Date: {datetime.date.today().strftime('%B %d, %Y')}</div>
    </header>

    <div class="grid-top">
        <div class="card">
            <div class="card-title">Piotroski F-Score Comparison</div>
            <div class="chart-container">
                <canvas id="piotroskiChart"></canvas>
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

    <div class="grid-bottom">
        <div class="card">
            <div class="card-title">Multi-Metric Score Radar</div>
            <div class="chart-container-large">
                <canvas id="radarChart"></canvas>
            </div>
        </div>
        <div class="card" style="overflow-x: auto;">
            <div class="card-title">Portfolio Metrics Table</div>
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Company</th>
                        <th>P/E</th>
                        <th>P/B</th>
                        <th>Piotroski F</th>
                        <th>Altman Z</th>
                        <th>Concern</th>
                        <th>Brief</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_table_html(table_rows)}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const tickers = {json.dumps(tickers)};
        const pioScores = {json.dumps(piotroski_f)};
        const peRatios = {json.dumps(pe_ratios)};
        const altmanScores = {json.dumps(altman_z)};
        const radarDatasets = {json.dumps(radar_datasets)};

        // Color mapper for Piotroski F-scores
        const getPioColor = (val) => {{
            if (val >= 7) return '#10b981'; // green
            if (val >= 5) return '#f59e0b'; // orange
            return '#ef4444'; // red
        }};
        const pioColors = pioScores.map(getPioColor);

        // Chart 1: Piotroski F
        new Chart(document.getElementById('piotroskiChart'), {{
            type: 'bar',
            data: {{
                labels: tickers,
                datasets: [{{
                    label: 'Piotroski F-Score',
                    data: pioScores,
                    backgroundColor: pioColors,
                    borderRadius: 4,
                    borderWidth: 0,
                    barThickness: 15
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                }},
                scales: {{
                    x: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ color: '#a1a1aa' }},
                        max: 9
                    }},
                    y: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#a1a1aa' }}
                    }}
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
                    data: peRatios,
                    backgroundColor: '#6366f1',
                    borderRadius: 4,
                    borderWidth: 0,
                    barThickness: 15
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                }},
                scales: {{
                    x: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ color: '#a1a1aa' }}
                    }},
                    y: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#a1a1aa' }}
                    }}
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
                    data: altmanScores,
                    backgroundColor: '#06b6d4',
                    borderRadius: 4,
                    borderWidth: 0,
                    barThickness: 15
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                }},
                scales: {{
                    x: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ color: '#a1a1aa' }}
                    }},
                    y: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#a1a1aa' }}
                    }}
                }}
            }},
            plugins: [{{
                id: 'altmanLine',
                afterDraw(chart) {{
                    const {{ctx, chartArea: {{top, bottom, left, right}}, scales: {{x}}}} = chart;
                    const xPos = x.getPixelForValue(2.99);
                    if (xPos >= left && xPos <= right) {{
                        ctx.save();
                        ctx.strokeStyle = '#ef4444';
                        ctx.lineWidth = 1.5;
                        ctx.setLineDash([5, 5]);
                        ctx.beginPath();
                        ctx.moveTo(xPos, top);
                        ctx.lineTo(xPos, bottom);
                        ctx.stroke();
                        
                        // Add text label
                        ctx.fillStyle = '#ef4444';
                        ctx.font = '10px Inter';
                        ctx.fillText('Safe (2.99)', xPos + 5, top + 15);
                        ctx.restore();
                    }}
                }}
            }}]
        }});

        // Chart 4: Radar
        new Chart(document.getElementById('radarChart'), {{
            type: 'radar',
            data: {{
                labels: ['Financial Health', 'Credit Safety', 'Valuation Cheapness', 'Growth Rate', 'Debt Safety'],
                datasets: radarDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{ color: '#f4f4f5', font: {{ family: 'Inter' }} }}
                    }}
                }},
                scales: {{
                    r: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.08)' }},
                        angleLines: {{ color: 'rgba(255, 255, 255, 0.08)' }},
                        pointLabels: {{ color: '#a1a1aa', font: {{ family: 'Inter', size: 10 }} }},
                        ticks: {{
                            backdropColor: 'transparent',
                            color: '#a1a1aa',
                            showLabelBackdrop: false,
                            max: 10,
                            min: 0,
                            stepSize: 2
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
