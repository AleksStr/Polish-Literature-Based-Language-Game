from helpers import read_page, get_token_info_basic
import random
from typing import List, Tuple, Dict, Any
import uuid
import sys

MIN_WORDS = 3
MAX_WORDS = 5
''' This module handles logic for fill type riddles
It can be run as main passing relative path to extract as argument. then it will print a fill riddle in console

'''
FILE_PATH = "extracts/book_2/chapter_1.txt"
'''
#this can be uncommented to change color of [x] for printing
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"
'''
COLOR_START = ""
COLOR_RESET = ""

def pick_words_to_remove(word_tokens ,n):
    ''' picks random words that are different from each other'''
    words_to_remove = []
    tries = 0
    for i in range(n):
        random_word = random.choice(word_tokens)
        if random_word.original_text.lower() not in [w.original_text.lower() for w in words_to_remove]:
            words_to_remove.append(random_word)
        else:
            i -= 1
            tries += 1
        if tries == 5:
            break
    return words_to_remove

def generate_level(page: str, n_words: int = None):
    if n_words is None:
        n_words = random.randint(MIN_WORDS, MAX_WORDS)
    word_tokens_data = get_token_info_basic(page)
    if not word_tokens_data:
        return None, None
    
    word_tokens = [t for t in word_tokens_data]
    n = min(len(word_tokens), n_words)
    words_to_remove = pick_words_to_remove(word_tokens, n)
    return word_tokens, words_to_remove

def replace_word_token(page: str, word_token):
    ''' removes word and replaces it with red [x] in console output'''
    start = word_token.start
    end = word_token.finish
    replacement = f"{COLOR_START}[x]{COLOR_RESET}"
    page = page[:start] + replacement + page[end:]
    return page

def generate_riddle_for_printing(page:str, number_of_words_to_be_taken:int=5):
    '''
    chooses number of words to remove then calls function remove_words to remove them
    It is used for printing when running module as main, it is not used by frontend
    '''

    words_taken = []
    words_tokens, words_to_remove = generate_level(page, number_of_words_to_be_taken)
    words_to_remove.sort(key=lambda x:x.start,reverse=True)

    for word in words_to_remove:
        page = replace_word_token(page, word)
        words_taken.append(word)
    return page, words_taken

   
def generate_level_for_printing(extract_path: str) -> List[Tuple[str, List[str]]]:
    ''' repeats generate level for each page'''
    pages_and_words = []
    count = 1
    while True:
        page_content = read_page(extract_path, count)
        if not page_content:
            break
        riddle_page, riddle_words = generate_riddle_for_printing(page_content, random.randint(MIN_WORDS, MAX_WORDS)) 
        pages_and_words.append((riddle_page, riddle_words))
        count += 1
    return pages_and_words

def transform_to_fill_model(page_text: str, word_tokens: List, words_to_remove: List, game_id: int) -> Dict[str, Any]:
    ''' tranforms riddle to the form accepted by endpoints'''
    parts = []
    options = []
    
    words_to_remove.sort(key=lambda x: x.start)
    
    all_options_pool = [w.display_word for w in words_to_remove]
    random.shuffle(all_options_pool)

    label_to_option_id = {}
    for label in all_options_pool:
        opt_id = str(uuid.uuid4())
        label_to_option_id[label] = opt_id
        options.append({"id": opt_id, "label": label})

    last_idx = 0
    for word in words_to_remove:
        if word.start > last_idx:
            parts.append({
                "type": "text",
                "value": page_text[last_idx:word.start]
            })
        
        parts.append({
            "type": "gap",
            "value": "" 
        })
        last_idx = word.finish

    if last_idx < len(page_text):
        parts.append({
            "type": "text",
            "value": page_text[last_idx:]
        })

    return {
        "gameId": game_id,
        "riddle": {
            "prompt": {"parts": parts},
            "options": options
        }
    }


if __name__=="__main__":
    '''prints page as string, then prints options in random and correct order'''
    extract_file_path = FILE_PATH
    if len(sys.argv) > 1:
        extract_file_path = sys.argv[1]
    pages_data = generate_level_for_printing(extract_file_path)
    for page, words in pages_data:
        print("| NEXT PAGE |\n")
        print(page)
        print("\n")
        
        random_words = words[:] 
        random.shuffle(random_words)

        print("| Random Order|")
        print(", ".join(w.display_word for w in random_words))
        
        print("\n| Correct Order |")
        random_words.sort(key=lambda x: x.start)
        print(", ".join(w.display_word for w in random_words))
        print("\n")
    