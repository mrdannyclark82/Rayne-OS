import os

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Name replacements
        new_content = content.replace('Elara', 'Milla')
        new_content = new_content.replace('elara', 'milla')
        new_content = new_content.replace('ELARA', 'MILLA')
        
        # Theme replacements
        new_content = new_content.replace('emerald', 'cyan')
        new_content = new_content.replace('#10b981', '#38bdf8') # emerald to cyan
        new_content = new_content.replace('bg-gray-900', 'bg-[#0b0f19]')
        new_content = new_content.replace('bg-gray-800', 'bg-[#0f141e]')
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
    except Exception as e:
        print(f"Skipped {filepath}: {e}")

for root, dirs, files in os.walk('staging/Elara_Remillafied'):
    if 'node_modules' in root or 'dist' in root:
        continue
    for file in files:
        if file.endswith(('.ts', '.tsx', '.html', '.json', '.md', '.sh')):
            replace_in_file(os.path.join(root, file))
