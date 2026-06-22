import os

files_to_update = [
    'pyproject.toml',
    'telmus/exporters/html_dashboard.py'
]

for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace('0.1.6', '0.1.7')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
print("Version bumped to 0.1.7")
