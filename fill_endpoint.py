from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import random
from datetime import datetime, timedelta
import uuid

from helpers import read_page, get_token_info2
from fill import transform_to_fill_model, pick_words_to_remove


from typing import Optional
from pydantic import BaseModel


class GameRequest(BaseModel):
    bookId: int
    gameType: str  
    chapter: int

class FillGapAnswer(BaseModel):
    gapIndex: int
    optionId: str

class FillGapsAnswerRequest(BaseModel):
    type: str  
    gameId: int
    answers: list[FillGapAnswer]
    elapsedTimeMs: Optional[int] = None

class RiddleOption(BaseModel):
    id: str
    label: str

class FillGapsRiddlePart(BaseModel):
    type: str  # 'gap' or 'text'
    value: str

class FillGapsRiddle(BaseModel):
    prompt: dict
    options: list[RiddleOption]

class FillGapsResponse(BaseModel):
    gameId: int
    riddle: FillGapsRiddle

class ResultResponse(BaseModel):
    score: int
    mistakes: int
    time: str
    accuracy: float
    pagesCompleted: int

def cleanup_expired_games():
    now = datetime.now()
    expired_ids = [
        gid for gid, data in active_games.items()
        if now - data["start_time"] > timedelta(hours=1)
    ]
    for gid in expired_ids:
        del active_games[gid]



router = APIRouter(prefix="/games", tags=["fill-gaps"])
active_games: Dict[int, Dict[str, Any]] = {}

@router.post("/fill-gaps/start")
async def start_fill_gaps_game(request: GameRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(cleanup_expired_games)
    if request.gameType != 'fill-gaps':
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        game_id = random.randint(1000, 9999)
        
        all_pages_riddles = []
        correct_answers_state = {}
        page_to_gaps = {} 
        global_gap_counter = 0
        page_idx = 1

        while True:
            page_content = read_page(extract_path, page_idx)
            if not page_content:
                break
            
            word_tokens_data = get_token_info2(page_content)
            if not word_tokens_data:
                page_idx += 1
                continue

            word_tokens = [t for t in word_tokens_data]
            for t in word_tokens:
                if not hasattr(t, 'display_word'):
                    t.display_word = t.original_text.lower()

            n_words = min(random.randint(1,1), len(word_tokens))
            words_to_remove = pick_words_to_remove(word_tokens, n_words)
            
            game_data = transform_to_fill_model(page_content, word_tokens, words_to_remove)
            

            current_page_gaps = []
            sorted_words = sorted(words_to_remove, key=lambda x: x.start)
            for i, word in enumerate(sorted_words):
                for option in game_data["riddle"]["options"]:
                    if option["label"] == word.display_word:
                        correct_answers_state[global_gap_counter] = option["id"]
                        current_page_gaps.append(global_gap_counter)
                        global_gap_counter += 1
                        break

            page_to_gaps[page_idx] = current_page_gaps
            all_pages_riddles.append({
                "gameId": game_id,
                "riddle": game_data["riddle"]
            })
            page_idx += 1

        active_games[game_id] = {
            "start_time": datetime.now(),
            "total_gaps": global_gap_counter,
            "correct_answers": correct_answers_state,
            "page_to_gaps": page_to_gaps,
            "total_pages": len(all_pages_riddles)
        }

        return all_pages_riddles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fill-gaps/submit", response_model=ResultResponse)
async def submit_fill_gaps_answers(request: FillGapsAnswerRequest):
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_data = active_games[request.gameId]
    page_to_gaps = game_data["page_to_gaps"]
    correct_count = 0
    

    user_answered_indices = {answer.gapIndex for answer in request.answers}
    
    for answer in request.answers:
        if game_data["correct_answers"].get(answer.gapIndex) == answer.optionId:
            correct_count += 1

    pages_with_activity = 0
    for p_idx, gap_indices in page_to_gaps.items():
        if any(idx in user_answered_indices for idx in gap_indices):
            pages_with_activity += 1

    total_gaps = game_data["total_gaps"]
    accuracy = correct_count / total_gaps if total_gaps > 0 else 0
    
    if request.elapsedTimeMs:
        sec = request.elapsedTimeMs // 1000
    else:
        delta = datetime.now() - game_data["start_time"]
        sec = int(delta.total_seconds())
        
    time_str = f"{sec // 60:02d}:{sec % 60:02d}"
    
    del active_games[request.gameId]
    
    return ResultResponse(
        score=int(accuracy * 100),
        mistakes=max(0, total_gaps - correct_count),
        time=time_str,
        accuracy=accuracy,
        pagesCompleted=pages_with_activity
    )

@router.get("/fill-gaps/active")
async def get_active_games():

    return {
        "active_games_count": len(active_games),
        "game_ids": list(active_games.keys())
    }