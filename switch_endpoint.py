from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

from helpers import read_page, get_token_info2
from switch import transform_to_switch_model

class GameRequest(BaseModel):
    bookId: int
    gameType: str
    chapter: int

class RiddleWord(BaseModel):
    id: str
    value: str

class GameText(BaseModel):
    words: List[RiddleWord]

class SwitchRiddle(BaseModel):
    prompt: GameText

class SwitchResponse(BaseModel):
    gameId: int
    riddle: SwitchRiddle

class SelectedSwitchPair(BaseModel):
    firstWordId: str
    secondWordId: str

class SwitchAnswerRequest(BaseModel):
    type: str
    gameId: int
    selectedPairs: List[SelectedSwitchPair]
    elapsedTimeMs: Optional[int] = None

class ResultResponse(BaseModel):
    score: int
    mistakes: int
    time: str
    accuracy: float
    pagesCompleted: int

router = APIRouter(prefix="/games", tags=["switch"])
active_games: Dict[int, Dict[str, Any]] = {}

def cleanup_expired_games():
    now = datetime.now()
    expired_ids = [
        gid for gid, data in active_games.items()
        if now - data["start_time"] > timedelta(hours=1)
    ]
    for gid in expired_ids:
        del active_games[gid]

@router.post("/switch/start", response_model=List[SwitchResponse])
async def start_switch_game(request: GameRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(cleanup_expired_games)
    if request.gameType != 'switch':
        raise HTTPException(status_code=400, detail="Invalid game type")
        
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        game_id = random.randint(1000, 9999)
        all_pages_responses = []
        all_correct_swapped_ids = set()
        
        page_to_ids = {}
        
        page_idx = 1
        current_id = 1

        while True:
            page_content = read_page(extract_path, page_idx)
            if not page_content:
                break
            
            word_tokens = get_token_info2(page_content)
            if not word_tokens:
                page_idx += 1
                continue

            page_data = transform_to_switch_model(page_content, word_tokens, current_id)
            
            page_ids = {w["id"] for w in page_data["words"]}
            page_to_ids[page_idx] = page_ids
            
            current_id = page_data["next_id"]
            all_correct_swapped_ids.update(page_data["swapped_ids"])

            all_pages_responses.append(SwitchResponse(
                gameId=game_id,
                riddle=SwitchRiddle(
                    prompt=GameText(words=[RiddleWord(**w) for w in page_data["words"]])
                )
            ))
            page_idx += 1

        active_games[game_id] = {
            "start_time": datetime.now(),
            "correct_ids": all_correct_swapped_ids,
            "page_to_ids": page_to_ids,
            "total_pages": len(all_pages_responses)
        }

        return all_pages_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch/submit", response_model=ResultResponse)
async def submit_switch_answers(request: SwitchAnswerRequest):
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_data = active_games[request.gameId]
    correct_ids = game_data["correct_ids"]
    page_to_ids = game_data["page_to_ids"]
    
    user_submitted_ids = set()
    for pair in request.selectedPairs:
        user_submitted_ids.add(pair.firstWordId)
        user_submitted_ids.add(pair.secondWordId)
    
    pages_with_activity = 0
    for p_idx, p_ids in page_to_ids.items():
        if any(uid in p_ids for uid in user_submitted_ids):
            pages_with_activity += 1
            
    hits = len(user_submitted_ids.intersection(correct_ids))
    misses = len(user_submitted_ids - correct_ids)
    unfound = len(correct_ids - user_submitted_ids)
    
    total_mistakes = misses + unfound
    total_possible = len(correct_ids)
    accuracy = hits / total_possible if total_possible > 0 else 0
    
    if request.elapsedTimeMs:
        sec = request.elapsedTimeMs // 1000
    else:
        sec = int((datetime.now() - game_data["start_time"]).total_seconds())
        
    del active_games[request.gameId]
    
    return ResultResponse(
        score=int(accuracy * 100),
        mistakes=total_mistakes,
        time=f"{sec // 60:02d}:{sec % 60:02d}",
        accuracy=accuracy,
        pagesCompleted=pages_with_activity
    )

@router.get("/switch/active")
async def get_active_games():

    return {
        "active_games_count": len(active_games),
        "game_ids": list(active_games.keys())
    }