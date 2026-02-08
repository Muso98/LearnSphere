import os
import re
from pathlib import Path

def normalize_trans_tags(content):
    """
    Finds {% trans "..." %} tags and normalizes whitespace inside the string.
    Replaces newlines and multiple spaces with a single space.
    """
    # Pattern for double quotes: {% trans "..." %}
    def replace_double(match):
        text = match.group(1)
        # Replace newlines and multi-spaces with single space
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        return f'{{% trans "{cleaned_text}" %}}'

    content = re.sub(r'{%\s*trans\s+"([^"]*?)"\s*%}', replace_double, content, flags=re.DOTALL)

    # Pattern for single quotes: {% trans '...' %}
    def replace_single(match):
        text = match.group(1)
        # Replace newlines and multi-spaces with single space
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        return f"{{% trans '{cleaned_text}' %}}"

    content = re.sub(r"{%\s*trans\s+'([^']*?)'\s*%}", replace_single, content, flags=re.DOTALL)
    
    return content

def check_static_files_for_tags(root_dir):
    """Check if any .js or .css files in static/ contain {% %} tags"""
    static_dir = Path(root_dir) / 'static'
    if not static_dir.exists():
        return
        
    print(f"\nChecking static files for Django tags (which won't work there)...")
    for f in static_dir.rglob('*'):
        if f.suffix in ['.js', '.css']:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if '{% trans' in content or '{% url' in content:
                        print(f"⚠️  WARNING: Found Django tags in static file: {f}")
                        print("   Static files are not rendered by Django! Move this logic to a template.")
            except:
                pass

def process_templates(root_dir):
    templates_dir = Path(root_dir) / 'templates'
    print(f"Processing templates in {templates_dir}...")
    
    count = 0
    for html_file in templates_dir.rglob('*.html'):
        with open(html_file, 'r', encoding='utf-8') as f:
            original = f.read()
            
        fixed = normalize_trans_tags(original)
        
        if fixed != original:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(fixed)
            print(f"  ✓ Fixed whitespace in: {html_file.name}")
            count += 1
            
    print(f"Total files updated: {count}")

if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__))
    process_templates(root)
    check_static_files_for_tags(root)
