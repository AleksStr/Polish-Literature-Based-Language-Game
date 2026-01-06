from helpers import read_page, get_token_info, is_punctuation
import random
from typing import List, Tuple, Dict, Any
import uuid
''' current version switches words WITH interpunction that is attached to them'''
MIN_PAIRS = 3
MAX_PAIRS = 6
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"

def switch_word_riddle(page, swapped_word):
    # Main function to swap words in a random line
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

    valid_pairs = get_valid_word_pairs(words)
    if not valid_pairs:
        return page

    swap_index = select_swap_index(valid_pairs, line_index, swapped_word)
    if swap_index is None:
        return ("\n".join(lines), (line_index, swap_index))

    new_line = swap_and_color_words(words, swap_index)
    lines[line_index] = new_line
    
    return ("\n".join(lines), (line_index, swap_index))


def get_valid_word_pairs(words):
    # Find valid consecutive word pairs
    valid_pairs = []
    for i in range(len(words) - 1):
        if words[i].strip() and words[i+1].strip() and not is_punctuation(words[i].strip()) and not is_punctuation(words[i+1].strip()) and words[i] != words[i+1]:
            valid_pairs.append(i)
    return valid_pairs


def select_swap_index(valid_pairs, line_index, swapped_word):
    # Pick index avoiding recent swaps
    if not valid_pairs:
        return None

    swap_index = random.choice(valid_pairs)
    tries_counter = 5
    
    while (line_index, swap_index) in swapped_word or (line_index, swap_index+1) in swapped_word or (line_index, swap_index-1) in swapped_word:
        swap_index = random.choice(valid_pairs)
        tries_counter -= 1
        if tries_counter < 0:
            return None
    
    return swap_index


def swap_and_color_words(words, swap_index):
    # Swap two words and apply colors
    word1 = words[swap_index]
    word2 = words[swap_index + 1]

    colored_word1 = COLOR_START + word1 + COLOR_RESET
    colored_word2 = COLOR_START + word2 + COLOR_RESET

    words[swap_index] = colored_word2
    words[swap_index + 1] = colored_word1
    
    return ' '.join(words)


def generate_riddle(page):
    word_count = random.randint(MIN_PAIRS, MAX_PAIRS)
    riddle = page
    swapped_words = []
    for i in range(0,word_count):
        riddle_text, (line_index, swap_index) = switch_word_riddle(riddle, swapped_words)
        swapped_words.append((line_index, swap_index))  
        riddle = riddle_text  
    return riddle_text


def generate_level(extract_path):
    pages = []
    count = 1
    while read_page(extract_path, count):
        pages.append(generate_riddle(read_page(extract_path, count)))
        count += 1
    return pages



if __name__ == "__main__":
    pages = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")
    for page in pages:
        print("| NEXT PAGE |\n")
        print(page)
        print("\n")