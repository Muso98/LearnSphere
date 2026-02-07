import re

# Read the file
with open('core/templates/core/director_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all split template tags using regex
# 1. Fix {{ t.grade_count|default:0 }} ta baho
content = re.sub(
    r'<span\s+class="badge bg-primary[^>]+>\{\{\s*t\.grade_count\|default:0\s*\}\}\s*ta baho</span>',
    '<span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-3 py-2 border border-primary border-opacity-25">{{ t.grade_count|default:0 }} ta baho</span>',
    content,
    flags=re.DOTALL
)

# 2. Fix 5 (A'lo) badge
content = re.sub(
    r'<span\s+class="badge bg-success[^>]+>5\s+\(A\'lo\)</span>',
    '<span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 rounded-pill px-3">5 (A\'lo)</span>',
    content,
    flags=re.DOTALL
)

# 3. Fix 4 (Yaxshi) badge
content = re.sub(
    r'<span\s+class="badge bg-info[^>]+>4\s+\(Yaxshi\)</span>',
    '<span class="badge bg-info bg-opacity-10 text-info border border-info border-opacity-25 rounded-pill px-3">4 (Yaxshi)</span>',
    content,
    flags=re.DOTALL
)

# 4. Fix {% firstof grade.value "N/A" %}
content = re.sub(
    r'<span\s+class="badge bg-warning[^>]+>\{%\s*firstof\s+grade\.value\s+"N/A"\s*%\}</span>',
    '<span class="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-25 rounded-pill px-3">{% firstof grade.value "N/A" %}</span>',
    content,
    flags=re.DOTALL
)

# 5. Fix teacher names
content = re.sub(
    r'<td class="pe-4 text-muted small">\{%\s*firstof\s+grade\.teacher\.first_name\s+""\s*%\}\s*\{%\s*firstof\s+grade\.teacher\.last_name\s+""\s*%\}</td>',
    '<td class="pe-4 text-muted small">{% firstof grade.teacher.first_name "" %} {% firstof grade.teacher.last_name "" %}</td>',
    content,
    flags=re.DOTALL
)

# Write back
with open('core/templates/core/director_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Template fixed successfully!")
