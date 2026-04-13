from helpers import read_page, get_token_info_basic
import random
from typing import List, Tuple, Dict, Any
import re
import sys

''' 
Spellcheck module is responsible for generating spellcheck type riddles
Run as main to get plain text of spellcheck riddle in console from extract FILE_PATH
Extract path (relative) can be passed as argument

'''
MIN_WORDS = 5
MAX_WORDS = 5
FILE_PATH = "extracts/book_2/chapter_1.txt"

COLOR_START = ""
COLOR_RESET = ""
'''
#this is commented because in spellcheck words changed in text should be hidden, 
# this can be uncommented for visuals but would need to be commented again for code to run as app
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"
'''

MIN_WORD_LENGTH_FOR_TYPO = 3

def swap_adjacent_letters(word: str) -> str:
    ''' swaps places of a randomly chosen letter and the one directly behind it, 
    already considering words with double letters like for example"inny"'''
    word = list(word)
    if len(word) < 2:
        return "".join(word)
    old_word = "".join(word)
    new_word = "".join(word)
    while old_word==new_word:  
        swap_index = random.randint(0, len(word) - 2)
        word[swap_index], word[swap_index + 1] = word[swap_index + 1], word[swap_index]
        new_word = "".join(word)

        if len(set(word))==1:
            break
    return new_word


def change_u(word: str) -> str:
    ''' changes a randomly chosen u/ó into the other one'''
    replacements = {'u': 'ó', 'ó': 'u', 'U': 'Ó', 'Ó': 'U'}
    indices = [i for i, char in enumerate(word) if char.lower() in 'uó']
    
    if not indices:
        return word
        
    char_index = random.choice(indices)
    original_char = word[char_index]
    
    return word[:char_index] + replacements[original_char] + word[char_index+1:]


def change_rz(word: str) -> str:
    ''' changes a randomly chosen rz/ż into the other one'''
    replacements = {'rz': 'ż', 'ż': 'rz', 'Rz': 'Ż', 'Ż': 'Rz', 'RZ': 'Ż'}

    indices_rz = [m.start() for m in re.finditer('rz', word.lower())]
    indices_z = [m.start() for m in re.finditer('ż', word.lower())]
    indices = indices_rz + indices_z

    if not indices:
        return word
    
    char_index = random.choice(indices)
    original_char = word[char_index]
    if original_char.lower() == 'r':

        return word[:char_index] + replacements[word[char_index:(char_index+2)]] + word[char_index+2:]
    else:
        if original_char == "Ż" and word[char_index+1].isupper():
            return word[:char_index] + "RZ" + word[char_index+1:]
        else:
            return word[:char_index] + replacements[original_char] + word[char_index+1:]
        

def change_ch(word: str) -> str:
    ''' changes a randomly chosen ch/h into the other one'''
    replacements = {'ch': 'h', 'h': 'ch', 'Ch': 'H', 'H': 'Ch', 'CH': 'H'}

    indices_rz = [m.start() for m in re.finditer('ch', word.lower())]
    indices_z = [m.start() for m in re.finditer('h', word.lower())]
    indices = indices_rz + indices_z

    if not indices:
        return word
    
    char_index = random.choice(indices)
    original_char = word[char_index]
    if original_char.lower() == 'c':

        return word[:char_index] + replacements[word[char_index:(char_index+2)]] + word[char_index+2:]
    else:
        if original_char == "H" and word[char_index+1].isupper():
            return word[:char_index] + "CH" + word[char_index+1:]
        else:
            return word[:char_index] + replacements[original_char] + word[char_index+1:]


def generate_typo_distractor(correct_word: str) -> str:
    '''randomly chooses what type of type the word will have'''
    word_lower = correct_word.lower()
    
    if len(correct_word) < MIN_WORD_LENGTH_FOR_TYPO:
        return swap_adjacent_letters(correct_word)

    options = [swap_adjacent_letters]

    if any(c in word_lower for c in 'uó'):
        options.append(change_u)
    
    if any(sub in word_lower for sub in ['rz', 'ż']):
        options.append(change_rz)
        
    if any(sub in word_lower for sub in ['ch', 'h']):
        options.append(change_ch)

    chosen_transform = random.choice(options)
    
    return chosen_transform(correct_word)


def generate_riddle(page: str) -> Tuple[str, List[Tuple[str, str]]]:
    ''' this function generates a singular page of riddle'''
    word_tokens = get_token_info_basic(page) 
    
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
    ''' this function generates a full riddle of all the pages'''
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


def transform_to_spellcheck_model(page_text: str, all_tokens: List, typos_data: List[Tuple[str, str, int]], start_id: int, game_id: int) -> Tuple[Dict[str, Any], int, List[str]]:
    ''' this transforms the riddle into the form needed by the endpoint'''
    words_list = []
    current_id = start_id
    typo_ids = []
    
    typo_starts = {pos for _, _, pos in typos_data}
    
    current_pos = 0
    lines = page_text.split('\n')
    
    for line_idx, line in enumerate(lines):
        if not line and line_idx < len(lines) - 1:
            current_pos += 1
            continue
            
        parts = line.split(' ')
        for part_idx, part in enumerate(parts):
            if not part:
                current_pos += 1
                continue
            
            word_id = str(current_id)
            is_last_in_line = line_idx < len(lines) - 1 and part_idx == len(parts) - 1
            display_val = part + '\n' if is_last_in_line else part
            
            words_list.append({
                "id": word_id,
                "value": display_val
            })
            
            if current_pos in typo_starts:
                typo_ids.append(word_id)
            
            current_pos += len(part) + 1
            current_id += 1
            
    return {
        "gameId": game_id,
        "riddle": {
            "prompt": {
                "words": words_list
            }
        }
    }, current_id, typo_ids

if __name__=="__main__":
    extract_file_path = FILE_PATH
    if len(sys.argv) > 1:
        extract_file_path = sys.argv[1]
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
        