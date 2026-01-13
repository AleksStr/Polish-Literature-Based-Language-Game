import os

folder_path = 'extracts/book_10'
output_file = os.path.join(folder_path, 'all_lines.txt')

all_content = []

files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

files.sort(key=lambda x: os.path.getctime(os.path.join(folder_path, x)))

for filename in files:
    if filename == 'all_lines.txt':
        continue
        
    file_path = os.path.join(folder_path, filename)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = line.strip()
            if clean_line and '| Page' not in line:
                all_content.append(line)

with open(output_file, 'w', encoding='utf-8') as out_f:
    out_f.writelines(all_content)