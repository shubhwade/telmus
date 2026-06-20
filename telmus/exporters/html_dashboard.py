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
        rev_cagr = result.growth.revenue_cagr_3y
        fcf_yield = result.growth.fcf_yield
        m_score = result.beneish_m if result.beneish_m is not None else -2.22

        # P/E Color and Label logic
        pe_text = self._fmt(pe)
        if pe is None:
            pe_color = "text-gray-400"
        elif 0 <= pe < 20:
            pe_color = "text-[#00d4aa]" # green
        elif 20 <= pe <= 35:
            pe_color = "text-[#e3b341]" # amber
        else:
            pe_color = "text-[#f78166]" # red

        # Piotroski Color
        pio_text = f"{pio}/9" if pio is not None else "n/a"
        if pio is None:
            pio_color = "text-gray-400"
        elif pio >= 7:
            pio_color = "text-[#00d4aa]"
        elif pio >= 5:
            pio_color = "text-[#e3b341]"
        else:
            pio_color = "text-[#f78166]"

        # Altman Z Color
        altman_text = self._fmt(altman)
        if altman is None:
            altman_color = "text-gray-400"
        elif altman > 2.6:
            altman_color = "text-[#00d4aa]"
        elif altman >= 1.1:
            altman_color = "text-[#e3b341]"
        else:
            altman_color = "text-[#f78166]"

        # Revenue CAGR Color
        cagr_text = self._fmt_pct(rev_cagr)
        if rev_cagr is None:
            cagr_color = "text-gray-400"
        elif rev_cagr > 0:
            cagr_color = "text-[#00d4aa]"
        else:
            cagr_color = "text-[#f78166]"

        # Compute Piotroski individual signals on the fly
        from telmus.core.loaders import load_financials
        from telmus.core.engines.health import HealthEngine
        import pandas as pd

        signals = {
            "ROA Positive": ("Company is profitable", False),
            "CFO Positive": ("Operations generate cash", False),
            "ROA Improving": ("Profitability improving", False),
            "Low Accruals": ("Earnings quality is high", False),
            "Leverage Falling": ("Debt burden reducing", False),
            "Liquidity Rising": ("Short-term health improving", False),
            "No Dilution": ("No new shares issued", False),
            "Gross Margin Rising": ("Pricing power improving", False),
            "Asset Turnover Rising": ("Using assets efficiently", False),
        }

        try:
            financials = load_financials(result.ticker)
            income_stmt = financials.get("income_stmt")
            if income_stmt is None:
                income_stmt = pd.DataFrame()
            balance_sheet = financials.get("balance_sheet")
            if balance_sheet is None:
                balance_sheet = pd.DataFrame()
            cashflow = financials.get("cashflow")
            if cashflow is None:
                cashflow = pd.DataFrame()

            he = HealthEngine()
            signals["ROA Positive"] = (signals["ROA Positive"][0], he._roa_positive(income_stmt, balance_sheet))
            signals["CFO Positive"] = (signals["CFO Positive"][0], he._cfo_positive(cashflow))
            signals["ROA Improving"] = (signals["ROA Improving"][0], he._roa_increasing(income_stmt, balance_sheet))
            signals["Low Accruals"] = (signals["Low Accruals"][0], he._accruals(income_stmt, cashflow))
            signals["Leverage Falling"] = (signals["Leverage Falling"][0], he._leverage_decreasing(balance_sheet))
            signals["Liquidity Rising"] = (signals["Liquidity Rising"][0], he._liquidity_increasing(balance_sheet))
            signals["No Dilution"] = (signals["No Dilution"][0], he._no_dilution(balance_sheet))
            signals["Gross Margin Rising"] = (signals["Gross Margin Rising"][0], he._gross_margin_increasing(income_stmt))
            signals["Asset Turnover Rising"] = (signals["Asset Turnover Rising"][0], he._asset_turnover_increasing(income_stmt, balance_sheet))
        except Exception:
            pass

        # Build Piotroski checklist HTML
        checklist_items = []
        for name, (desc, passed) in signals.items():
            status_icon = '<span class="text-[#00d4aa] text-lg">✔</span>' if passed else '<span class="text-[#f78166] text-lg">✘</span>'
            status_bg = "bg-[#00d4aa]/5 border-[#00d4aa]/20" if passed else "bg-[#f78166]/5 border-[#f78166]/20"
            checklist_items.append(f"""
            <div class="flex items-center gap-3 p-3.5 rounded-xl border {status_bg} transition-all">
                {status_icon}
                <div>
                    <div class="text-xs font-bold text-gray-300 uppercase tracking-wider">{name}</div>
                    <div class="text-[11px] text-gray-500">{desc}</div>
                </div>
            </div>
            """)

        # Analyst Brief Pill Badges
        val_status = (result.valuation.vs_sector or "FAIR").upper()
        if val_status == "CHEAP":
            val_badge = "bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20"
        elif val_status == "EXPENSIVE":
            val_badge = "bg-[#f78166]/10 text-[#f78166] border border-[#f78166]/20"
        else:
            val_badge = "bg-gray-500/10 text-gray-400 border border-gray-500/20"

        pio_score = pio if pio is not None else 0
        if pio_score >= 7:
            health_badge = "bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20"
            health_text = "HEALTH: STRONG"
        elif pio_score >= 5:
            health_badge = "bg-[#e3b341]/10 text-[#e3b341] border border-[#e3b341]/20"
            health_text = "HEALTH: ADEQUATE"
        else:
            health_badge = "bg-[#f78166]/10 text-[#f78166] border border-[#f78166]/20"
            health_text = "HEALTH: WEAK"

        if rev_cagr is not None and rev_cagr > 0:
            growth_badge = "bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20"
            growth_text = "GROWTH: POSITIVE"
        else:
            growth_badge = "bg-[#f78166]/10 text-[#f78166] border border-[#f78166]/20"
            growth_text = "GROWTH: DECLINING"

        # Red flags or success banner
        FLAG_MEANINGS = {
            "negative_fcf": "Free Cash Flow is negative, indicating cash burn",
            "negative_revenue_growth": "Revenue is declining, showing contraction",
            "high_debt": "Debt to Equity ratio is high, increasing credit risk",
            "weak_piotroski": "Low Piotroski score indicates weak core business health",
            "distress_z": "Altman Z-Score indicates high risk of credit distress",
            "expensive_sector": "Valuation is expensive relative to peer sector median",
            "high_leverage": "High leverage ratio increases financial risk",
            "low_current_ratio": "Current ratio is below safe liquidity threshold",
            "low_interest_coverage": "Interest coverage is weak, indicating debt service concerns",
        }

        if not result.red_flags:
            flags_html = f"""
            <div class="bg-[#00d4aa]/10 border border-[#00d4aa]/20 text-[#00d4aa] px-6 py-5 rounded-2xl flex items-center gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-6 h-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="font-bold text-base">No Red Flags Detected — Beneish M-Score of {m_score:.2f} indicates low manipulation risk</span>
            </div>
            """
        else:
            rows = []
            for flag in result.red_flags:
                sev = flag.severity.upper()
                if sev == "HIGH":
                    badge = "bg-[#f78166]/10 text-[#f78166] border border-[#f78166]/20"
                elif sev == "MEDIUM":
                    badge = "bg-[#e3b341]/10 text-[#e3b341] border border-[#e3b341]/20"
                else:
                    badge = "bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20"
                
                meaning = FLAG_MEANINGS.get(flag.type, "Triggered threshold alert")
                rows.append(f"""
                <tr class="border-b border-[#21262d] hover:bg-white/[0.01] transition-all">
                    <td class="px-6 py-4 text-sm font-semibold text-white">{flag.type}</td>
                    <td class="px-6 py-4 text-sm text-gray-300 font-mono">{self._fmt(flag.value)}</td>
                    <td class="px-6 py-4 text-sm"><span class="px-2.5 py-1 rounded text-xs font-bold {badge}">{sev}</span></td>
                    <td class="px-6 py-4 text-sm text-gray-400">{meaning}</td>
                </tr>
                """)
            flags_html = f"""
            <div class="bg-[#161b22] border border-[#21262d] rounded-2xl p-6 shadow-2xl">
                <h3 class="text-sm font-extrabold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-4 bg-[#f78166] rounded-full"></span>
                    Red Flags ({len(result.red_flags)})
                </h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-[#21262d]">
                                <th class="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Flag</th>
                                <th class="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Value</th>
                                <th class="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Severity</th>
                                <th class="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">What it means</th>
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
        pat_cagr_pct = (result.growth.pat_cagr_3y or 0.0) * 100.0
        fcf_yield_pct = (fcf_yield or 0.0) * 100.0

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="bg-[#0d1117]">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus - {result.company} ({result.ticker}) Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        darkBg: '#0d1117',
                        cardBg: '#161b22',
                        borderD: '#21262d',
                        tealAccent: '#00d4aa',
                        coralAccent: '#f78166',
                        amberAccent: '#e3b341'
                    }},
                    fontFamily: {{
                        mono: ['JetBrains Mono', 'monospace'],
                        sans: ['Inter', 'sans-serif']
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-darkBg text-gray-100 min-h-screen flex flex-col p-6 lg:p-12 font-sans">
    <div class="max-w-7xl mx-auto w-full flex-1 flex flex-col gap-8">
        
        <!-- Header -->
        <header class="flex flex-col border-b border-borderD pb-6 gap-2">
            <div class="flex justify-between items-start flex-wrap gap-4">
                <div>
                    <h1 class="text-3xl font-extrabold text-white tracking-tight">{result.company}</h1>
                    <p class="text-gray-400 text-sm mt-1 uppercase font-semibold font-mono tracking-wider">
                        {result.ticker} | {result.exchange} | Last scanned: {scan_date}
                    </p>
                </div>
                <div>
                    <span class="text-2xl font-black text-white font-mono tracking-tight">
                        <span class="text-tealAccent">telmus</span> v0.1.6
                    </span>
                </div>
            </div>
            <p class="text-gray-500 text-sm italic mt-2">"{result.analyst_brief}"</p>
        </header>

        <!-- KPI ROW (4 cards) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- P/E Card -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 transition-all duration-300">
                <div class="text-4xl font-extrabold font-mono {pe_color}">{pe_text}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">P/E Ratio</div>
                <p class="text-[10px] text-gray-500 mt-1">Price you pay per ₹1 of earnings</p>
            </div>
            <!-- Piotroski Card -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 transition-all duration-300">
                <div class="text-4xl font-extrabold font-mono {pio_color}">{pio_text}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Piotroski F-Score</div>
                <p class="text-[10px] text-gray-500 mt-1">Financial health score (higher = stronger)</p>
            </div>
            <!-- Altman Z Card -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 transition-all duration-300">
                <div class="text-4xl font-extrabold font-mono {altman_color}">{altman_text}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Altman Z-Score</div>
                <p class="text-[10px] text-gray-500 mt-1">Bankruptcy risk (&gt;2.6 = safe)</p>
            </div>
            <!-- Revenue CAGR Card -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 transition-all duration-300">
                <div class="text-4xl font-extrabold font-mono {cagr_color}">{cagr_text}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Revenue CAGR (3Y)</div>
                <p class="text-[10px] text-gray-500 mt-1">3-year revenue growth rate</p>
            </div>
        </div>

        <!-- GAUGE ROW (3 gauges) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Piotroski F Gauge -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col items-center">
                <h3 class="text-xs font-extrabold text-gray-400 uppercase tracking-wider mb-4">Piotroski F-Score</h3>
                <div class="relative w-full max-w-[200px] aspect-[2/1] flex flex-col items-center">
                    <canvas id="gaugePio"></canvas>
                    <div class="absolute bottom-1 text-center">
                        <span class="text-2xl font-black text-white font-mono">{pio_text}</span>
                    </div>
                </div>
                <span class="text-xs text-gray-500 mt-2 text-center uppercase tracking-wider font-semibold font-mono">
                    {pio_score}/9 — { 'Strong fundamentals' if pio_score >= 7 else ('Adequate fundamentals' if pio_score >= 5 else 'Weak fundamentals') }
                </span>
            </div>
            <!-- Altman Z Gauge -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col items-center">
                <h3 class="text-xs font-extrabold text-gray-400 uppercase tracking-wider mb-4">Altman Z-Score</h3>
                <div class="relative w-full max-w-[200px] aspect-[2/1] flex flex-col items-center">
                    <canvas id="gaugeAltman"></canvas>
                    <div class="absolute bottom-1 text-center">
                        <span class="text-2xl font-black text-white font-mono">{altman_text}</span>
                    </div>
                </div>
                <span class="text-xs text-gray-500 mt-2 text-center uppercase tracking-wider font-semibold font-mono">
                    { 'Safe zone (Z > 2.6)' if (altman or 0) > 2.6 else ('Grey zone (1.1 - 2.6)' if (altman or 0) >= 1.1 else 'Distress zone (Z < 1.1)') }
                </span>
            </div>
            <!-- FCF Yield Gauge -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col items-center">
                <h3 class="text-xs font-extrabold text-gray-400 uppercase tracking-wider mb-4">FCF Yield</h3>
                <div class="relative w-full max-w-[200px] aspect-[2/1] flex flex-col items-center">
                    <canvas id="gaugeFCF"></canvas>
                    <div class="absolute bottom-1 text-center">
                        <span class="text-2xl font-black text-white font-mono">{self._fmt_pct(fcf_yield)}</span>
                    </div>
                </div>
                <span class="text-xs text-gray-500 mt-2 text-center uppercase tracking-wider font-semibold font-mono">
                    { 'High yield' if (fcf_yield or 0.0) >= 0.08 else ('Adequate yield' if (fcf_yield or 0.0) >= 0.02 else 'Weak/Negative yield') }
                </span>
            </div>
        </div>

        <!-- CHARTS ROW (2 side by side) -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Valuation Benchmarks -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-xs font-extrabold text-gray-400 uppercase tracking-wider mb-6 flex items-center gap-2">
                    <span class="w-1.5 h-4 bg-tealAccent rounded-full"></span>
                    Valuation Benchmarks
                </h3>
                <div class="h-64 relative">
                    <canvas id="chartValuation"></canvas>
                </div>
            </div>
            <!-- Growth Metrics -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-xs font-extrabold text-gray-400 uppercase tracking-wider mb-6 flex items-center gap-2">
                    <span class="w-1.5 h-4 bg-indigo-500 rounded-full"></span>
                    Growth Metrics (3Y CAGR)
                </h3>
                <div class="h-64 relative">
                    <canvas id="chartGrowth"></canvas>
                </div>
            </div>
        </div>

        <!-- PIOTROSKI BREAKDOWN checklist -->
        <div class="bg-cardBg border border-borderD rounded-2xl p-6 shadow-2xl">
            <h3 class="text-sm font-extrabold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                <span class="w-1.5 h-4 bg-tealAccent rounded-full"></span>
                Piotroski F-Score Breakdown — {pio_score}/9 Signals Passed
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {"".join(checklist_items)}
            </div>
        </div>

        <!-- AI Analyst Brief -->
        <div class="bg-cardBg border-l-4 border-l-tealAccent border border-y-borderD border-r-borderD p-8 rounded-2xl shadow-2xl flex flex-col gap-4">
            <div>
                <h3 class="text-xs font-extrabold text-gray-400 uppercase tracking-wider mb-2">AI Analyst Brief</h3>
                <p class="text-gray-100 leading-relaxed font-semibold">{result.analyst_brief}</p>
            </div>
            <div class="flex flex-wrap gap-2">
                <span class="px-2.5 py-1 rounded text-[10px] font-extrabold uppercase font-mono {val_badge}">VALUATION: {val_status}</span>
                <span class="px-2.5 py-1 rounded text-[10px] font-extrabold uppercase font-mono {health_badge}">{health_text}</span>
                <span class="px-2.5 py-1 rounded text-[10px] font-extrabold uppercase font-mono {growth_badge}">{growth_text}</span>
            </div>
        </div>

        <!-- RED FLAGS SECTION -->
        {flags_html}

        <!-- Footer -->
        <footer class="border-t border-borderD pt-6 text-center text-xs text-gray-500 flex flex-col sm:flex-row justify-between items-center gap-4 mt-8 font-mono">
            <div>
                Generated by <span class="font-bold text-gray-400">telmus v0.1.6</span> | <code class="bg-[#161b22] px-1.5 py-0.5 rounded text-gray-400">pip install telmus</code>
            </div>
            <div>
                Data via Yahoo Finance | Not financial advice
            </div>
        </footer>

    </div>

    <script>
        // Custom benchmark line drawing plugin
        const benchmarkLinesPlugin = {{
            afterDraw(chart, args, options) {{
                const ctx = chart.ctx;
                const left = chart.chartArea.left;
                const right = chart.chartArea.right;
                const y = chart.scales.y;
                ctx.save();
                
                (options.lines || []).forEach(line => {{
                    const yPos = y.getPixelForValue(line.value);
                    if (yPos >= chart.chartArea.top && yPos <= chart.chartArea.bottom) {{
                        ctx.strokeStyle = line.color || '#f78166';
                        ctx.lineWidth = line.lineWidth || 1.5;
                        ctx.setLineDash(line.lineDash || [5, 5]);
                        
                        ctx.beginPath();
                        ctx.moveTo(left, yPos);
                        ctx.lineTo(right, yPos);
                        ctx.stroke();
                        
                        ctx.fillStyle = line.color || '#f78166';
                        ctx.font = '10px Inter';
                        ctx.fillText(line.label, left + 10, yPos - 5);
                    }}
                }});
                ctx.restore();
            }}
        }};
        Chart.register(benchmarkLinesPlugin);

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
        const pioScore = {pio_score};
        new Chart(document.getElementById('gaugePio'), {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [pioScore, Math.max(0, 9 - pioScore)],
                    backgroundColor: [pioScore >= 7 ? '#00d4aa' : (pioScore >= 5 ? '#e3b341' : '#f78166'), '#21262d'],
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
                    backgroundColor: [altmanScore > 2.6 ? '#00d4aa' : (altmanScore >= 1.1 ? '#e3b341' : '#f78166'), '#21262d'],
                    borderWidth: 0
                }}]
            }},
            options: gaugeOptions
        }});

        // FCF Yield Gauge (Capped at 50% for display)
        const fcfYield = {fcf_yield_pct};
        const cappedFCF = Math.min(50.0, Math.max(0.0, fcfYield));
        new Chart(document.getElementById('gaugeFCF'), {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [cappedFCF, 50.0 - cappedFCF],
                    backgroundColor: [fcfYield > 0 ? '#00d4aa' : '#f78166', '#21262d'],
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
                labels: ['P/E (Earnings)', 'P/B (Assets)', 'EV/EBITDA (EBITDA)'],
                datasets: [{{
                    label: 'Valuation',
                    data: [peVal, pbVal, evVal],
                    backgroundColor: [
                        peVal < 20 ? '#00d4aa' : '#f78166',
                        pbVal < 3 ? '#00d4aa' : '#f78166',
                        evVal < 10 ? '#00d4aa' : '#f78166'
                    ],
                    borderRadius: 4,
                    barThickness: 35
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    benchmarkLines: {{
                        lines: [
                            {{ value: 20, label: 'P/E Fair Value (20)', color: '#00d4aa', lineDash: [4, 4] }},
                            {{ value: 10, label: 'EV/EBITDA Sector Avg (10)', color: '#f78166', lineDash: [4, 4] }}
                        ]
                    }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#8b949e', font: {{ family: 'Inter', size: 10 }} }} }},
                    y: {{ grid: {{ color: '#21262d' }}, ticks: {{ color: '#8b949e', font: {{ family: 'JetBrains Mono' }} }} }}
                }}
            }}
        }});

        // Growth Chart
        const revCagrVal = {rev_cagr * 100.0 if rev_cagr is not None else 0.0};
        const patCagrVal = {pat_cagr_pct};
        const fcfYieldVal = {fcf_yield_pct};
        
        new Chart(document.getElementById('chartGrowth'), {{
            type: 'bar',
            data: {{
                labels: ['Revenue CAGR', 'PAT CAGR', 'FCF Yield'],
                datasets: [{{
                    label: 'Growth %',
                    data: [revCagrVal, patCagrVal, fcfYieldVal],
                    backgroundColor: [
                        revCagrVal > 0 ? '#00d4aa' : '#f78166',
                        patCagrVal > 0 ? '#00d4aa' : '#f78166',
                        fcfYieldVal > 0 ? '#00d4aa' : '#f78166'
                    ],
                    borderRadius: 4,
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
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#8b949e', font: {{ family: 'Inter', size: 10 }} }} }},
                    y: {{ grid: {{ color: '#21262d' }}, ticks: {{ color: '#8b949e', font: {{ family: 'JetBrains Mono' }} }} }}
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
                return f"{val:,.2f}", "text-[#00d4aa]"
            if val <= 35:
                return f"{val:,.2f}", "text-[#e3b341]"
            return f"{val:,.2f}", "text-[#f78166]"

        def _get_pio_styles(val: int | None) -> tuple[str, str]:
            if val is None:
                return "n/a", "text-gray-400"
            if val >= 7:
                return f"{val}/9", "text-[#00d4aa]"
            if val >= 5:
                return f"{val}/9", "text-[#e3b341]"
            return f"{val}/9", "text-[#f78166]"

        def _get_alt_styles(val: float | None) -> tuple[str, str]:
            if val is None:
                return "n/a", "text-gray-400"
            if val > 2.6:
                return f"{val:,.2f}", "text-[#00d4aa]"
            if val >= 1.1:
                return f"{val:,.2f}", "text-[#e3b341]"
            return f"{val:,.2f}", "text-[#f78166]"

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

            style_a = "bg-[#00d4aa]/10 text-[#00d4aa] font-bold font-mono" if win_code == "A" else "text-gray-400 font-mono bg-white/[0.01]"
            style_b = "bg-[#00d4aa]/10 text-[#00d4aa] font-bold font-mono" if win_code == "B" else "text-gray-400 font-mono bg-white/[0.01]"
            
            if win_code in ("A", "B"):
                win_display = f"""<span class="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#00d4aa]/10 text-[#00d4aa] text-xs font-bold border border-[#00d4aa]/20">
                    👑 {win_text}
                </span>"""
            else:
                win_display = f"""<span class="px-2.5 py-1 rounded bg-gray-500/10 text-gray-400 text-xs font-bold border border-gray-500/20">Draw</span>"""

            table_rows.append(f"""
            <tr class="border-b border-[#21262d] hover:bg-white/[0.01] transition-all">
                <td class="px-6 py-4 text-sm font-semibold text-white">{name}</td>
                <td class="px-6 py-4 text-sm {style_a}">{str_a}</td>
                <td class="px-6 py-4 text-sm {style_b}">{str_b}</td>
                <td class="px-6 py-4 text-sm">{win_display}</td>
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
<html lang="en" class="bg-[#0d1117]">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus Comparison - {ticker_a} vs {ticker_b}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        darkBg: '#0d1117',
                        cardBg: '#161b22',
                        borderD: '#21262d',
                        tealAccent: '#00d4aa',
                        coralAccent: '#f78166',
                        amberAccent: '#e3b341'
                    }},
                    fontFamily: {{
                        mono: ['JetBrains Mono', 'monospace'],
                        sans: ['Inter', 'sans-serif']
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-darkBg text-gray-100 min-h-screen flex flex-col p-6 lg:p-12 font-sans">
    <div class="max-w-7xl mx-auto w-full flex-1 flex flex-col gap-8">
        
        <!-- Header -->
        <header class="flex justify-between items-center border-b border-borderD pb-6">
            <div>
                <h1 class="text-2xl font-extrabold text-white tracking-tight">{ticker_a} vs {ticker_b} — Head to Head Analysis</h1>
                <p class="text-gray-400 text-xs mt-1 uppercase font-semibold font-mono tracking-wider">Comparison Scan | {scan_date}</p>
            </div>
            <div class="text-right">
                <span class="text-xs text-gray-500 uppercase tracking-widest block font-mono">System</span>
                <span class="text-sm font-semibold text-gray-300 font-mono"><span class="text-tealAccent">telmus</span> v0.1.6</span>
            </div>
        </header>

        <!-- TWO COLUMN COMPANY HEADERS -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Company -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex items-center gap-4">
                <div class="w-12 h-12 rounded-full bg-[#00d4aa]/10 border border-[#00d4aa]/20 flex items-center justify-center font-bold text-[#00d4aa] text-lg font-mono">
                    {ticker_a[0]}
                </div>
                <div>
                    <h2 class="text-lg font-bold text-white">{res_a.company}</h2>
                    <p class="text-xs text-gray-400 font-mono">{ticker_a} | {res_a.exchange}</p>
                </div>
            </div>

            <!-- Right Company -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex items-center gap-4">
                <div class="w-12 h-12 rounded-full bg-[#f78166]/10 border border-[#f78166]/20 flex items-center justify-center font-bold text-[#f78166] text-lg font-mono">
                    {ticker_b[0]}
                </div>
                <div>
                    <h2 class="text-lg font-bold text-white">{res_b.company}</h2>
                    <p class="text-xs text-gray-400 font-mono">{ticker_b} | {res_b.exchange}</p>
                </div>
            </div>
        </div>

        <!-- GROUPED BAR CHARTS (3 charts) -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Valuation Chart -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Valuation</h3>
                <div class="h-60 relative">
                    <canvas id="chartValuation"></canvas>
                </div>
            </div>
            <!-- Health Chart -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Health</h3>
                <div class="h-60 relative">
                    <canvas id="chartHealth"></canvas>
                </div>
            </div>
            <!-- Growth Chart -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Growth</h3>
                <div class="h-60 relative">
                    <canvas id="chartGrowth"></canvas>
                </div>
            </div>
        </div>

        <!-- WINNER TABLE -->
        <div class="bg-cardBg border border-borderD rounded-2xl p-6 shadow-2xl">
            <h3 class="text-sm font-extrabold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                <span class="w-1.5 h-4 bg-tealAccent rounded-full"></span>
                Head-to-Head Winner Table
            </h3>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-borderD text-xs font-bold text-gray-500 uppercase tracking-wider">
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
        <footer class="border-t border-borderD pt-6 text-center text-xs text-gray-500 flex flex-col sm:flex-row justify-between items-center gap-4 font-mono">
            <div>
                Generated by <span class="font-bold text-gray-400">telmus v0.1.6</span> | <code class="bg-[#161b22] px-1.5 py-0.5 rounded text-gray-400">pip install telmus</code>
            </div>
            <div>
                Data via Yahoo Finance | Not financial advice
            </div>
        </footer>

    </div>

    <script>
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ labels: {{ color: '#8b949e', font: {{ family: 'Inter', size: 10 }} }} }}
            }},
            scales: {{
                x: {{ grid: {{ display: false }}, ticks: {{ color: '#8b949e', font: {{ family: 'Inter', size: 10 }} }} }},
                y: {{ grid: {{ color: '#21262d' }}, ticks: {{ color: '#8b949e', font: {{ family: 'JetBrains Mono' }} }} }}
            }}
        }};

        // Valuation Chart
        new Chart(document.getElementById('chartValuation'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(val_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(val_a)},
                        backgroundColor: '#00d4aa',
                        borderRadius: 4
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(val_b)},
                        backgroundColor: '#f78166',
                        borderRadius: 4
                    }}
                ]
            }},
            options: chartOptions
        }});

        // Health Chart
        new Chart(document.getElementById('chartHealth'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(health_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(health_a)},
                        backgroundColor: '#00d4aa',
                        borderRadius: 4
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(health_b)},
                        backgroundColor: '#f78166',
                        borderRadius: 4
                    }}
                ]
            }},
            options: chartOptions
        }});

        // Growth Chart
        new Chart(document.getElementById('chartGrowth'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(growth_labels)},
                datasets: [
                    {{
                        label: '{ticker_a}',
                        data: {json.dumps(growth_a)},
                        backgroundColor: '#00d4aa',
                        borderRadius: 4
                    }},
                    {{
                        label: '{ticker_b}',
                        data: {json.dumps(growth_b)},
                        backgroundColor: '#f78166',
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
        n = len(results)

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
        for idx, r in enumerate(results, start=1):
            pe_str = f"{r.valuation.pe_ratio:,.2f}" if r.valuation.pe_ratio is not None else "n/a"
            alt_str = f"{r.health.altman_z:,.2f}" if r.health.altman_z is not None else "n/a"
            rev_str = f"{(r.growth.revenue_cagr_3y or 0.0) * 100:,.2f}%" if r.growth.revenue_cagr_3y is not None else "n/a"

            concern_lvl = (r.highest_concern or "LOW").upper()
            if concern_lvl == "HIGH":
                concern_badge = "bg-[#f78166]/10 text-[#f78166] border border-[#f78166]/20"
                row_bg = "bg-[#f78166]/5 border-l-4 border-l-[#f78166]"
            elif concern_lvl == "MEDIUM":
                concern_badge = "bg-[#e3b341]/10 text-[#e3b341] border border-[#e3b341]/20"
                row_bg = "bg-[#e3b341]/5 border-l-4 border-l-[#e3b341]"
            else:
                concern_badge = "bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20"
                row_bg = "bg-[#00d4aa]/5 border-l-4 border-l-[#00d4aa]"

            table_rows.append(f"""
            <tr class="border-b border-[#21262d] {row_bg} hover:bg-white/[0.01] transition-all">
                <td class="px-6 py-4 text-sm font-bold text-gray-400 font-mono" data-val="{idx}">{idx}</td>
                <td class="px-6 py-4 text-sm text-white font-semibold" data-val="{r.company}">{r.company}</td>
                <td class="px-6 py-4 text-sm font-bold text-tealAccent font-mono" data-val="{r.ticker}">{r.ticker}</td>
                <td class="px-6 py-4 text-sm text-gray-300 font-mono" data-val="{r.valuation.pe_ratio or 9999}">{pe_str}</td>
                <td class="px-6 py-4 text-sm text-gray-300 font-mono" data-val="{r.health.piotroski_f or -1}">{r.health.piotroski_f if r.health.piotroski_f is not None else 'n/a'}</td>
                <td class="px-6 py-4 text-sm text-gray-300 font-mono" data-val="{r.health.altman_z or -99}">{alt_str}</td>
                <td class="px-6 py-4 text-sm text-gray-300 font-mono" data-val="{r.growth.revenue_cagr_3y or -99}">{rev_str}</td>
                <td class="px-6 py-4 text-sm" data-val="{concern_lvl}"><span class="px-2.5 py-1 rounded text-xs font-bold uppercase {concern_badge}">{concern_lvl}</span></td>
            </tr>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="bg-[#0d1117]">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>telmus - Sector Screen Results</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        darkBg: '#0d1117',
                        cardBg: '#161b22',
                        borderD: '#21262d',
                        tealAccent: '#00d4aa',
                        coralAccent: '#f78166',
                        amberAccent: '#e3b341'
                    }},
                    fontFamily: {{
                        mono: ['JetBrains Mono', 'monospace'],
                        sans: ['Inter', 'sans-serif']
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-darkBg text-gray-100 min-h-screen flex flex-col p-6 lg:p-12 font-sans">
    <div class="max-w-7xl mx-auto w-full flex-1 flex flex-col gap-8">
        
        <!-- Header -->
        <header class="flex justify-between items-center border-b border-borderD pb-6">
            <div>
                <h1 class="text-2xl font-extrabold text-white tracking-tight">Sector Screen Results — {n} companies analysed</h1>
                <p class="text-gray-400 text-xs mt-1 uppercase font-semibold font-mono tracking-wider">Screening Report | {scan_date}</p>
            </div>
            <div class="text-right">
                <span class="text-xs text-gray-500 uppercase tracking-widest block font-mono">System</span>
                <span class="text-sm font-semibold text-gray-300 font-mono"><span class="text-tealAccent">telmus</span> v0.1.6</span>
            </div>
        </header>

        <!-- SUMMARY KPI ROW -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Screened -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 transition-all duration-300">
                <div class="text-4xl font-extrabold font-mono text-tealAccent">{n}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Stocks Screened</div>
            </div>
            <!-- Avg Piotroski -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 transition-all duration-300">
                <div class="text-4xl font-extrabold font-mono text-emerald-400">{avg_pio:,.2f}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Average Piotroski F</div>
            </div>
            <!-- Avg PE -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 transition-all duration-300">
                <div class="text-4xl font-extrabold font-mono text-indigo-400">{avg_pe:,.2f}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">Average P/E Ratio</div>
            </div>
            <!-- Clean count -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl hover:border-tealAccent/30 transition-all duration-300">
                <div class="text-4xl font-extrabold font-mono text-amber-400">{no_flags_count}</div>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-2">No Red Flag Stocks</div>
            </div>
        </div>

        <!-- HORIZONTAL BAR CHARTS -->
        <div class="grid grid-cols-1 gap-6">
            <!-- Piotroski Horiz -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Piotroski F-Score Comparison</h3>
                <div class="h-64 relative">
                    <canvas id="chartPio"></canvas>
                </div>
            </div>
            <!-- P/E Ratio Horiz -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">P/E Ratio Comparison</h3>
                <div class="h-64 relative">
                    <canvas id="chartPE"></canvas>
                </div>
            </div>
            <!-- Altman Z Horiz -->
            <div class="bg-cardBg border border-borderD p-6 rounded-2xl shadow-xl flex flex-col">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Altman Z-Score Comparison</h3>
                <div class="h-64 relative">
                    <canvas id="chartAltman"></canvas>
                </div>
            </div>
        </div>

        <!-- RESULTS TABLE (full width, sortable) -->
        <div class="bg-cardBg border border-borderD rounded-2xl p-6 shadow-2xl">
            <h3 class="text-sm font-extrabold text-white uppercase tracking-wider mb-2 flex items-center gap-2">
                <span class="w-1.5 h-4 bg-tealAccent rounded-full"></span>
                Screening Results (Click Headers to Sort)
            </h3>
            <div class="overflow-x-auto">
                <table id="screenTable" class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-borderD text-xs font-bold text-gray-500 uppercase tracking-wider cursor-pointer">
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(0)">Rank</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(1)">Company</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(2)">Ticker</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(3)">P/E</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(4)">Piotroski F</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(5)">Altman Z</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(6)">Revenue CAGR</th>
                            <th class="px-6 py-3 hover:text-tealAccent" onclick="sortTable(7)">Concern Level</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(table_rows)}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <footer class="border-t border-borderD pt-6 text-center text-xs text-gray-500 flex flex-col sm:flex-row justify-between items-center gap-4 font-mono">
            <div>
                Generated by <span class="font-bold text-gray-400">telmus v0.1.6</span> | <code class="bg-[#161b22] px-1.5 py-0.5 rounded text-gray-400">pip install telmus</code>
            </div>
            <div>
                Data via Yahoo Finance | Not financial advice
            </div>
        </footer>

    </div>

    <script>
        // Custom vertical line plugin
        const verticalLinePlugin = {{
            id: 'verticalLine',
            afterDraw(chart, args, options) {{
                const ctx = chart.ctx;
                const top = chart.chartArea.top;
                const bottom = chart.chartArea.bottom;
                const x = chart.scales.x;
                ctx.save();
                
                (options.lines || []).forEach(line => {{
                    const xPos = x.getPixelForValue(line.value);
                    if (xPos >= chart.chartArea.left && xPos <= chart.chartArea.right) {{
                        ctx.strokeStyle = line.color || '#ef4444';
                        ctx.lineWidth = line.lineWidth || 1.5;
                        ctx.setLineDash(line.lineDash || [4, 4]);
                        
                        ctx.beginPath();
                        ctx.moveTo(xPos, top);
                        ctx.lineTo(xPos, bottom);
                        ctx.stroke();
                        
                        ctx.fillStyle = line.color || '#ef4444';
                        ctx.font = '10px Inter';
                        ctx.fillText(line.label, xPos + 5, top + 15);
                    }}
                }});
                ctx.restore();
            }}
        }};
        Chart.register(verticalLinePlugin);

        const tickers = {json.dumps(tickers)};
        
        // Colors mapping for Piotroski
        const pioScores = {json.dumps(pio_scores)};
        const pioColors = pioScores.map(score => score >= 7 ? '#00d4aa' : (score >= 5 ? '#e3b341' : '#f78166'));

        const chartOptions = {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }}
            }},
            scales: {{
                x: {{ grid: {{ color: '#21262d' }}, ticks: {{ color: '#8b949e', font: {{ family: 'JetBrains Mono' }} }} }},
                y: {{ grid: {{ display: false }}, ticks: {{ color: '#8b949e', font: {{ family: 'Inter', size: 10 }} }} }}
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
            options: {{
                ...chartOptions,
                plugins: {{
                    legend: {{ display: false }},
                    verticalLine: {{
                        lines: [
                            {{ value: 7, label: 'Strong threshold (7)', color: '#00d4aa' }},
                            {{ value: 5, label: 'Adequate threshold (5)', color: '#e3b341' }}
                        ]
                    }}
                }}
            }}
        }});

        // Chart 2: P/E
        new Chart(document.getElementById('chartPE'), {{
            type: 'bar',
            data: {{
                labels: tickers,
                datasets: [{{
                    data: {json.dumps(pe_ratios)},
                    backgroundColor: '#00d4aa',
                    borderRadius: 4
                }}]
            }},
            options: {{
                ...chartOptions,
                plugins: {{
                    legend: {{ display: false }},
                    verticalLine: {{
                        lines: [
                            {{ value: 20, label: 'Fair value benchmark (20)', color: '#00d4aa' }}
                        ]
                    }}
                }}
            }}
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
            options: {{
                ...chartOptions,
                plugins: {{
                    legend: {{ display: false }},
                    verticalLine: {{
                        lines: [
                            {{ value: 2.6, label: 'Safety zone (2.6)', color: '#00d4aa' }}
                        ]
                    }}
                }}
            }}
        }});

        // Sorting Logic
        let sortDirections = Array(8).fill(false);
        function sortTable(colIndex) {{
            const table = document.getElementById("screenTable");
            let rows, switching, i, x, y, shouldSwitch;
            const dirAsc = !sortDirections[colIndex];
            sortDirections = Array(8).fill(false);
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
