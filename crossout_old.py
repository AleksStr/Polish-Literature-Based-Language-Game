import random
import os
from helpers import read_page
import sys
#THIS IS NOT THE VERSION IN USE
#THIS VERSION WORKED GREAT LOCALLY BUT CLOUD RUN COULDNT HANDLE OPENING SO MANY FILES
'''crossout module is responsble for generating crossout type riddles
This module can be run on its own by passing extract path (relative) as argument'''
FILE_PATH = "extracts/book_2/chapter_1.txt"

MIN_EXTRA_LINES = 1
MAX_EXTRA_LINES = 3
#the lines below can be uncommented for visual purposes but need to be commented again for the code to run as backend
'''

COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"
'''
COLOR_START = ""
COLOR_RESET = ""

def check_if_allowed(extract_path):
    '''this checks if there is more than one chapter of the book, 
    by assumption of the app this should never happen'''
    folder = os.path.dirname(extract_path)
    contents = os.listdir(folder)
    if len(contents) == 1:
        print(f"Only one item: {contents[0]}")
        return 0
    return 1

def put_extra_line(page, extra):  
    ''' puts "extra" line in random location on page'''  
    lines = page.split("\n")
    if lines and lines[-1] == '':
        lines.pop()

    extra_index = random.randint(0, len(lines))
    colored_extra = COLOR_START + extra.strip() + COLOR_RESET
    
    lines.insert(extra_index, colored_extra)
    
    return "\n".join(lines)


def get_random_line_from_extract(extra_extract_path):
    ''' gets a random line from extract'''
    with open(extra_extract_path, 'r', encoding='utf-8') as extra_extract_file:
        extra_line=""
        lines = extra_extract_file.readlines()
        while(extra_line.strip()=="" or "| Page " in extra_line):
            extra_line =random.choice(lines)
    return extra_line

def get_random_extract(extract_path):
    """gets a random extract, different from the current one"""
    folder = os.path.dirname(extract_path)
    random_extract = extract_path
    while random_extract == extract_path:
        random_extract = random.choice(os.listdir(folder)) 
    return os.path.join(folder, random_extract)


def generate_riddle(page, extract_path):
    '''generates a singular page of riddle'''
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
    '''generates riddle pages until the entire extract is finished'''
    pages = []
    count = 1
    while read_page(extract_path, count):
        pages.append(generate_riddle(read_page(extract_path, count), extract_path))
        count += 1
    return pages


def transform_to_crossout_model(riddle_text: str):
    '''transforms to model nedded by endpoint'''
    raw_lines = riddle_text.split("\n")
    return [line.strip() for line in raw_lines if line.strip()]


if __name__ == "__main__":
    extract_file_path = FILE_PATH
    if len(sys.argv) > 1:
        extract_file_path = sys.argv[1]
    pages = generate_level()
    for page in pages:
        print("| NEXT PAGE |\n")
        print(page)
        print("\n")