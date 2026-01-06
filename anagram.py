from helpers import read_page, get_token_info2
import random
import spacy
from word_token import Word_Token
from typing import List, Tuple, Dict, Any

MIN_WORDS = 3
MAX_WORDS = 8
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"


def get_anagram(word: str) -> str:
    if len(word) <= 1:
        return word
    
    original_letters = list(word)
    shuffled_letters = original_letters[:]
    anagram = word
    
    max_attempts = 100  
    attempts = 0
    
    while anagram == word and attempts < max_attempts:
        random.shuffle(shuffled_letters)
        anagram = "".join(shuffled_letters)
        attempts += 1
    
    return anagram.lower()

def generate_riddle(page: str):
    word_tokens = get_token_info2(page) 
    
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

if __name__ == "__main__":
    pages, words = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")
    
    for page, word_list in zip(pages, words):
        print("\n| Next Page |\n")
        print(page)
        print("\n")
        
        display_texts = [w.display_word for w in word_list]
        
        print("| Solution |\n")
        print(", ".join(display_texts))
    