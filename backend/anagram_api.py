import uuid
from anagram import generate_riddle
from backend.game_store import create_game


def start_anagram_game(page_text: str):
    anagrammed_page, masked_tokens = generate_riddle(page_text)

    words = []
    correct_word_ids = set()

    masked_positions = set(
        (t.start, t.finish) for t in masked_tokens
    )

    cursor = 0
    for word in anagrammed_page.split():
        word_id = f"w_{uuid.uuid4().hex[:8]}"

        words.append({
            "id": word_id,
            "value": word
        })

        if "\033[91m" in word:
            correct_word_ids.add(word_id)

    game_id = create_game({
        "type": "anagram",
        "correct_word_ids": correct_word_ids
    })

    return {
        "gameId": game_id,
        "riddle": {
            "prompt": {
                "words": words
            }
        }
    }