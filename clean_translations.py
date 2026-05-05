import os

def clean_po_file(lang):
    po_path = f'locale/{lang}/LC_MESSAGES/django.po'
    if not os.path.exists(po_path):
        print(f"Error: {po_path} not found!")
        return

    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by entries (separated by empty line)
    entries = content.split('\n\n')
    header = entries[0]
    
    seen_msgids = {}
    cleaned_entries = [header]

    for entry in entries[1:]:
        if not entry.strip():
            continue
        
        lines = entry.strip().split('\n')
        msgid = None
        msgstr = ""
        
        current_msgid_lines = []
        is_msgid = False
        is_msgstr = False
        
        for line in lines:
            if line.startswith('msgid "'):
                msgid = line[7:-1]
                is_msgid = True
                is_msgstr = False
            elif line.startswith('msgstr "'):
                msgstr = line[8:-1]
                is_msgid = False
                is_msgstr = True
            elif line.startswith('"') and is_msgid:
                msgid += line[1:-1]
            elif line.startswith('"') and is_msgstr:
                msgstr += line[1:-1]
        
        if msgid is not None:
            # If we already saw this msgid, keep the one with translation
            if msgid in seen_msgids:
                old_entry, old_msgstr = seen_msgids[msgid]
                if not old_msgstr and msgstr:
                    seen_msgids[msgid] = (entry, msgstr)
            else:
                seen_msgids[msgid] = (entry, msgstr)

    # Reconstruct the file
    final_content = header + '\n\n' + '\n\n'.join([e[0] for e in seen_msgids.values()])
    
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Successfully cleaned {po_path}")

clean_po_file('ru')
clean_po_file('en')
clean_po_file('uz')
