import random
from helpers import read_page

MIN_PAIRS = 3
MAX_PAIRS = 6
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"

def switch_word_riddle(page):
    lines = page.split("\n")
    if not lines or all(not line.strip() for line in lines):
        return page

    content_lines_indices = [i for i, line in enumerate(lines) if line.strip()]

    if not content_lines_indices:
        return page

    line_index = random.choice(content_lines_indices)
    original_line = lines[line_index]
    
    words = original_line.split(' ')
    
    if len(words) < 2:
        return page

    swap_index = -1
    for i in range(len(words) - 1):
        if words[i].strip() and words[i+1].strip():
            swap_index = i
            break
            
    valid_pairs = []
    for i in range(len(words) - 1):
        if words[i].strip() and words[i+1].strip():
            valid_pairs.append(i)

    if not valid_pairs:
        return page

    swap_index = random.choice(valid_pairs)
    
    word1 = words[swap_index]
    word2 = words[swap_index + 1]

    colored_word1 = COLOR_START + word1 + COLOR_RESET
    colored_word2 = COLOR_START + word2 + COLOR_RESET

    words[swap_index] = colored_word2
    words[swap_index + 1] = colored_word1
    
    new_line = ' '.join(words)
    
    lines[line_index] = new_line
    
    return "\n".join(lines)


def generate_riddle(page):
    word_count = random.randint(MIN_PAIRS, MAX_PAIRS)
    riddle = page
    for i in range(0,word_count):
        riddle = switch_word_riddle(riddle)
    return riddle


def generate_level(extract_path):
    pages = []
    count = 1
    while read_page(extract_path, count):
        pages.append(generate_riddle(read_page(extract_path, count)))
        count += 1
    return pages

pages = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")
for page in pages:
    print("| NEXT PAGE |\n")
    print(page)
    print("\n")