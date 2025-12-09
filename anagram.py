from helpers import read_page, get_token_info
import random
import spacy
from typing import List, Tuple, Dict, Any

MIN_WORDS = 3
MAX_WORDS = 8
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"


def get_anagram(word: str) -> str:
    original_letters = list(word)
    shuffled_letters = original_letters[:]
    anagram = word
    while anagram == word:
        random.shuffle(shuffled_letters)
        anagram = "".join(shuffled_letters)        
    
    return anagram

def generate_riddle(page: str) -> Tuple[str, List[str]]:
    word_tokens = get_token_info(page) 
    
    if not word_tokens:
        return page, []

    max_to_mask = min(len(word_tokens), MAX_WORDS)
    words_count = random.randint(MIN_WORDS, max_to_mask)
    
    token_indices_to_mask = random.sample(range(len(word_tokens)), words_count)
    
    selected_tokens_info = []
    
    for token_idx in token_indices_to_mask:
        token_info = word_tokens[token_idx]
        selected_tokens_info.append({
            'original_word': token_info['text'],
            'start': token_info['start'],
            'end': token_info['end']
        })
    
    selected_tokens_info.sort(key=lambda x: x['start'])
    
    replacements = [] 
    masked_words_in_order = []
    
    for info in selected_tokens_info:
        original_word = info['original_word']
        
        masked_words_in_order.append(original_word)
        
        replacement_text = get_anagram(original_word)
        
        start = info['start']
        end = info['end']
        
        replacement = f"{COLOR_START}{replacement_text}{COLOR_RESET}"
        
        replacements.append((start, end, replacement))

    replacements.sort(key=lambda x: x[0], reverse=True)
    
    anagrammed_page = page
    
    for start, end, replacement in replacements:
        anagrammed_page = anagrammed_page[:start] + replacement + anagrammed_page[end:]
        
    return anagrammed_page, masked_words_in_order

def generate_level(extract_path: str) -> List[Tuple[str, List[str]]]:
    pages_and_words = []
    count = 1
    while True:
        page_content = read_page(extract_path, count)
        if not page_content:
            break
        anagrammed_page, masked_words = generate_riddle(page_content) 
        pages_and_words.append((anagrammed_page, masked_words))
        count += 1
    return pages_and_words

pages_data = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")

for page, words in pages_data:
    print("\n| Next Page |\n")
    print(page)
    print("\n")
    
    print("| Solution |\n")
    print(", ".join(words))
    