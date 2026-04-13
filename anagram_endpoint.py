from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

from helpers import read_page, get_token_info_basic
from anagram import generate_riddle, transform_to_model

''' module responsible for endpoints for anagram riddles'''

class GameRequest(BaseModel):
    bookId: int
    gameType: str  
    chapter: int

class RiddleWord(BaseModel):
    id: str
    value: str

class GameText(BaseModel):
    words: List[RiddleWord]

class AnagramRiddle(BaseModel):
    prompt: GameText

class AnagramResponse(BaseModel):
    gameId: int
    riddle: AnagramRiddle

class AnagramAnswerRequest(BaseModel):
    type: str
    gameId: int
    selectedWordIds: List[str]
    elapsedTimeMs: Optional[int] = None

class ResultResponse(BaseModel):
    score: int
    mistakes: int
    time: str
    accuracy: float
    pagesCompleted: int

router = APIRouter(prefix="/games", tags=["anagram"])
active_games: Dict[int, Dict[str, Any]] = {}


def cleanup_expired_games():
    '''cleans up games older than 1h'''
    now = datetime.now()
    expired_ids = [
        gid for gid, data in active_games.items()
        if now - data["start_time"] > timedelta(hours=1)
    ]
    for gid in expired_ids:
        del active_games[gid]



@router.post("/anagram/start", response_model=List[AnagramResponse])
async def start_anagram_game(request: GameRequest, background_tasks: BackgroundTasks):
    '''posts the riddle'''
    background_tasks.add_task(cleanup_expired_games)
    if request.gameType != 'anagram':
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        responses = []
        all_correct_word_ids = set()
        page_to_ids = {}

        game_id = random.randint(1000, 9999)
        while (game_id in active_games):
            game_id = random.randint(1000, 9999)
        current_word_id = 1
        page_idx = 1

        while True:
            page_content = read_page(extract_path, page_idx)
            if not page_content:
                break
            
            anagrammed_page, masked_words = generate_riddle(page_content)
            if not masked_words:
                page_idx += 1
                continue

            tokens = get_token_info_basic(page_content)
            if not tokens:
                page_idx += 1
                continue

            masked_metadata = []
            for i, token in enumerate(tokens):
                for masked_word in masked_words:
                    if token.i == masked_word.i:
                        masked_metadata.append((i, masked_word))
                        break
            
            spellcheck_model, next_id, page_anagram_ids = transform_to_model(
                anagrammed_page,
                tokens,
                masked_metadata,
                current_word_id,
                game_id
            )
            
            page_all_word_ids = {w["id"] for w in spellcheck_model["riddle"]["prompt"]["words"]}
            page_to_ids[page_idx] = page_all_word_ids
            
            all_correct_word_ids.update(page_anagram_ids)
            current_word_id = next_id
            
            riddle_words = [RiddleWord(id=w["id"], value=w["value"]) for w in spellcheck_model["riddle"]["prompt"]["words"]]
            
            responses.append(AnagramResponse(
                gameId=game_id,
                riddle=AnagramRiddle(prompt=GameText(words=riddle_words))
            ))
            page_idx += 1

        if not responses:
            raise HTTPException(status_code=404, detail="Content not found")

        active_games[game_id] = {
            "correct_word_ids": all_correct_word_ids,
            "page_to_ids": page_to_ids,
            "start_time": datetime.now(),
            "total_pages": len(responses)
        }

        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anagram/submit", response_model=ResultResponse)
async def submit_anagram_answers(request: AnagramAnswerRequest):
    '''checks answers'''
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_data = active_games[request.gameId]
    correct_ids = game_data["correct_word_ids"]
    page_to_ids = game_data["page_to_ids"]
    submitted_ids = set(request.selectedWordIds)
    
    pages_with_activity = 0
    for p_idx, p_ids in page_to_ids.items():
        if any(sid in p_ids for sid in submitted_ids):
            pages_with_activity += 1
            
    hits = len(submitted_ids.intersection(correct_ids))
    misses = len(submitted_ids - correct_ids)
    unfound = len(correct_ids - submitted_ids)
    
    total_mistakes = misses + unfound
    accuracy = hits / len(correct_ids) if correct_ids else 0
    
    if request.elapsedTimeMs:
        seconds = request.elapsedTimeMs // 1000
    else:
        delta = datetime.now() - game_data["start_time"]
        seconds = int(delta.total_seconds())
        
    time_str = f"{seconds // 60:02d}:{seconds % 60:02d}"
    
    del active_games[request.gameId]
    
    return ResultResponse(
        score=int(accuracy * 100),
        mistakes=total_mistakes,
        time=time_str,
        accuracy=accuracy,
        pagesCompleted=pages_with_activity
    )

@router.get("/anagram/active")
async def get_active_anagram_games():
    '''list of active games, for testing purposes'''
    games_debug = {}
    for gid, data in active_games.items():
        games_debug[gid] = {
            "correct_count": len(data["correct_word_ids"]),
            "correct_ids": sorted(list(data["correct_word_ids"]), key=int),
            "start_time": data["start_time"].isoformat()
        }
    
    return {
        "active_games_count": len(active_games),
        "games": games_debug
    }