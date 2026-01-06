from fastapi import FastAPI
from backend.anagram_api import start_anagram_game

app = FastAPI()

BASE_TEXT = """Litwo, Ojczyzno moja! ty jesteś jak zdrowie;
Ile cię trzeba cenić, ten tylko się dowie,
Kto cię stracił. Dziś piękność twą w całej ozdobie
Widzę i opisuję, bo tęsknię po tobie."""
@app.post("/game/start")
def start_game(req: dict):
    if req["gameType"] == "anagram":
        return start_anagram_game(BASE_TEXT)

    raise ValueError("Unsupported game type")

from backend.game_store import GAMES

@app.post("/game/answer")
def submit_answer(req: dict):
    game = GAMES[req["gameId"]]

    selected = set(req.get("selectedWordIds", []))
    correct = game["correct_word_ids"]

    mistakes = len(selected - correct)
    score = max(0, 100 - mistakes * 20)

    return {
        "score": score,
        "mistakes": mistakes,
        "time": "00:45",
        "accuracy": score / 100,
        "pagesCompleted": 1
    }