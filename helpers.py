from typing import List, Tuple, Dict, Any
import spacy
try:
    NLP = spacy.load("pl_core_news_sm")
except OSError:
    spacy.cli.download("pl_core_news_sm")
    NLP = spacy.load("pl_core_news_sm")

def read_page(extract_path, page_index):
    with open(extract_path, 'r', encoding='utf-8') as extract_file:
        line = extract_file.readline()
        while (line.strip()!= f"| Page {page_index} |"):
            if not line:
                return None
            line = extract_file.readline()
        line = extract_file.readline()
        page = []
        while (line and line.strip()!= f"| Page {page_index+1} |"):
            page.append(line)
            line = extract_file.readline()
    page = "".join(page[1:-1])
    return page



def get_token_info(text: str) -> List[Dict[str, Any]]:
    doc = NLP(text)
    word_tokens = []
    for token in doc:
        word = token.text
        if not token.is_punct and not token.is_space and word.strip() and len(word) > 1:
            word_tokens.append({
                'text': word,
                'start': token.idx,
                'end': token.idx + len(word)
            })
    return word_tokens