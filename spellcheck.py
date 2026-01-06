from helpers import read_page, get_token_info2
import random
import spacy
from typing import List, Tuple, Dict, Any, Set, Optional


MIN_WORDS = 3
MAX_WORDS = 8
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"
MIN_WORD_LENGTH_FOR_TYPO = 5

def swap_adjacent_letters(word: str) -> str:
    word = list(word)
    
    if len(word) < 2:
        return "".join(word)
        
    swap_index = random.randint(0, len(word) - 2)
    word[swap_index], word[swap_index + 1] = word[swap_index + 1], word[swap_index]
    return "".join(word)


def change_u(word: str) -> str:
    replacements = {'u': 'ó', 'ó': 'u', 'U': 'Ó', 'Ó': 'U'}
    indices = [i for i, char in enumerate(word) if char.lower() in 'uó']
    
    if not indices:
        return word
        
    char_index = random.choice(indices)
    original_char = word[char_index]
    
    return word[:char_index] + replacements[original_char] + word[char_index+1:]


def change_rz(word: str) -> str:
    replacements = {'rz': 'ż', 'ż': 'rz', 'Rz': 'Ż', 'Ż': 'Rz', 'RZ': 'Ż', 'Ż': 'RZ'}
    
    for original, replacement in replacements.items():
        if original in word:
            start_index = word.find(original)
            
            if len(original) == 2:
                
                return word[:start_index] + replacement + word[start_index + 2:]
            elif len(original) == 1:
                
                return word[:start_index] + replacement + word[start_index + 1:]
                
    return word


def generate_typo_distractor(correct_word: str) -> str:
    word = correct_word
    has_u_o = any(c in word.lower() for c in 'uó')
    has_rz_z = any(sub in word.lower() for sub in ['rz', 'ż'])
    
    if len(word) < MIN_WORD_LENGTH_FOR_TYPO:
        return swap_adjacent_letters(word)

    if not has_u_o and not has_rz_z:
        return swap_adjacent_letters(word)

    if has_u_o != has_rz_z:
        roll = random.random()
        
        if roll < 0.5: 
            return swap_adjacent_letters(word)
        elif has_u_o:
            return change_u(word)
        else: 
            return change_rz(word)

    if has_u_o and has_rz_z:
        roll = random.random()
        
        if roll < 0.2:
            return swap_adjacent_letters(word)
        elif roll < 0.6: 
            return change_u(word)
        else: 
            return change_rz(word)
            
    return swap_adjacent_letters(word)


def generate_riddle(page: str) -> Tuple[str, List[Tuple[str, str]]]:
    word_tokens = get_token_info2(page) 
    
    maskable_tokens = [t for t in word_tokens if len(t.original_text) >= MIN_WORD_LENGTH_FOR_TYPO]
    
    riddle_words_data: List[Tuple[str, str]] = []
    
    if not maskable_tokens:
        return page, riddle_words_data

    max_to_mask = min(len(maskable_tokens), MAX_WORDS)
    words_count = random.randint(MIN_WORDS, max_to_mask)
    
    tokens_to_mask = random.sample(maskable_tokens, words_count)
    
    replacements = [] 
    
    for token_info in tokens_to_mask:
        correct_word = token_info.original_text
        if len(correct_word)<2:
            continue
        typo_to_insert = generate_typo_distractor(correct_word)
        
        while typo_to_insert == correct_word:
            typo_to_insert = generate_typo_distractor(correct_word)
        
        
        start = token_info.start
        end = token_info.finish
        riddle_words_data.append((correct_word, typo_to_insert, start))
        
        replacement = f"{COLOR_START}{typo_to_insert}{COLOR_RESET}"
        replacements.append((start, end, replacement))

    replacements.sort(key=lambda x: x[0], reverse=True)
    riddle_words_data.sort(key=lambda x: x[2])
    riddle_words_data = [(original, typo) for original, typo, _ in riddle_words_data]
    masked_page = page
    
    for start, end, replacement in replacements:
        masked_page = masked_page[:start] + replacement + masked_page[end:]
        
    return masked_page, riddle_words_data


def generate_level(extract_path: str) -> List[Tuple[str, List[Tuple[str, str]]]]:
    pages_and_words = []
    count = 1
    
    while True:
        page_content = read_page(extract_path, count)
        if not page_content:
            break
        
        masked_page, riddle_words_data = generate_riddle(page_content) 
        pages_and_words.append((masked_page, riddle_words_data))
        count += 1
        
    return pages_and_words
if __name__=="__main__":
    extract_file_path = "extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt"
    pages_data = generate_level(extract_file_path)

    for page, riddle_data in pages_data:
        print("| NEXT PAGE |\n")
        print(page)
        print("\n")
        
        if not riddle_data:
            continue
            
        print("| Solutions |")
        
        for correct, typo in riddle_data:
            print(f"Typo: {typo} | Correct: {correct}")
        