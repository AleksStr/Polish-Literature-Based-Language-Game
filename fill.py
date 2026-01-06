from helpers import read_page, get_token_info2
import random
from typing import List, Tuple, Dict, Any
import uuid

MIN_WORDS = 3
MAX_WORDS = 8
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"

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

def replace_word_token(page: str, word_token):
    ''' removes word and replaces it with red [x] in console output'''
    start = word_token.start
    end = word_token.finish
    replacement = f"{COLOR_START}[x]{COLOR_RESET}"
    page = page[:start] + replacement + page[end:]
    return page

def generate_riddle(page:str, number_of_words_to_be_taken:int=5):
    '''
    chooses number of words to remove then calls function remove_words to remove them
    '''
    word_tokens = get_token_info2(page) 
    words_taken = []
    if not word_tokens:
        raise ValueError("spacy error")
    n = min(len(word_tokens), number_of_words_to_be_taken)
    words_to_remove = pick_words_to_remove(word_tokens, n)
    words_to_remove.sort(key=lambda x:x.start,reverse=True)

    for word in words_to_remove:
        page = replace_word_token(page, word)
        words_taken.append(word)
    return page, words_taken

   
def generate_level(extract_path: str) -> List[Tuple[str, List[str]]]:
    ''' repeats generate level for each page'''
    pages_and_words = []
    count = 1
    while True:
        page_content = read_page(extract_path, count)
        if not page_content:
            break
        riddle_page, riddle_words = generate_riddle(page_content, random.randint(MIN_WORDS, MAX_WORDS)) 
        pages_and_words.append((riddle_page, riddle_words))
        count += 1
    return pages_and_words

def transform_to_fill_model(page_text: str, word_tokens: List, words_to_remove: List) -> Dict[str, Any]:
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
        "gameId": random.randint(1000, 9999),
        "riddle": {
            "prompt": {"parts": parts},
            "options": options
        }
    }


if __name__=="__main__":
    '''prints page as string, then prints options in random and correct order'''
    pages_data = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")
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
    