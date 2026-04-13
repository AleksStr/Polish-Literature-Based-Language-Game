from helpers import read_page, get_token_info_basic
import random
import spacy
from word_token import Word_Token
from typing import List, Tuple, Dict, Any
import sys

'''This module handles anagram type riddles
Running as main results in the text of the riddle being printed in the console
Pass extract path (relative) as argument'''
FILE_PATH = "extracts/book_2/chapter_1.txt"
MIN_WORDS = 2
MAX_WORDS = 4

# this can be uncommented for visuals but would need to be commented again for code to run as app
'''
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"
'''
COLOR_START = ""
COLOR_RESET = ""

def get_anagram(word: str) -> str:
    ''' this function shuffles a word until an anagram is made'''
    if len(word) <= 1:
        return word
    upper = word[0].isupper()
    capslock = word[1].isupper()

    original_letters = list(word)
    shuffled_letters = original_letters[:]
    anagram = word
    
    max_attempts = 10 
    attempts = 0
    
    while anagram == word and attempts < max_attempts:
        random.shuffle(shuffled_letters)
        anagram = "".join(shuffled_letters)
        attempts += 1
    
    new_word = anagram.lower()
    if upper:
        new_word = anagram.capitalize()
    if capslock:
        new_word = anagram.upper()

    return new_word

def generate_riddle(page: str):
    ''' generates a single page of anagram riddle'''
    word_tokens = get_token_info_basic(page) 
    
    if not word_tokens:
        return page, []

    max_to_mask = min(len(word_tokens), MAX_WORDS)
    words_count = random.randint(MIN_WORDS, max_to_mask)
    
    token_indices_to_mask = random.sample(range(len(word_tokens)), words_count)
    
    selected_tokens_info = []
    
    for token_idx in token_indices_to_mask:
        token_info = word_tokens[token_idx]
        selected_tokens_info.append(token_info)

    
    selected_tokens_info.sort(key=lambda x: x.start)
    
    replacements = [] 
    masked_words_in_order = []
    
    for info in selected_tokens_info:
        original_word = info.original_text
        
        masked_words_in_order.append(info)
        
        replacement_text = get_anagram(original_word)
        
        start = info.start
        end = info.finish
        
        replacement = f"{COLOR_START}{replacement_text}{COLOR_RESET}"
        
        replacements.append((start, end, replacement))

    replacements.sort(key=lambda x: x[0], reverse=True)
    
    anagrammed_page = page
    
    for start, end, replacement in replacements:
        anagrammed_page = anagrammed_page[:start] + replacement + anagrammed_page[end:] 
    return anagrammed_page, masked_words_in_order

def generate_level(extract_path: str):
    ''' generates full riddle'''
    pages=[]
    words = []
    count = 1
    while True:
        page_content = read_page(extract_path, count)
        if not page_content:
            break
        anagrammed_page, masked_words = generate_riddle(page_content) 
        pages.append(anagrammed_page)
        words.append(masked_words)
        count += 1
    return pages, words


def transform_to_model(page_text: str, all_tokens: List, masked_metadata: List, start_id: int, game_id: int) -> Tuple[Dict[str, Any], int, List[str]]:
    ''' transform into model used by endpoints'''
    words_list = []
    current_id = start_id
    anagram_ids = []
    
    masked_starts = {m.start for _, m in masked_metadata}
    
    lines = page_text.split('\n')
    char_tracker = 0
    
    for line_idx, line in enumerate(lines):
        if not line and line_idx < len(lines) - 1:
            char_tracker += 1
            continue
            
        parts = line.split(' ')
        for part_idx, part in enumerate(parts):
            if not part:
                char_tracker += 1
                continue
            
            word_id = str(current_id)
            is_last_in_line = line_idx < len(lines) - 1 and part_idx == len(parts) - 1
            val = part + '\n' if is_last_in_line else part
            
            words_list.append({
                "id": word_id,
                "value": val
            })
            
            if char_tracker in masked_starts:
                anagram_ids.append(word_id)
            
            char_tracker += len(part) + 1
            current_id += 1
            
    return {
        "gameId": game_id,
        "riddle": {
            "prompt": {
                "words": words_list
            }
        }
    }, current_id, anagram_ids

if __name__ == "__main__":
    extract_file_path = FILE_PATH
    if len(sys.argv) > 1:
        extract_file_path = sys.argv[1]
    pages, words = generate_level(extract_file_path)
    
    for page, word_list in zip(pages, words):
        print("\n| Next Page |\n")
        print(page)
        print("\n")
        
        display_texts = [w.display_word for w in word_list]
        
        print("| Solution |\n")
        print(", ".join(display_texts))

