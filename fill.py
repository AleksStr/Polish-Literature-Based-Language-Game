from helpers import read_page, get_token_info
import random
import spacy
from typing import List, Tuple, Dict, Any

MIN_WORDS = 3
MAX_WORDS = 8
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"

def generate_riddle(page: str) -> Tuple[str, List[str]]:
    word_tokens = get_token_info(page) 
    masked_words = []
    
    if not word_tokens:
        return page, masked_words

    max_to_mask = min(len(word_tokens), MAX_WORDS)
    words_count = random.randint(MIN_WORDS, max_to_mask)
    
    token_indices_to_mask = random.sample(range(len(word_tokens)), words_count)
    
    replacements = [] 
    
    for token_idx in token_indices_to_mask:
        token_info = word_tokens[token_idx]
        
        masked_words.append(token_info['text'])
        
        start = token_info['start']
        end = token_info['end']
        replacement = f"{COLOR_START}[x]{COLOR_RESET}"
        replacements.append((start, end, replacement))

    replacements.sort(key=lambda x: x[0], reverse=True)
    
    masked_page = page
    
    for start, end, replacement in replacements:
        masked_page = masked_page[:start] + replacement + masked_page[end:]
        
    return masked_page, masked_words

def generate_level(extract_path: str) -> List[Tuple[str, List[str]]]:
    pages_and_words = []
    count = 1
    while True:
        page_content = read_page(extract_path, count)
        if not page_content:
            break
        masked_page, masked_words = generate_riddle(page_content) 
        pages_and_words.append((masked_page, masked_words))
        count += 1
    return pages_and_words

pages_data = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")

for page, words in pages_data:
    print("| NEXT PAGE |\n")
    print(page)
    print("\n")
    
    random_words = words[:] 
    random.shuffle(random_words)
    
    correct_words = sorted(words)
    
    print("| Random Order|")
    print(", ".join(random_words))
    
    print("\n| Corect Order |")
    print(", ".join(correct_words))