import os

path = "telmus/exporters/html_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix DOMContentLoaded opening
content = content.replace("document.addEventListener('DOMContentLoaded', function() {", "document.addEventListener('DOMContentLoaded', function() {{")

# Fix DOMContentLoaded closing
# It might look like:
#         });
#     </script>
content = content.replace("        });\n    </script>", "        }});\n    </script>")
content = content.replace("        });\n        });\n    </script>", "        }});\n        }});\n    </script>")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed f-string braces in html_dashboard.py")
