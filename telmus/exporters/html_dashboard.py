from __future__ import annotations

import json
import datetime
from telmus.core.result import ScanResult, CompareResult


class HtmlDashboardExporter:
    def _fmt(self, val: any) -> str:
        if val is None:
            return "n/a"
        if isinstance(val, (int, float)):
            return f"{val:,.2f}"
        return str(val)

    def _fmt_pct(self, val: any) -> str:
        if val is None:
            return "n/a"
        if isinstance(val, (int, float)):
            return f"{val * 100:,.2f}%"
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
        scan_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pe = result.valuation.pe_ratio
        pio = result.health.piotroski_f
        altman = result.health.altman_z
        concern = result.highest_concern or "LOW"

        # Card colors logic
        pe_text = self._fmt(pe)
        if pe is None:
            pe_color = "text-gray-400"
        elif pe < 20:
            pe_color = "text-emerald-400"
        elif pe <= 35:
            pe_color = "text-amber-400"
        else:
            pe_color = "text-rose-400"

        pio_text = f"{pio}/9" if pio is not None else "n/a"
        if pio is None:
            pio_color = "text-gray-400"
        elif pio >= 7:
            pio_color = "text-emerald-400"
        elif pio >= 5:
            pio_color = "text-amber-400"
        else:
            pio_color = "text-rose-400"

        altman_text = self._fmt(altman)
        if altman is None:
            altman_color = "text-gray-400"
        elif altman > 2.99:
            altman_color = "text-emerald-400"
        elif altman >= 1.81:
            altman_color = "text-amber-400"
        else:
            altman_color = "text-rose-400"

        concern_upper = concern.upper()
        if concern_upper == "HIGH":
            concern_badge = "bg-rose-500/10 text-rose-400 border border-rose-500/20"
        elif concern_upper == "MEDIUM":
            concern_badge = "bg-amber-500/10 text-amber-400 border border-amber-500/20"
        else:
            concern_badge = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"

        # Flags layout
        if not result.red_flags:
            flags_html = """
            <div class="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-6 py-4 rounded-xl flex items-center gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="font-medium text-lg">No Red Flags Detected</span>
            </div>
            """
        else:
            rows = []
            for flag in result.red_flags:
                sev = flag.severity.upper()
                if sev == "HIGH":
                    badge = "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                elif sev == "MEDIUM":
                    badge = "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                else:
                    badge = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                rows.append(f"""
                <tr class="border-b border-borderD/40 hover:bg-white/[0.01] transition-all">
                    <td class="px-6 py-4 text-sm font-semibold text-white">{flag.type}</td>
                    <td class="px-6 py-4 text-sm text-gray-300">{self._fmt(flag.value)}</td>
                    <td class="px-6 py-4 text-sm"><span class="px-2.5 py-1 rounded text-xs font-bold {badge}">{sev}</span></td>
                </tr>
                """)
            flags_html = f"""
            <div class="bg-cardBg border border-borderD rounded-2xl p-6 shadow-2xl">
                <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-6 bg-rose-500 rounded-full"></span>
                    Red Flags Checked ({len(result.red_flags)})
                </h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-borderD">
                                <th class="px-6 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Flag Type</th>
                                <th class="px-6 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Value</th>
                                <th class="px-6 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Severity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            """

        # Prep chart values
        pe_val = pe if pe is not None else 0.0
        pb_val = result.valuation.pb_ratio if result.valuation.pb_ratio is not None else 0.0
        ev_val = result.valuation.ev_ebitda if result.valuation.ev_ebitda is not None else 0.0
        rev_cagr_pct = (result.growth.revenue_cagr_3y or 0.0) * 100.0
        pat_cagr_pct = (result.growth.pat_cagr_3y or 0.0) * 100.0
        fcf_yield_pct = (result.growth.fcf_yield or 0.0) * 100.0

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="bg-darkBg">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus - {result.company} ({result.ticker}) Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        darkBg: '#0a0a0f',
                        cardBg: '#12121a',
                        borderD: '#1e1e2e',
                        tealAccent: '#00b4d8',
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
        }}
    </style>
