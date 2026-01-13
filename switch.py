from helpers import read_page, is_punctuation
import random
from typing import List, Tuple, Dict, Any

MIN_PAIRS = 3
MAX_PAIRS = 3

COLOR_START = ""
COLOR_RESET = ""

def merge_parts_with_punctuation(parts: List[str]) -> List[str]:
    merged = []
    buffer = ""
    for p in parts:
        if is_punctuation(p) or p in ["—", "-", "–"]:
            buffer += p + " "
        else:
            merged.append(buffer + p)
            buffer = ""
    if buffer:
        if merged:
            merged[-1] = merged[-1] + " " + buffer.strip()
        else:
            merged.append(buffer.strip())
    return merged

def switch_word_riddle(page, swapped_word):
    lines = page.split("\n")
    content_lines_indices = [i for i, line in enumerate(lines) if line.strip()]
    
    if not content_lines_indices:
        return page, (None, None)

    line_index = random.choice(content_lines_indices)
    original_line = lines[line_index]
    
    parts = [p for p in original_line.split(' ') if p]
    words = merge_parts_with_punctuation(parts)
    
    if len(words) < 2:
        return page, (None, None)

    valid_pairs = []
    for i in range(len(words) - 1):
        if words[i] != words[i+1]:
            valid_pairs.append(i)

    if not valid_pairs:
        return page, (None, None)

    swap_index = select_swap_index(valid_pairs, line_index, swapped_word)
    if swap_index is None:
        return page, (None, None)

    word1, word2 = words[swap_index], words[swap_index + 1]
    words[swap_index], words[swap_index + 1] = word2, word1
    
    lines[line_index] = ' '.join(words)
    return "\n".join(lines), (line_index, swap_index)

def select_swap_index(valid_pairs, line_index, swapped_word):
    if not valid_pairs:
        return None
    
    random.shuffle(valid_pairs)
    for idx in valid_pairs:
        if (line_index, idx) not in swapped_word and \
           (line_index, idx+1) not in swapped_word and \
           (line_index, idx-1) not in swapped_word:
            return idx
    return None

def generate_riddle(page):
    riddle = page
    swapped_words = []
    for _ in range(MIN_PAIRS):
        riddle_text, coords = switch_word_riddle(riddle, swapped_words)
        if coords[0] is not None:
            swapped_words.append(coords)
            riddle = riddle_text
    return riddle

def generate_level(extract_path):
    pages = []
    count = 1
    while True:
        content = read_page(extract_path, count)
        if not content:
            break
        pages.append(generate_riddle(content))
        count += 1
    return pages

def transform_to_switch_model(page_content: str, word_tokens: List, starting_id: int) -> Dict[str, Any]:
    riddle_text = generate_riddle(page_content)
    
    og_lines = page_content.split('\n')
    rid_lines = riddle_text.split('\n')
    
    words_data = []
    swapped_ids = set()
    current_id = starting_id
    
    for line_idx, (og_line, rid_line) in enumerate(zip(og_lines, rid_lines)):
        og_parts = merge_parts_with_punctuation([p for p in og_line.split(' ') if p])
        rid_parts = merge_parts_with_punctuation([p for p in rid_line.split(' ') if p])
        
        count = max(len(og_parts), len(rid_parts))
        for i in range(count):
            o_val = og_parts[i] if i < len(og_parts) else ""
            r_val = rid_parts[i] if i < len(rid_parts) else ""
            
            if not r_val and not o_val:
                continue
            
            word_id = str(current_id)
            is_last = line_idx < len(rid_lines) - 1 and i == count - 1
            display_val = r_val + '\n' if is_last else r_val
            
            words_data.append({"id": word_id, "value": display_val})
            if o_val != r_val:
                swapped_ids.add(word_id)
            current_id += 1
            
    return {
        "words": words_data,
        "swapped_ids": swapped_ids,
        "next_id": current_id
    }

if __name__ == "__main__":
    pages = generate_level("extracts/book_2/chapter_1.txt")
    for page in pages:
        print("| NEXT PAGE |\n")
        print(page)
        print("\n")