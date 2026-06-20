import re

path = "telmus/exporters/html_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find all blocks between <script> and </script>
scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)

for i, script in enumerate(scripts):
    print(f"Script block {i}:")
    # Find all {var} patterns but ignore {{ and }}
    # A single { followed by non-brace characters and then }
    vars_injected = re.findall(r'(?<!\{)\{([a-zA-Z0-9_.]+)\}(?!\})', script)
    vars_injected += re.findall(r'json\.dumps\(([a-zA-Z0-9_.]+)\)', script)
    
    # Also find {json.dumps(var)} or similar
    
    # Deduplicate and print
    vars_injected = list(set(vars_injected))
    for v in vars_injected:
        print(f"  - {v}")