</head>
<body class="bg-darkBg text-gray-100 min-h-screen flex flex-col p-6 lg:p-12">
    <div class="max-w-7xl mx-auto w-full flex-1 flex flex-col gap-8">
        
        <!-- Header -->
        <header class="flex justify-between items-center border-b border-borderD pb-6">
            <div>
                <h1 class="text-3xl font-extrabold text-white tracking-tight">
                    <span class="text-tealAccent">telmus</span> dashboard
                </h1>
                <p class="text-gray-400 text-sm mt-1">Exchange: {result.exchange} | Ticker: {result.ticker}</p>
            </div>
            <div class="text-right hidden sm:block">
                <span class="text-xs text-gray-500 uppercase tracking-widest block">Last Scanned</span>
                <span class="text-sm font-semibold text-gray-300">{scan_date}</span>
            </div>
        </header>

        <!-- TOP ROW - 4 KPI cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- P/E Card -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 hover:shadow-tealAccent/5 hover:-translate-y-1 transition-all duration-300">
                <div class="text-4xl font-extrabold {pe_color}">{pe_text}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">P/E Ratio</div>
            </div>
            <!-- Piotroski Card -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 hover:shadow-tealAccent/5 hover:-translate-y-1 transition-all duration-300">
                <div class="text-4xl font-extrabold {pio_color}">{pio_text}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Piotroski F-Score</div>
            </div>
            <!-- Altman Z Card -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 hover:shadow-tealAccent/5 hover:-translate-y-1 transition-all duration-300">
                <div class="text-4xl font-extrabold {altman_color}">{altman_text}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Altman Z-Score</div>
            </div>
            <!-- Concern Card -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 hover:shadow-tealAccent/5 hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between">
                <div>
                    <span class="px-3 py-1 rounded-full text-xs font-bold uppercase {concern_badge}">{concern}</span>
                </div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-4">Highest Concern Level</div>
            </div>
        </div>

        <!-- SECOND ROW - 3 gauge charts -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Piotroski Gauge -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col items-center">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Piotroski F-Score</h3>
                <div class="relative w-full max-w-[200px] aspect-[2/1] flex flex-col items-center">
                    <canvas id="gaugePio"></canvas>
                    <div class="absolute bottom-1 text-center">
                        <span class="text-2xl font-black text-white">{pio_text}</span>
                        <span class="text-[10px] block text-gray-500 uppercase mt-0.5">Fundamentals</span>
                    </div>
                </div>
            </div>
            <!-- Altman Z Gauge -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col items-center">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Altman Z-Score</h3>
                <div class="relative w-full max-w-[200px] aspect-[2/1] flex flex-col items-center">
                    <canvas id="gaugeAltman"></canvas>
                    <div class="absolute bottom-1 text-center">
                        <span class="text-2xl font-black text-white">{altman_text}</span>
                        <span class="text-[10px] block text-gray-500 uppercase mt-0.5">Credit Risk</span>
                    </div>
                </div>
            </div>
            <!-- Rev CAGR Gauge -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col items-center">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Revenue CAGR (3Y)</h3>
                <div class="relative w-full max-w-[200px] aspect-[2/1] flex flex-col items-center">
                    <canvas id="gaugeRev"></canvas>
                    <div class="absolute bottom-1 text-center">
                        <span class="text-2xl font-black text-white">{self._fmt_pct(result.growth.revenue_cagr_3y)}</span>
                        <span class="text-[10px] block text-gray-500 uppercase mt-0.5">Growth Rate</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- THIRD ROW - 2 bar charts side by side -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Valuation Chart -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6 flex items-center gap-2">
                    <span class="w-1.5 h-4 bg-tealAccent rounded-full"></span>
                    Valuation Benchmarks
                </h3>
                <div class="h-64 relative">
                    <canvas id="chartValuation"></canvas>
                </div>
            </div>
            <!-- Growth Chart -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6 flex items-center gap-2">
                    <span class="w-1.5 h-4 bg-indigo-500 rounded-full"></span>
                    Growth Metrics
                </h3>
                <div class="h-64 relative">
                    <canvas id="chartGrowth"></canvas>
                </div>
            </div>
        </div>

        <!-- FOURTH ROW - Analyst Brief -->
        <div class="bg-cardBg border-l-4 border-l-tealAccent border border-y-borderD border-r-borderD p-8 rounded-2xl shadow-2xl">
            <h2 class="text-xl font-bold text-white mb-2">{result.company}</h2>
            <p class="text-gray-300 leading-relaxed text-sm lg:text-base font-medium">{result.analyst_brief}</p>
        </div>

        <!-- FIFTH ROW - Red Flags Table -->
        {flags_html}

        <!-- Footer -->
        <footer class="border-t border-borderD pt-6 text-center text-xs text-gray-500 flex flex-col sm:flex-row justify-between items-center gap-4 mt-8">
            <div>
                Generated by <span class="font-bold text-gray-400">telmus v0.1.5</span> | <a href="https://pypi.org/project/telmus" class="text-tealAccent hover:underline" target="_blank">pypi.org/project/telmus</a>
            </div>
            <div>
                Data sourced via Yahoo Finance | {scan_date}
            </div>
        </footer>

    </div>

    <script>
        // Common Gauge options
        const gaugeOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            rotation: 270,
            circumference: 180,
            cutout: '80%',
            plugins: {{
                legend: {{ display: false }},
                tooltip: {{ enabled: false }}
            }}
        }};

        // Piotroski Gauge
        const pioScore = {pio if pio is not None else 0};
        new Chart(document.getElementById('gaugePio'), {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [pioScore, Math.max(0, 9 - pioScore)],
                    backgroundColor: [pioScore >= 7 ? '#10b981' : (pioScore >= 5 ? '#f59e0b' : '#ef4444'), '#1e1e2e'],
                    borderWidth: 0
                }}]
            }},
            options: gaugeOptions
        }});

        // Altman Z Gauge (Capped at 10)
        const altmanScore = {altman if altman is not None else 0.0};
        const cappedAltman = Math.min(10.0, Math.max(0.0, altmanScore));
        new Chart(document.getElementById('gaugeAltman'), {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [cappedAltman, 10.0 - cappedAltman],
                    backgroundColor: [altmanScore > 2.99 ? '#10b981' : (altmanScore >= 1.81 ? '#f59e0b' : '#ef4444'), '#1e1e2e'],
                    borderWidth: 0
                }}]
            }},
            options: gaugeOptions
        }});

        // Rev CAGR Gauge (Capped at 50% for display)
        const revCagr = {rev_cagr_pct};
        const cappedRev = Math.min(50.0, Math.max(0.0, revCagr));
        new Chart(document.getElementById('gaugeRev'), {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [cappedRev, 50.0 - cappedRev],
                    backgroundColor: [revCagr > 0 ? '#10b981' : '#ef4444', '#1e1e2e'],
                    borderWidth: 0
                }}]
            }},
            options: gaugeOptions
        }});

        // Valuation Chart (Bar Chart with conditional coloring and benchmark lines)
        const peVal = {pe_val};
        const pbVal = {pb_val};
        const evVal = {ev_val};
        
        new Chart(document.getElementById('chartValuation'), {{
            type: 'bar',
            data: {{
                labels: ['P/E Ratio', 'P/B Ratio', 'EV/EBITDA'],
                datasets: [{{
                    label: 'Valuation',
                    data: [peVal, pbVal, evVal],
                    backgroundColor: [
                        peVal < 20 ? '#10b981' : '#ef4444',
                        pbVal < 3 ? '#10b981' : '#ef4444',
                        evVal < 10 ? '#10b981' : '#ef4444'
                    ],
                    borderRadius: 6,
                    barThickness: 35
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#1e1e2e' }}, ticks: {{ color: '#a1a1aa' }} }}
                }}
            }}
        }});

        // Growth Chart
        const revCagrVal = {rev_cagr_pct};
        const patCagrVal = {pat_cagr_pct};
        const fcfYieldVal = {fcf_yield_pct};
        
        new Chart(document.getElementById('chartGrowth'), {{
            type: 'bar',
            data: {{
                labels: ['Revenue CAGR (3Y) %', 'PAT CAGR (3Y) %', 'FCF Yield %'],
                datasets: [{{
                    label: 'Growth %',
                    data: [revCagrVal, patCagrVal, fcfYieldVal],
                    backgroundColor: [
                        revCagrVal > 0 ? '#10b981' : '#ef4444',
                        patCagrVal > 0 ? '#10b981' : '#ef4444',
                        fcfYieldVal > 0 ? '#10b981' : '#ef4444'
                    ],
                    borderRadius: 6,
                    barThickness: 35
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                    y: {{ grid: {{ color: '#1e1e2e' }}, ticks: {{ color: '#a1a1aa' }} }}
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
        scan_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ticker_a = result.ticker_a
        ticker_b = result.ticker_b
        res_a = result.result_a
        res_b = result.result_b

        # Helper method for styling cards inside compare view
        def _get_val_styles(val: float | None) -> tuple[str, str]:
            if val is None:
                return "n/a", "text-gray-400"
            if val < 20:
                return f"{val:,.2f}", "text-emerald-400"
            if val <= 35:
                return f"{val:,.2f}", "text-amber-400"
            return f"{val:,.2f}", "text-rose-400"

        def _get_pio_styles(val: int | None) -> tuple[str, str]:
            if val is None:
                return "n/a", "text-gray-400"
            if val >= 7:
                return f"{val}/9", "text-emerald-400"
            if val >= 5:
                return f"{val}/9", "text-amber-400"
            return f"{val}/9", "text-rose-400"

        def _get_alt_styles(val: float | None) -> tuple[str, str]:
            if val is None:
                return "n/a", "text-gray-400"
            if val > 2.99:
                return f"{val:,.2f}", "text-emerald-400"
            if val >= 1.81:
                return f"{val:,.2f}", "text-amber-400"
            return f"{val:,.2f}", "text-rose-400"

        pe_a_text, pe_a_col = _get_val_styles(res_a.valuation.pe_ratio)
        pe_b_text, pe_b_col = _get_val_styles(res_b.valuation.pe_ratio)
        pio_a_text, pio_a_col = _get_pio_styles(res_a.health.piotroski_f)
        pio_b_text, pio_b_col = _get_pio_styles(res_b.health.piotroski_f)
        alt_a_text, alt_a_col = _get_alt_styles(res_a.health.altman_z)
        alt_b_text, alt_b_col = _get_alt_styles(res_b.health.altman_z)

        # Build metrics list for winner table
        metrics = [
            ("P/E Ratio", res_a.valuation.pe_ratio, res_b.valuation.pe_ratio, "ratio"),
            ("P/B Ratio", res_a.valuation.pb_ratio, res_b.valuation.pb_ratio, "ratio"),
            ("EV/EBITDA", res_a.valuation.ev_ebitda, res_b.valuation.ev_ebitda, "ratio"),
            ("Piotroski F-Score", res_a.health.piotroski_f, res_b.health.piotroski_f, "score"),
            ("Altman Z-Score", res_a.health.altman_z, res_b.health.altman_z, "score"),
            ("Debt/Equity", res_a.health.debt_to_equity, res_b.health.debt_to_equity, "ratio"),
            ("Current Ratio", res_a.health.current_ratio, res_b.health.current_ratio, "score"),
            ("Interest Coverage", res_a.health.interest_coverage, res_b.health.interest_coverage, "score"),
            ("Revenue CAGR (3Y)", res_a.growth.revenue_cagr_3y, res_b.growth.revenue_cagr_3y, "percent"),
            ("PAT CAGR (3Y)", res_a.growth.pat_cagr_3y, res_b.growth.pat_cagr_3y, "percent"),
            ("FCF Yield", res_a.growth.fcf_yield, res_b.growth.fcf_yield, "percent"),
        ]

        table_rows = []
        for name, val_a, val_b, fmt_type in metrics:
            win_code, win_text = self._get_winner_details(name, val_a, val_b, ticker_a, ticker_b)
            
            if fmt_type == "percent":
                str_a = self._fmt_pct(val_a)
                str_b = self._fmt_pct(val_b)
            else:
                str_a = self._fmt(val_a)
                str_b = self._fmt(val_b)

            style_a = "bg-emerald-500/10 text-emerald-400 font-bold" if win_code == "A" else "text-gray-300"
            style_b = "bg-emerald-500/10 text-emerald-400 font-bold" if win_code == "B" else "text-gray-300"
            
            if win_code in ("A", "B"):
                win_display = f"""<span class="flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3.5 h-3.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                    </svg>
                    👑 {win_text}
                </span>"""
            else:
                win_display = f"""<span class="px-2.5 py-1 rounded bg-gray-500/10 text-gray-400 text-xs font-bold border border-gray-500/20">Draw</span>"""

            table_rows.append(f"""
            <tr class="border-b border-borderD/40 hover:bg-white/[0.01] transition-all">
                <td class="px-6 py-4 text-sm font-semibold text-white">{name}</td>
                <td class="px-6 py-4 text-sm {style_a}">{str_a}</td>
                <td class="px-6 py-4 text-sm {style_b}">{str_b}</td>
                <td class="px-6 py-4 text-sm flex items-center">{win_display}</td>
            </tr>
            """)

        # Prep JSON data for Chart.js
        val_labels = ['P/E Ratio', 'P/B Ratio', 'EV/EBITDA']
        val_a = [res_a.valuation.pe_ratio or 0.0, res_a.valuation.pb_ratio or 0.0, res_a.valuation.ev_ebitda or 0.0]
        val_b = [res_b.valuation.pe_ratio or 0.0, res_b.valuation.pb_ratio or 0.0, res_b.valuation.ev_ebitda or 0.0]

        health_labels = ['Piotroski F', 'Altman Z', 'Debt/Equity', 'Current Ratio', 'Interest Coverage']
        health_a = [res_a.health.piotroski_f or 0.0, res_a.health.altman_z or 0.0, res_a.health.debt_to_equity or 0.0, res_a.health.current_ratio or 0.0, res_a.health.interest_coverage or 0.0]
        health_b = [res_b.health.piotroski_f or 0.0, res_b.health.altman_z or 0.0, res_b.health.debt_to_equity or 0.0, res_b.health.current_ratio or 0.0, res_b.health.interest_coverage or 0.0]

        growth_labels = ['Revenue CAGR %', 'PAT CAGR %', 'FCF Yield %']
        growth_a = [(res_a.growth.revenue_cagr_3y or 0.0) * 100.0, (res_a.growth.pat_cagr_3y or 0.0) * 100.0, (res_a.growth.fcf_yield or 0.0) * 100.0]
        growth_b = [(res_b.growth.revenue_cagr_3y or 0.0) * 100.0, (res_b.growth.pat_cagr_3y or 0.0) * 100.0, (res_b.growth.fcf_yield or 0.0) * 100.0]

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="bg-darkBg">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus Comparison - {ticker_a} vs {ticker_b}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        darkBg: '#0a0a0f',
                        cardBg: '#12121a',
                        borderD: '#1e1e2e',
                        tealAccent: '#00b4d8',
                        orangeAccent: '#ea580c'
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-darkBg text-gray-100 min-h-screen flex flex-col p-6 lg:p-12">
    <div class="max-w-7xl mx-auto w-full flex-1 flex flex-col gap-8">
        
        <!-- Header -->
        <header class="flex justify-between items-center border-b border-borderD pb-6">
            <div>
                <h1 class="text-3xl font-extrabold text-white tracking-tight">
                    <span class="text-tealAccent">telmus</span> comparison
                </h1>
                <p class="text-gray-400 text-sm mt-1">Side-by-Side Stock Analysis</p>
            </div>
            <div class="text-right hidden sm:block">
                <span class="text-xs text-gray-500 uppercase tracking-widest block">Scan Time</span>
                <span class="text-sm font-semibold text-gray-300">{scan_date}</span>
            </div>
        </header>

        <!-- TOP ROW - Side by Side Company KPIs -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Company A -->
            <div class="bg-cardBg border-t-4 border-t-tealAccent border-x border-b border-borderD p-6 rounded-2xl shadow-xl">
                <h2 class="text-xl font-bold text-white mb-4">{res_a.company} ({ticker_a})</h2>
                <div class="grid grid-cols-3 gap-4">
                    <div class="bg-black/30 p-4 rounded-xl border border-borderD/40">
                        <span class="text-2xl font-black {pe_a_col} block">{pe_a_text}</span>
                        <span class="text-[10px] font-bold text-gray-500 uppercase tracking-wider">P/E Ratio</span>
                    </div>
                    <div class="bg-black/30 p-4 rounded-xl border border-borderD/40">
                        <span class="text-2xl font-black {pio_a_col} block">{pio_a_text}</span>
                        <span class="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Piotroski F</span>
                    </div>
                    <div class="bg-black/30 p-4 rounded-xl border border-borderD/40">
                        <span class="text-2xl font-black {alt_a_col} block">{alt_a_text}</span>
                        <span class="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Altman Z</span>
                    </div>
                </div>
            </div>

            <!-- Company B -->
            <div class="bg-cardBg border-t-4 border-t-orangeAccent border-x border-b border-borderD p-6 rounded-2xl shadow-xl">
                <h2 class="text-xl font-bold text-white mb-4">{res_b.company} ({ticker_b})</h2>
                <div class="grid grid-cols-3 gap-4">
                    <div class="bg-black/30 p-4 rounded-xl border border-borderD/40">
                        <span class="text-2xl font-black {pe_b_col} block">{pe_b_text}</span>
                        <span class="text-[10px] font-bold text-gray-500 uppercase tracking-wider">P/E Ratio</span>
                    </div>
                    <div class="bg-black/30 p-4 rounded-xl border border-borderD/40">
                        <span class="text-2xl font-black {pio_b_col} block">{pio_b_text}</span>
                        <span class="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Piotroski F</span>
                    </div>
                    <div class="bg-black/30 p-4 rounded-xl border border-borderD/40">
                        <span class="text-2xl font-black {alt_b_col} block">{alt_b_text}</span>
                        <span class="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Altman Z</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- MIDDLE ROW - Grouped Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Valuation Grouped -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Valuation Comparison</h3>
                <div class="h-60 relative">
                    <canvas id="chartValuation"></canvas>
                </div>
            </div>
            <!-- Health Grouped -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Health & Credit</h3>
                <div class="h-60 relative">
                    <canvas id="chartHealth"></canvas>
                </div>
            </div>
            <!-- Growth Grouped -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Growth % Comparison</h3>
                <div class="h-60 relative">
                    <canvas id="chartGrowth"></canvas>
                </div>
            </div>
        </div>

        <!-- BOTTOM - Winner Table -->
        <div class="bg-cardBg border border-borderD rounded-2xl p-6 shadow-2xl">
            <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span class="w-1.5 h-6 bg-tealAccent rounded-full"></span>
                Detailed Comparison & Winner Matrix
            </h3>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-borderD text-xs font-bold text-gray-400 uppercase tracking-wider">
                            <th class="px-6 py-3">Metric</th>
                            <th class="px-6 py-3">{ticker_a}</th>
                            <th class="px-6 py-3">{ticker_b}</th>
                            <th class="px-6 py-3">Winner</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(table_rows)}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <footer class="border-t border-borderD pt-6 text-center text-xs text-gray-500 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div>
                Generated by <span class="font-bold text-gray-400">telmus v0.1.5</span> | <a href="https://pypi.org/project/telmus" class="text-tealAccent hover:underline" target="_blank">pypi.org/project/telmus</a>
            </div>
            <div>
                Data sourced via Yahoo Finance | {scan_date}
            </div>
        </footer>

    </div>

    <script>
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ labels: {{ color: '#a1a1aa', font: {{ family: 'Inter' }} }} }}
            }},
            scales: {{
                x: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }},
                y: {{ grid: {{ color: '#1e1e2e' }}, ticks: {{ color: '#a1a1aa' }} }}
            }}
        }};

        // Valuation Grouped
        new Chart(document.getElementById('chartValuation'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(val_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(val_a)},
                        backgroundColor: '#00b4d8',
                        borderRadius: 4
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(val_b)},
                        backgroundColor: '#ea580c',
                        borderRadius: 4
                    }}
                ]
            }},
            options: chartOptions
        }});

        // Health Grouped
        new Chart(document.getElementById('chartHealth'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(health_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(health_a)},
                        backgroundColor: '#00b4d8',
                        borderRadius: 4
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(health_b)},
                        backgroundColor: '#ea580c',
                        borderRadius: 4
                    }}
                ]
            }},
            options: chartOptions
        }});

        // Growth Grouped
        new Chart(document.getElementById('chartGrowth'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(growth_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(growth_a)},
                        backgroundColor: '#00b4d8',
                        borderRadius: 4
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(growth_b)},
                        backgroundColor: '#ea580c',
                        borderRadius: 4
                    }}
                ]
            }},
            options: chartOptions
        }});
    </script>
