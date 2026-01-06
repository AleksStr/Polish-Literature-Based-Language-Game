import time

GAMES = {}
GAME_ID = 1000

def create_game(data: dict) -> int:
    global GAME_ID
    GAME_ID += 1
    data["created_at"] = time.time()
    GAMES[GAME_ID] = data
    return GAME_ID