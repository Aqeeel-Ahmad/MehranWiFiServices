import os

replacements = {
    "HAM 3 NETWORK": "HAM 3 NETWORK",
    "HAM 3 NETWORK": "HAM 3 NETWORK",
    "HAM 3 NETWORK": "HAM 3 NETWORK",
    "HAM 3 NETWORK": "HAM 3 NETWORK",
    "HAM 3": "HAM 3",
    "HAM 3": "HAM 3",
    "03452524086": "03452524086",
    "923452524086": "923452524086",
    "0345-2524086": "0345-2524086"
}

# Directories to search
dirs_to_search = ['apps', 'templates', 'static', 'mehran_wifi', '.']

# Extensions to process
valid_exts = {'.html', '.py', '.js', '.css', '.svg', '.json'}

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    # Do specific replacements first to avoid partial matches
    
    # Exclude certain things from being blindly replaced (like 'mehran_wifi', 'mehran_theme', 'admin@mehranwifi')
    # Actually, python replace runs sequentially. If we do exact phrases first, it's safer.
    
    # We will NOT replace 'mehran_wifi' or 'mehran_theme' or 'mehranwifi.com'
    # So we temporarily protect them
    protections = {
        "mehran_wifi": "mehran_wifi",
        "mehran_theme": "mehran_theme",
        "mehranwifi.com": "mehranwifi.com",
        "mehranwifi": "mehranwifi",
        "Mehran City": "Mehran City"
    }
    
    for k, v in protections.items():
        new_content = new_content.replace(k, v)
        
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    for k, v in protections.items():
        new_content = new_content.replace(v, k)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")

for d in dirs_to_search:
    if os.path.isfile(d):
        if d.endswith('.py') or d.endswith('.json'):
            replace_in_file(d)
        continue
    for root, _, files in os.walk(d):
        if 'env' in root or 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in valid_exts:
                replace_in_file(os.path.join(root, file))

print("Done")
