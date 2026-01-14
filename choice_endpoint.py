from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import random

from helpers import read_page, get_token_info
from choice import transform_to_choice_model

class ChoiceOption(BaseModel):
    id: str
    label: str

class GameRequest(BaseModel):
    bookId: int
    gameType: str  
    chapter: int

class ChoiceGap(BaseModel):
    id: str
    correctOptionId: str
    options: List[ChoiceOption]

class ChoiceRiddlePart(BaseModel):
    type: str
    value: Optional[str] = None
    gapId: Optional[str] = None

class ChoiceRiddle(BaseModel):
    id: str
    parts: List[ChoiceRiddlePart]
    gaps: List[ChoiceGap]

class ChoiceResponse(BaseModel):
    gameId: int
    riddle: ChoiceRiddle

class ChoiceAnswer(BaseModel):
    gapId: str
    optionId: str

class ChoiceAnswerRequest(BaseModel):
    type: str
    gameId: int
    answers: List[ChoiceAnswer]
    elapsedTimeMs: Optional[int] = None

class ResultResponse(BaseModel):
    score: int
    mistakes: int
    time: str
    accuracy: float
    pagesCompleted: int

router = APIRouter(prefix="/games", tags=["choice"])
active_games: Dict[int, Dict[str, Any]] = {}

@router.post("/choice/start", response_model=List[ChoiceResponse])
async def start_choice_game(request: GameRequest):
    if request.gameType != 'choice':
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        game_id = random.randint(1000, 9999)
        all_pages_responses = []
        correct_answers_state = {}
        page_to_gap_ids = {}
        page_idx = 1

        while True:
            page_content = read_page(extract_path, page_idx)
            if not page_content:
                break
            
            word_tokens = get_token_info(page_content)
            if not word_tokens:
                page_idx += 1
                continue

            max_to_mask = min(len(word_tokens), 8)
            chosen_indices = set(random.sample(range(len(word_tokens)), random.randint(3, max_to_mask)))
            
            page_data = transform_to_choice_model(page_content, word_tokens, chosen_indices)
            
            current_page_gaps = set()
            for gap in page_data["gaps"]:
                gap_id = gap["id"]
                correct_answers_state[gap_id] = gap["correctOptionId"]
                current_page_gaps.add(gap_id)

            page_to_gap_ids[page_idx] = current_page_gaps
            all_pages_responses.append(ChoiceResponse(
                gameId=game_id,
                riddle=ChoiceRiddle(**page_data)
            ))
            page_idx += 1

        if not all_pages_responses:
            raise HTTPException(status_code=404, detail="Chapter not found")

        active_games[game_id] = {
            "start_time": datetime.now(),
            "correct_answers": correct_answers_state,
            "page_to_gap_ids": page_to_gap_ids,
            "total_pages": len(all_pages_responses)
        }

        return all_pages_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/choice/submit", response_model=ResultResponse)
async def submit_choice_answers(request: ChoiceAnswerRequest):
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    game_data = active_games[request.gameId]
    correct_map = game_data["correct_answers"]
    page_to_gap_ids = game_data["page_to_gap_ids"]
    
    user_answered_gap_ids = {ans.gapId for ans in request.answers}
    
    hits = 0
    for user_ans in request.answers:
        if correct_map.get(user_ans.gapId) == user_ans.optionId:
            hits += 1

    pages_with_activity = 0
    for p_idx, gap_ids in page_to_gap_ids.items():
        if any(gid in user_answered_gap_ids for gid in gap_ids):
            pages_with_activity += 1

    total_gaps = len(correct_map)
    accuracy = hits / total_gaps if total_gaps > 0 else 0
    
    if request.elapsedTimeMs:
        sec = request.elapsedTimeMs // 1000
    else:
        sec = int((datetime.now() - game_data["start_time"]).total_seconds())
        
    del active_games[request.gameId]
    
    return ResultResponse(
        score=int(accuracy * 100),
        mistakes=max(0, total_gaps - hits),
        time=f"{sec // 60:02d}:{sec % 60:02d}",
        accuracy=accuracy,
        pagesCompleted=pages_with_activity
    )