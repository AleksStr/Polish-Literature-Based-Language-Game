from typing import List, Tuple, Dict, Any
from word_token import Word_Token
from word_token_detailed import Word_Token_Detailed
import string
import spacy

COLOR_START = "\033[91m"
COLOR_RESET = "\033[0m"


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


def get_token_info(text):
    doc = NLP(text)
    word_tokens = []
    for token in doc:
        word = token.text
        if not token.is_punct and not token.is_space and word.strip() and len(word) > 1:
            word_tokens.append(Word_Token_Detailed(word, token.idx, token.idx+len(word), token.i, token.morph, token.pos))
    return word_tokens

def get_token_info2(text:str):
    doc = NLP(text)
    word_tokens = []
    for token in doc:
        word = token.text
        if not token.is_punct and not token.is_space and word.strip() and len(word) > 1:
            word_tokens.append(Word_Token(word, token.idx, token.idx+len(word), token.i))
    return word_tokens

def is_punctuation(text: str) -> bool:
    dash_chars = "-–—" 
    return bool(text) and all(char in string.punctuation + dash_chars for char in text)