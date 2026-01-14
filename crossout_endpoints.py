from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

from helpers import read_page
from crossout2 import generate_riddle, transform_to_crossout_model

class GameRequest(BaseModel):
    bookId: int
    gameType: str
    chapter: int

class CrossoutLine(BaseModel):
    id: str
    text: str

class CrossoutRiddle(BaseModel):
    lines: List[CrossoutLine]

class CrossoutResponse(BaseModel):
    gameId: int
    riddle: CrossoutRiddle

class CrossoutAnswerRequest(BaseModel):
    type: str
    gameId: int
    crossedOutLineIds: List[str]  
    elapsedTimeMs: Optional[int] = None

class ResultResponse(BaseModel):
    score: int
    mistakes: int
    time: str
    accuracy: float
    pagesCompleted: int

router = APIRouter(prefix="/games", tags=["crossout"])
active_games: Dict[int, Dict[str, Any]] = {}

def cleanup_expired_games():
    now = datetime.now()
    expired_ids = [
        gid for gid, data in active_games.items()
        if now - data["start_time"] > timedelta(hours=1)
    ]
    for gid in expired_ids:
        del active_games[gid]


@router.post("/crossout/start", response_model=List[CrossoutResponse])
async def start_crossout_game(request: GameRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(cleanup_expired_games)
    
    if request.gameType != 'crossout':
        raise HTTPException(status_code=400, detail="Invalid game type")
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        all_pages_responses = []
        all_extra_line_ids = set()
        page_to_ids = {}
        
        page_idx = 1
        shared_game_id = random.randint(1000, 9999)
        line_id_counter = 1 

        while True:
            page_content = read_page(extract_path, page_idx)
            if not page_content:
                break
            
            riddle_text = generate_riddle(page_content, extract_path)
            lines_text_list = transform_to_crossout_model(riddle_text)
            
            original_lines = {line.strip() for line in page_content.split("\n") if line.strip()}
            
            current_page_lines = []
            current_page_ids = set()
            
            for line_text in lines_text_list:
                line_id = str(line_id_counter)
                line_id_counter += 1
                
                current_page_ids.add(line_id)
                
                if line_text not in original_lines:
                    all_extra_line_ids.add(line_id)
                
                current_page_lines.append(CrossoutLine(id=line_id, text=line_text))

            page_to_ids[page_idx] = current_page_ids
            all_pages_responses.append(CrossoutResponse(
                gameId=shared_game_id,
                riddle=CrossoutRiddle(lines=current_page_lines)
            ))
            page_idx += 1

        if not all_pages_responses:
            raise HTTPException(status_code=404, detail="No content found")

        active_games[shared_game_id] = {
            "start_time": datetime.now(),
            "correct_ids": all_extra_line_ids,
            "page_to_ids": page_to_ids,
            "total_pages": len(all_pages_responses)
        }

        return all_pages_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crossout/submit", response_model=ResultResponse)
async def submit_crossout_answers(request: CrossoutAnswerRequest):
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    game_data = active_games[request.gameId]
    correct_ids = game_data["correct_ids"]
    page_to_ids = game_data["page_to_ids"]
    submitted_ids = set(request.crossedOutLineIds)
    
    pages_with_activity = 0
    for p_idx, p_ids in page_to_ids.items():
        if any(sid in p_ids for sid in submitted_ids):
            pages_with_activity += 1
    
    hits = len(submitted_ids.intersection(correct_ids))
    misses = len(submitted_ids - correct_ids)
    unfound = len(correct_ids - submitted_ids)
    
    total_possible = len(correct_ids)
    accuracy = hits / total_possible if total_possible > 0 else 0
    
    if request.elapsedTimeMs:
        sec = request.elapsedTimeMs // 1000
    else:
        sec = int((datetime.now() - game_data["start_time"]).total_seconds())
        
    del active_games[request.gameId]
    
    return ResultResponse(
        score=int(accuracy * 100),
        mistakes=misses + unfound,
        time=f"{sec // 60:02d}:{sec % 60:02d}",
        accuracy=accuracy,
        pagesCompleted=pages_with_activity
    )

@router.get("/crossout/active")
async def get_active_games():

    return {
        "active_games_count": len(active_games),
        "game_ids": list(active_games.keys())
    }