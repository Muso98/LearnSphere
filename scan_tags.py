import os
import re

def scan_templates(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Pattern for multi-line trans tag: {% trans [newline/space] "Asosiy sahifa"
                    if re.search(r'{%\s*trans\s*[\r\n]+', content):
                        print(f"Found multi-line trans tag in: {path}")
                        # Print context
                        matches = re.finditer(r'({%\s*trans\s*[\r\n]+[^%]+%})', content)
                        for m in matches:
                            print(f"  Match: {m.group(1)}")
                    
                    if "Asosiy sahifa" in content:
                        print(f"File contains 'Asosiy sahifa': {path}")

scan_templates(r'm:\LearnSphere\templates')
