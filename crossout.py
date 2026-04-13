
import random
import os
from helpers import read_page
import sys

MIN_EXTRA_LINES = 2
MAX_EXTRA_LINES = 2

'''This module handles generating riddles of crossout type
It uses special .txt files that hold all lines of a book
This module can be run in command line by passing relative path to extract as argument
'''
FILE_PATH = "extracts/book_2/chapter_1.txt"

def load_line_pool(extract_path):
    '''loads a file that has all the lines'''
    folder = os.path.dirname(extract_path)
    pool_path = os.path.join(folder, "all_lines.txt")
    
    if not os.path.exists(pool_path):
        return []
        
    with open(pool_path, 'r', encoding='utf-8') as f:
        pool = [line.strip() for line in f if line.strip() and "| Page " not in line]
    return pool

def get_lines_from_extract(extract_path):
    '''this gets all lines from this specific extract'''
    with open(extract_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and "| Page " not in line]
    return lines

def generate_riddle(page_content, extract_path):
    '''gets a random line and puts it in a random position'''
    line_pool = load_line_pool(extract_path)
    original_lines = [l.strip() for l in page_content.split("\n") if l.strip()]

    all_extract_lines = get_lines_from_extract(extract_path)
    filtered_pool = [l for l in line_pool if l not in all_extract_lines]
    
    if not filtered_pool or not original_lines:
        return page_content

    extra_count = random.randint(MIN_EXTRA_LINES, MAX_EXTRA_LINES)
    selected_extras = random.sample(filtered_pool, min(extra_count, len(filtered_pool)))

    
    riddle_lines = list(original_lines)
    
    for extra in selected_extras:
        insert_pos = random.randint(1, len(riddle_lines))
        riddle_lines.insert(insert_pos, extra)
        
    return "\n".join(riddle_lines)


def generate_level(extract_path):
    ''' this generates entire riddle'''
    pages = []
    count = 1
    while True:
        content = read_page(extract_path, count)
        if not content:
            break
        pages.append(generate_riddle(content, extract_path))
        count += 1
    return pages

def transform_to_crossout_model(riddle_text: str):
    if isinstance(riddle_text, list):
        return [line.strip() for line in riddle_text if line.strip()]
    return [line.strip() for line in riddle_text.split("\n") if line.strip()]

if __name__ == "__main__":
    path = FILE_PATH
    if len(sys.argv) > 1:
        path = sys.argv[1]
    pages = generate_level(path)
    for page in pages:
        print("| NEXT PAGE |\n")
        print(page)
        print("\n")