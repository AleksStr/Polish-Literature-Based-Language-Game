from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import random

from helpers import read_page
from crossout import generate_riddle, transform_to_crossout_model

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

active_games_metadata: Dict[int, Dict[str, Any]] = {}

@router.post("/crossout/start", response_model=List[CrossoutResponse])
async def start_crossout_game(request: GameRequest):
    if request.gameType != 'crossout':
        raise HTTPException(status_code=400, detail="Invalid game type")
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        all_pages_responses = []
        all_extra_line_ids = set()
        
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
            for line_text in lines_text_list:

                line_id = str(line_id_counter)
                line_id_counter += 1
                
                if line_text not in original_lines:
                    all_extra_line_ids.add(line_id)
                
                current_page_lines.append(CrossoutLine(id=line_id, text=line_text))

            all_pages_responses.append(CrossoutResponse(
                gameId=shared_game_id,
                riddle=CrossoutRiddle(lines=current_page_lines)
            ))
            page_idx += 1

        if not all_pages_responses:
            raise HTTPException(status_code=404, detail="No content found")

        active_games_metadata[shared_game_id] = {
            "start_time": datetime.now(),
            "correct_ids": all_extra_line_ids,
            "pages_count": len(all_pages_responses)
        }

        return all_pages_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crossout/submit", response_model=ResultResponse)
async def submit_crossout_answers(request: CrossoutAnswerRequest):
    if request.gameId not in active_games_metadata:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    game_data = active_games_metadata[request.gameId]
    correct_ids = game_data["correct_ids"]
    
    # Directly convert the list to a set for comparison
    submitted_ids = set(request.crossedOutLineIds)
    
    hits = len(submitted_ids.intersection(correct_ids))
    misses = len(submitted_ids - correct_ids)
    unfound = len(correct_ids - submitted_ids)
    
    total_possible = len(correct_ids)
    accuracy = hits / total_possible if total_possible > 0 else 0
    
    if request.elapsedTimeMs:
        sec = request.elapsedTimeMs // 1000
    else:
        sec = int((datetime.now() - game_data["start_time"]).total_seconds())
        
    del active_games_metadata[request.gameId]
    
    return ResultResponse(
        score=int(accuracy * 100),
        mistakes=misses + unfound,
        time=f"{sec // 60:02d}:{sec % 60:02d}",
        accuracy=accuracy,
        pagesCompleted=game_data["pages_count"]
    )