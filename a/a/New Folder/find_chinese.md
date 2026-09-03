import os, re
for root, _, files in os.walk('src/flask_exts'):
    for f in sorted(files):
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fh:
                lines = fh.readlines()
            found = False
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if re.search(r'^[#"]', s) and re.search(r'[\u4e00-\u9fff]', s):
                    found = True
                    print(f'{path}:{i}:{s[:200]}')
            if found:
                print('---')