</body>
</html>
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def export_screen(self, results: list[ScanResult], path: str) -> None:
        scan_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_stocks = len(results)

        # Summaries calculations
        pio_values = [r.health.piotroski_f for r in results if r.health.piotroski_f is not None]
        pe_values = [r.valuation.pe_ratio for r in results if r.valuation.pe_ratio is not None]
        no_flags_count = sum(1 for r in results if not r.red_flags)

        avg_pio = sum(pio_values) / len(pio_values) if pio_values else 0.0
        avg_pe = sum(pe_values) / len(pe_values) if pe_values else 0.0

        # Construct JS lists
        tickers = [r.ticker for r in results]
        pio_scores = [r.health.piotroski_f if r.health.piotroski_f is not None else 0 for r in results]
        pe_ratios = [r.valuation.pe_ratio if r.valuation.pe_ratio is not None else 0.0 for r in results]
        altman_scores = [r.health.altman_z if r.health.altman_z is not None else 0.0 for r in results]

        # Table rows
        table_rows = []
        for r in results:
            pe_str = f"{r.valuation.pe_ratio:,.2f}" if r.valuation.pe_ratio is not None else "n/a"
            pb_str = f"{r.valuation.pb_ratio:,.2f}" if r.valuation.pb_ratio is not None else "n/a"
            alt_str = f"{r.health.altman_z:,.2f}" if r.health.altman_z is not None else "n/a"
            de_str = f"{r.health.debt_to_equity:,.2f}" if r.health.debt_to_equity is not None else "n/a"
            rev_str = f"{(r.growth.revenue_cagr_3y or 0.0) * 100:,.2f}%" if r.growth.revenue_cagr_3y is not None else "n/a"

            concern_lvl = (r.highest_concern or "LOW").upper()
            if concern_lvl == "HIGH":
                concern_badge = "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                row_border = "border-l-rose-500/60"
            elif concern_lvl == "MEDIUM":
                concern_badge = "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                row_border = "border-l-amber-500/60"
            else:
                concern_badge = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                row_border = "border-l-emerald-500/60"

            table_rows.append(f"""
            <tr class="border-b border-borderD/40 border-l-4 {row_border} hover:bg-white/[0.01] transition-all">
                <td class="px-6 py-4 text-sm font-bold text-tealAccent" data-val="{r.ticker}">{r.ticker}</td>
                <td class="px-6 py-4 text-sm text-white" data-val="{r.company}">{r.company}</td>
                <td class="px-6 py-4 text-sm text-gray-300" data-val="{r.health.piotroski_f or -1}">{r.health.piotroski_f if r.health.piotroski_f is not None else 'n/a'}</td>
                <td class="px-6 py-4 text-sm text-gray-300" data-val="{r.health.altman_z or -99}">{alt_str}</td>
                <td class="px-6 py-4 text-sm text-gray-300" data-val="{r.valuation.pe_ratio or 9999}">{pe_str}</td>
                <td class="px-6 py-4 text-sm text-gray-300" data-val="{r.valuation.pb_ratio or 9999}">{pb_str}</td>
                <td class="px-6 py-4 text-sm text-gray-300" data-val="{r.health.debt_to_equity or 9999}">{de_str}</td>
                <td class="px-6 py-4 text-sm text-gray-300" data-val="{r.growth.revenue_cagr_3y or -99}">{rev_str}</td>
                <td class="px-6 py-4 text-sm" data-val="{concern_lvl}"><span class="px-2.5 py-1 rounded text-xs font-bold uppercase {concern_badge}">{concern_lvl}</span></td>
            </tr>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="bg-darkBg">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus - Sector Screening Results</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        darkBg: '#0a0a0f',
                        cardBg: '#12121a',
                        borderD: '#1e1e2e',
                        tealAccent: '#00b4d8',
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-darkBg text-gray-100 min-h-screen flex flex-col p-6 lg:p-12">
    <div class="max-w-7xl mx-auto w-full flex-1 flex flex-col gap-8">
        
        <!-- Header -->
        <header class="flex justify-between items-center border-b border-borderD pb-6">
            <div>
                <h1 class="text-3xl font-extrabold text-white tracking-tight">
                    <span class="text-tealAccent">telmus</span> screening
                </h1>
                <p class="text-gray-400 text-sm mt-1">Sector Analysis & Screening Dashboard</p>
            </div>
            <div class="text-right hidden sm:block">
                <span class="text-xs text-gray-500 uppercase tracking-widest block">Report Date</span>
                <span class="text-sm font-semibold text-gray-300">{scan_date}</span>
            </div>
        </header>

        <!-- TOP ROW - summary KPI cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Screened count -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 hover:shadow-tealAccent/5 transition-all duration-300">
                <div class="text-4xl font-extrabold text-tealAccent">{total_stocks}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Stocks Screened</div>
            </div>
            <!-- Avg Piotroski -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 hover:shadow-tealAccent/5 transition-all duration-300">
                <div class="text-4xl font-extrabold text-emerald-400">{avg_pio:,.2f}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Average Piotroski F</div>
            </div>
            <!-- Avg PE -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 hover:shadow-tealAccent/5 transition-all duration-300">
                <div class="text-4xl font-extrabold text-indigo-400">{avg_pe:,.2f}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Average P/E Ratio</div>
            </div>
            <!-- Clean count -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 hover:shadow-tealAccent/5 transition-all duration-300">
                <div class="text-4xl font-extrabold text-amber-400">{no_flags_count}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">No Red Flag Stocks</div>
            </div>
        </div>

        <!-- CHARTS ROW -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Piotroski Horiz Bar -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Piotroski F-Scores</h3>
                <div class="h-64 relative">
                    <canvas id="chartPio"></canvas>
                </div>
            </div>
            <!-- P/E Ratio Horiz Bar -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">P/E Ratios</h3>
                <div class="h-64 relative">
                    <canvas id="chartPE"></canvas>
                </div>
            </div>
            <!-- Altman Z Horiz Bar -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Altman Z-Scores</h3>
                <div class="h-64 relative">
                    <canvas id="chartAltman"></canvas>
                </div>
            </div>
        </div>

        <!-- BOTTOM - sortable table -->
        <div class="bg-cardBg border border-borderD rounded-2xl p-6 shadow-2xl">
            <h3 class="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <span class="w-1.5 h-6 bg-tealAccent rounded-full"></span>
                Screening Metric Matrix
            </h3>
            <p class="text-xs text-gray-500 mb-4">Click table headers to sort rows dynamically.</p>
            <div class="overflow-x-auto">
                <table id="screenTable" class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-borderD text-xs font-bold text-gray-400 uppercase tracking-wider cursor-pointer">
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(0)">Ticker</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(1)">Company</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(2)">Piotroski F</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(3)">Altman Z</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(4)">P/E</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(5)">P/B</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(6)">D/E</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(7)">Revenue CAGR</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(8)">Highest Concern</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(table_rows)}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <footer class="border-t border-borderD pt-6 text-center text-xs text-gray-500 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div>
                Generated by <span class="font-bold text-gray-400">telmus v0.1.5</span> | <a href="https://pypi.org/project/telmus" class="text-tealAccent hover:underline" target="_blank">pypi.org/project/telmus</a>
            </div>
            <div>
                Data sourced via Yahoo Finance | {scan_date}
            </div>
        </footer>

    </div>

    <script>
        const tickers = {json.dumps(tickers)};
        
        // Colors mapping for Piotroski
        const pioScores = {json.dumps(pio_scores)};
        const pioColors = pioScores.map(score => score >= 7 ? '#10b981' : (score >= 5 ? '#f59e0b' : '#ef4444'));

        const chartOptions = {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }}
            }},
            scales: {{
                x: {{ grid: {{ color: '#1e1e2e' }}, ticks: {{ color: '#a1a1aa' }} }},
                y: {{ grid: {{ display: false }}, ticks: {{ color: '#a1a1aa' }} }}
            }}
        }};

        // Chart 1: Piotroski F
        new Chart(document.getElementById('chartPio'), {{
            type: 'bar',
            data: {{
                labels: tickers,
                datasets: [{{
                    data: pioScores,
                    backgroundColor: pioColors,
                    borderRadius: 4
                }}]
            }},
            options: chartOptions
        }});

        // Chart 2: P/E
        new Chart(document.getElementById('chartPE'), {{
            type: 'bar',
            data: {{
                labels: tickers,
                datasets: [{{
                    data: {json.dumps(pe_ratios)},
                    backgroundColor: '#00b4d8',
                    borderRadius: 4
                }}]
            }},
            options: chartOptions
        }});

        // Chart 3: Altman Z
        new Chart(document.getElementById('chartAltman'), {{
            type: 'bar',
            data: {{
                labels: tickers,
                datasets: [{{
                    data: {json.dumps(altman_scores)},
                    backgroundColor: '#6366f1',
                    borderRadius: 4
                }}]
            }},
            options: chartOptions
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
                    
                    let xNum = parseFloat(xVal.replace('%', ''));
                    let yNum = parseFloat(yVal.replace('%', ''));
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
