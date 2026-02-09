import os
import re

file_path = r'm:\LearnSphere\templates\administration\partials\shop_management.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define patterns to fix
# Pattern 1: {% trans "Bekor qilish" [newline] %}
content = re.sub(r'{%\s*trans\s*"Bekor qilish"\s*%}', '{% trans "Bekor qilish" %}', content)

# Pattern 2: {% trans "Saqlash" [newline] %}
content = re.sub(r'{%\s*trans\s*"Saqlash"\s*%}', '{% trans "Saqlash" %}', content)

# General fix for any broken trans tag with specific indentation usually found in this file
content = re.sub(r'{%\s*trans\s*"([^"]+)"\s*%}', r'{% trans "\1" %}', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed template tags in {file_path}")
