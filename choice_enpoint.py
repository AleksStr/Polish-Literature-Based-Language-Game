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
            
            for gap in page_data["gaps"]:
                correct_answers_state[gap["id"]] = gap["correctOptionId"]

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
            "pages_count": len(all_pages_responses)
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
    
    hits = 0
    for user_ans in request.answers:
        if correct_map.get(user_ans.gapId) == user_ans.optionId:
            hits += 1

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
        pagesCompleted=game_data["pages_count"]
    )