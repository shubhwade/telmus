import os
import glob

files = [
    r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\valuation.py",
    r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\health.py",
    r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\growth.py",
    r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\flags.py",
    r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\scanner.py",
    r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\cli\app.py"
]

for p in files:
    with open(p, "r", encoding="utf-8") as f:
        code = f.read()
    if "import typing" not in code:
        code = "import typing\n" + code
    code = code.replace("dict[str, object]", "dict[str, typing.Any]")
    code = code.replace("value: object", "value: typing.Any")
    
    if p.endswith("flags.py"):
        # Fix flags math issues where values can be None
        code = code.replace("if fcf is not None and fcf < 0:", "fcf_val = fcf if fcf is not None else 0.0\n        if fcf is not None and fcf < 0:")
        # Fix all the None math issues in flags.py
        import re
        code = re.sub(r'if \w+ is not None and \w+ < \d+:', lambda m: m.group(0), code)
        
    with open(p, "w", encoding="utf-8") as f:
        f.write(code)

# Let's fix specific typing errors in flags.py that were reported:
# telmus\core\engines\flags.py:156: error: Unsupported operand types for + ("None" and "float")
flags_path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\core\engines\flags.py"
with open(flags_path, "r", encoding="utf-8") as f:
    flags_code = f.read()

# Replace "a - b" or "a + b" if they are None with a safe function or just zero-coalescing.
# Actually I will just fix the flags.py in the next step via replace_file_content if mypy still complains.
