import re

file_path = 'telmus/exporters/html_dashboard.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Make bar colors solid (remove rgba 0.7)
content = content.replace("rgba(0,212,170,0.7)", "'#00d4aa'")
content = content.replace("rgba(247,129,102,0.7)", "'#f78166'")
content = content.replace("rgba(227,179,65,0.7)", "'#e3b341'")
content = content.replace("rgba(129,140,248,0.7)", "'#818cf8'")
content = re.sub(r'backgroundColor:\s*\[([^\]]+)\]', lambda m: 'backgroundColor: [' + m.group(1).replace(',0.7)', ')').replace('rgba', 'rgb') + ']', content)

# 2. Fix dynamic array pioColors
content = content.replace(
    "const pioColors = pioScores.map(s => s >= 7 ? 'rgba(0,212,170,0.7)' : (s >= 5 ? 'rgba(227,179,65,0.7)' : 'rgba(247,129,102,0.7)'));",
    "const pioColors = pioScores.map(s => s >= 7 ? '#00d4aa' : (s >= 5 ? '#e3b341' : '#f78166'));"
)

# 3. Clean up bar rendering (sharp corners, nice spacing, no borders)
content = re.sub(
    r"borderColor:\s*'#[a-fA-F0-9]+',\s*borderWidth:\s*1,\s*borderSkipped:\s*'[^']+',\s*maxBarThickness:\s*\d+",
    "borderWidth: 0, barPercentage: 0.55, categoryPercentage: 0.8, borderRadius: 0",
    content
)

# Replace horizontal bar config
content = re.sub(
    r"borderColor:\s*pioBorders,\s*borderWidth:\s*1,\s*borderSkipped:\s*'start',\s*maxBarThickness:\s*20",
    "borderWidth: 0, barPercentage: 0.7, categoryPercentage: 0.9, borderRadius: 0",
    content
)

content = re.sub(
    r"borderColor:\s*'#[a-fA-F0-9]+',\s*borderWidth:\s*1,\s*borderSkipped:\s*'start',\s*maxBarThickness:\s*20",
    "borderWidth: 0, barPercentage: 0.7, categoryPercentage: 0.9, borderRadius: 0",
    content
)

# 4. Enhance chart-explain texts to fill the empty space below nicely
# Replace Valuation text in export_company
content = content.replace(
    '<div class="chart-explain">\n                    <strong>P/E</strong> = price per ₹1 of earnings (lower = cheaper). <strong>P/B</strong> = price vs book value of assets. <strong>EV/EBITDA</strong> = enterprise value per unit of operating profit. Dashed lines show typical fair-value benchmarks — bars below the line suggest the stock may be undervalued.\n                </div>',
    '<div class="chart-explain">\n                    <div style="font-weight:600;margin-bottom:0.5rem;color:#e5e5e5;">What this means:</div>\n                    <div style="display:grid;gap:0.5rem;line-height:1.5;">\n                        <div><strong style="color:var(--teal)">P/E Ratio</strong>: Shows how much investors are paying for ₹1 of earnings. Values under 20 (dashed line) often indicate a bargain.</div>\n                        <div><strong style="color:var(--teal)">P/B Ratio</strong>: Compares market value to the company\'s actual assets. Lower bars represent cheaper valuations.</div>\n                        <div><strong style="color:var(--teal)">EV/EBITDA</strong>: A pure measure of value that includes debt. Values below 10 are generally considered attractive.</div>\n                    </div>\n                </div>'
)

# Replace Growth text in export_company
content = content.replace(
    '<div class="chart-explain">\n                    <strong>Rev CAGR</strong> = average annual revenue growth over 3 years. <strong>PAT CAGR</strong> = profit-after-tax growth rate. <strong>FCF Yield</strong> = free cash flow as a % of market cap. Green bars = positive growth, red = declining. Higher is better for all three.\n                </div>',
    '<div class="chart-explain">\n                    <div style="font-weight:600;margin-bottom:0.5rem;color:#e5e5e5;">What this means:</div>\n                    <div style="display:grid;gap:0.5rem;line-height:1.5;">\n                        <div><strong style="color:var(--indigo)">Revenue & PAT CAGR</strong>: The average yearly growth in sales and profits over the last 3 years. Consistent green bars indicate a thriving, expanding business.</div>\n                        <div><strong style="color:var(--indigo)">FCF Yield</strong>: Shows how efficiently the company turns its market cap into hard cash. High values mean the company generates excess cash to reinvest or return to shareholders.</div>\n                    </div>\n                </div>'
)

# 5. Fix layout heights and add missing structural CSS enhancements
content = content.replace('height:200px;', 'height:220px;')
content = content.replace('height:260px;', 'height:280px;')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
