import random
import os
from helpers import read_page
MIN_EXTRA_LINES = 2
MAX_EXTRA_LINES = 5
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"

def check_if_allowed(extract_path):
    folder = os.path.dirname(extract_path)
    contents = os.listdir(folder)
    if len(contents) == 1:
        print(f"Only one item: {contents[0]}")
        return 0
    return 1

def put_extra_line(page, extra):    
    lines = page.split("\n")
    if extra.strip() in page:
        print("Warning: This line exist on this page")
        return page
    if lines and lines[-1] == '':
        lines.pop()

    extra_index = random.randint(0, len(lines))
    colored_extra = COLOR_START + extra.strip() + COLOR_RESET
    
    lines.insert(extra_index, colored_extra)
    
    return "\n".join(lines)


def get_random_line_from_extract(extra_extract_path):
    with open(extra_extract_path, 'r', encoding='utf-8') as extra_extract_file:
        extra_line=""
        lines = extra_extract_file.readlines()
        while(extra_line.strip()=="" or "| Page " in extra_line):
            extra_line =random.choice(lines)
    return extra_line

def get_random_extract(extract_path):
    folder = os.path.dirname(extract_path)
    random_extract = extract_path
    while random_extract == extract_path:
        random_extract = random.choice(os.listdir(folder)) 
    return os.path.join(folder, random_extract)

def generate_riddle(page, extract_path):
    if not check_if_allowed:
        return 0
    extra_count = random.randint(MIN_EXTRA_LINES, MAX_EXTRA_LINES)
    riddle = page
    for i in range(0,extra_count):
        random_path = get_random_extract(extract_path)
        extra_line = get_random_line_from_extract(random_path) 
        
        riddle = put_extra_line(riddle, extra_line)
    return riddle

def generate_level(extract_path):
    pages = []
    count = 1
    while read_page(extract_path, count):
        pages.append(generate_riddle(read_page(extract_path, count), extract_path))
        count += 1
    return pages


if __name__ == "__main__":
    pages = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")
    for page in pages:
        print("| NEXT PAGE |\n")
        print(page)
        print("\n")