from helpers import read_page, get_token_info
import random
import spacy
from word_token_detailed import Word_Token_Detailed
from typing import List, Tuple, Dict, Any
import uuid

MIN_WORDS = 3
MAX_WORDS = 8
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"

def find_same_form_candidates(word_token: Dict[str, Any], all_tokens: List[Dict[str, Any]]) -> List[str]:
    correct_pos = word_token.pos
    correct_morph = word_token.morph.to_dict()
    candidates = []

    for tok in all_tokens:
        if tok.display_word == word_token.display_word:
            continue
        if tok.pos != correct_pos:
            continue
        if tok.display_word in candidates:
            continue

        tok_morph = tok.morph.to_dict()

        if correct_pos == "NOUN":
            if tok_morph.get("Case") == correct_morph.get("Case") and tok_morph.get("Number") == correct_morph.get("Number"):
                candidates.append(tok.display_word)
                continue

        elif correct_pos == "VERB":
            features = ["Mood", "Tense", "Person", "Number", "Aspect"]
            shared = sum(1 for f in features if tok_morph.get(f) == correct_morph.get(f))
            if shared >= 2:
                candidates.append(tok.display_word)
                continue

        elif correct_pos == "ADJ":
            if tok_morph.get("Case") == correct_morph.get("Case") and tok_morph.get("Number") == correct_morph.get("Number") and tok_morph.get("Gender") == correct_morph.get("Gender"):
                candidates.append(tok.display_word)
                continue

        elif correct_pos == "ADV":
            candidates.append(tok.display_word)
            continue

        else:
            candidates.append(tok.display_word)

    return list(set(candidates))

def generate_riddle(page: str) -> Tuple[str, List[Dict[str, Any]]]:
    word_tokens = get_token_info(page)
    if not word_tokens:
        return page, []

    max_to_mask = min(len(word_tokens), MAX_WORDS)
    words_count = random.randint(MIN_WORDS, max_to_mask)
    chosen_indices = random.sample(range(len(word_tokens)), words_count)

    masked_tokens = []
    replacements = []

    for idx in chosen_indices:
        tok = word_tokens[idx]
        replacements.append((tok.start, tok.finish, f"{COLOR_START}[x]{COLOR_RESET}"))
        masked_tokens.append(tok)

    replacements.sort(key=lambda x: x[0], reverse=True)
    masked_tokens.sort(key=lambda x: x.start)
    masked_page = page
    for start, end, repl in replacements:
        masked_page = masked_page[:start] + repl + masked_page[end:]

    return masked_page, masked_tokens

def generate_options_for_masked(masked_tokens: List[Dict[str, Any]], all_tokens: List[Dict[str, Any]]):
    out = {}
    for tok in masked_tokens:
        correct = tok.display_word
        candidates = find_same_form_candidates(tok, all_tokens)

        fillers = [t.display_word for t in all_tokens if t.display_word != correct]

        if len(candidates) < 2:
            wrong = random.sample(fillers, 2)
        else:
            wrong = random.sample(candidates, 2)

        opts = [correct] + wrong
        random.shuffle(opts)
        out[correct] = opts

    return out

def generate_level(path: str):
    pages_output = []
    count = 1
    while True:
        page = read_page(path, count)
        if not page:
            break

        masked_page, masked_tokens = generate_riddle(page)
        all_tokens = get_token_info(page)
        options = generate_options_for_masked(masked_tokens, all_tokens)

        pages_output.append((masked_page, masked_tokens, options))
        count += 1
    return pages_output

def transform_to_choice_model(page_text: str, all_tokens: List, masked_indices: set) -> Dict[str, Any]:
    parts = []
    gaps = []
    last_idx = 0
    
    sorted_tokens = sorted(all_tokens, key=lambda x: x.start)
    
    for i, tok in enumerate(sorted_tokens):
        if tok.start > last_idx:
            parts.append({
                "type": "text",
                "value": page_text[last_idx:tok.start]
            })
            
        if i in masked_indices:
            gap_id = str(uuid.uuid4())
            parts.append({
                "type": "gap",
                "gapId": gap_id
            })
            
            correct_val = tok.display_word
            candidates = find_same_form_candidates(tok, sorted_tokens)
            fillers = [t.display_word for t in sorted_tokens if t.display_word != correct_val]
            
            wrong = random.sample(candidates, min(len(candidates), 2))
            if len(wrong) < 2:
                extra = random.sample(fillers, 2 - len(wrong))
                wrong.extend(extra)
            
            options_list = []
            correct_option_id = ""
            
            all_choice_texts = [correct_val] + wrong
            random.shuffle(all_choice_texts)
            
            for text in all_choice_texts:
                opt_id = str(uuid.uuid4())
                options_list.append({"id": opt_id, "label": text})
                if text == correct_val:
                    correct_option_id = opt_id
            
            gaps.append({
                "id": gap_id,
                "correctOptionId": correct_option_id,
                "options": options_list
            })
        else:
            parts.append({
                "type": "text",
                "value": tok.original_text
            })
            
        last_idx = tok.finish

    if last_idx < len(page_text):
        parts.append({
            "type": "text",
            "value": page_text[last_idx:]
        })

    return {
        "id": str(uuid.uuid4()),
        "parts": parts,
        "gaps": gaps
    }


if __name__ == "__main__":
    pages_data = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")

    for masked_page, masked_tokens, options in pages_data:
        print("| NEXT PAGE |\n")
        print(masked_page)
        print("\n| OPTIONS |")
        for tok in masked_tokens:
            w = tok.display_word
            print(f"{w}: {', '.join(options[w])}")
        print("\n")

