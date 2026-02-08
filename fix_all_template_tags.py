#!/usr/bin/env python3
"""
Comprehensive fix for split Django template tags in all HTML files.
This script finds and consolidates multi-line {% trans %} and {{ }} tags.
"""

import os
import re
from pathlib import Path

def fix_split_tags(file_path):
    """Fix split template tags in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Fix split {% trans "..." %}
    # Matches {% trans "text spreading
    #                across lines" %}
    pattern1 = r'{%\s*trans\s+"([^"]*?)"\s*%}'
    content = re.sub(pattern1, lambda m: '{%% trans "%s" %%}' % m.group(1).replace('\n', ' ').strip(), content, flags=re.DOTALL)
    
    # Pattern 2: Fix split {% trans 'text' %}
    pattern2 = r"{%\s*trans\s+'([^']*?)'\s*%}"
    content = re.sub(pattern2, lambda m: "{%% trans '%s' %%}" % m.group(1).replace('\n', ' ').strip(), content, flags=re.DOTALL)
    
    # Pattern 3: Fix {{ variable }} split across lines
    pattern3 = r'{{\s*([^}]+?)\s*}}'
    content = re.sub(pattern3, lambda m: '{{ %s }}' % m.group(1).replace('\n', ' ').strip(), content, flags=re.DOTALL)
    
    # Pattern 4: Fix {% url %} tags
    pattern4 = r'{%\s*url\s+([^%]+?)\s*%}'
    content = re.sub(pattern4, lambda m: '{%% url %s %%}' % m.group(1).replace('\n', ' ').strip(), content, flags=re.DOTALL)
    
    # Pattern 5: Fix {% if %} tags
    pattern5 = r'{%\s*if\s+([^%]+?)\s*%}'
    content = re.sub(pattern5, lambda m: '{%% if %s %%}' % m.group(1).replace('\n', ' ').strip(), content, flags=re.DOTALL)
    
    # Pattern 6: Fix {% for %} tags
    pattern6 = r'{%\s*for\s+([^%]+?)\s*%}'
    content = re.sub(pattern6, lambda m: '{%% for %s %%}' % m.group(1).replace('\n', ' ').strip(), content, flags=re.DOTALL)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def find_and_fix_templates(root_dir):
    """Find all HTML templates and fix them"""
    templates_dir = Path(root_dir) / 'templates'
    fixed_files = []
    
    print(f"Searching for templates in: {templates_dir}")
    
    for html_file in templates_dir.rglob('*.html'):
        print(f"Checking: {html_file}")
        if fix_split_tags(html_file):
            fixed_files.append(html_file)
            print(f"  ✓ Fixed: {html_file}")
    
    return fixed_files

if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__))
    print("=" * 60)
    print("Django Template Tag Consolidation Script")
    print("=" * 60)
    
    fixed = find_and_fix_templates(root)
    
    print("\n" + "=" * 60)
    print(f"Summary: Fixed {len(fixed)} files")
    print("=" * 60)
    
    if fixed:
        print("\nFixed files:")
        for f in fixed:
            print(f"  - {f}")
    else:
        print("\nNo files needed fixing!")
