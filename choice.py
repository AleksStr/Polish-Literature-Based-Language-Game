from helpers import read_page, get_token_info
import random
import spacy
from typing import List, Tuple, Dict, Any

MIN_WORDS = 3
MAX_WORDS = 8
COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"

def find_same_form_candidates(word_token: Dict[str, Any], all_tokens: List[Dict[str, Any]]) -> List[str]:
    correct_pos = word_token["pos"]
    correct_morph = word_token["morph"].to_dict()
    candidates = []

    for tok in all_tokens:
        if tok["text"] == word_token["text"]:
            continue
        if tok["pos"] != correct_pos:
            continue

        tok_morph = tok["morph"].to_dict()

        if correct_pos == "NOUN":
            if tok_morph.get("Case") == correct_morph.get("Case") and tok_morph.get("Number") == correct_morph.get("Number"):
                candidates.append(tok["text"])
                continue

        elif correct_pos == "VERB":
            features = ["Mood", "Tense", "Person", "Number", "Aspect"]
            shared = sum(1 for f in features if tok_morph.get(f) == correct_morph.get(f))
            if shared >= 2:
                candidates.append(tok["text"])
                continue

        elif correct_pos == "ADJ":
            if tok_morph.get("Case") == correct_morph.get("Case") and tok_morph.get("Number") == correct_morph.get("Number") and tok_morph.get("Gender") == correct_morph.get("Gender"):
                candidates.append(tok["text"])
                continue

        elif correct_pos == "ADV":
            candidates.append(tok["text"])
            continue

        else:
            candidates.append(tok["text"])

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
        replacements.append((tok["start"], tok["end"], f"{COLOR_START}[x]{COLOR_RESET}"))
        masked_tokens.append(tok)

    replacements.sort(key=lambda x: x[0], reverse=True)
    masked_page = page
    for start, end, repl in replacements:
        masked_page = masked_page[:start] + repl + masked_page[end:]

    return masked_page, masked_tokens

def generate_options_for_masked(masked_tokens: List[Dict[str, Any]], all_tokens: List[Dict[str, Any]]):
    out = {}
    for tok in masked_tokens:
        correct = tok["text"]
        candidates = find_same_form_candidates(tok, all_tokens)

        fillers = [t["text"] for t in all_tokens if t["text"] != correct]

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

pages_data = generate_level("extracts/Zwierciadlana zagadka/Zwierciadlana zagadka_part_1.txt")

for masked_page, masked_tokens, options in pages_data:
    print("| NEXT PAGE |\n")
    print(masked_page)
    print("\n| OPTIONS |")
    for tok in masked_tokens:
        w = tok["text"]
        print(f"{w}: {', '.join(options[w])}")
    print("\n")

