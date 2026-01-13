from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import random

from helpers import read_page, get_token_info2
from spellcheck import generate_typo_distractor

class GameRequest(BaseModel):
    bookId: int
    gameType: str
    chapter: int

class RiddleWord(BaseModel):
    id: str
    value: str

class GameText(BaseModel):
    words: List[RiddleWord]

class SpellcheckRiddle(BaseModel):
    prompt: GameText

class SpellcheckResponse(BaseModel):
    gameId: int
    riddle: SpellcheckRiddle

class SpellcheckAnswerRequest(BaseModel):
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

router = APIRouter(prefix="/games", tags=["spellcheck"])
active_games: Dict[int, Dict[str, Any]] = {}

@router.post("/spellcheck/start", response_model=List[SpellcheckResponse])
async def start_spellcheck_game(request: GameRequest):
    if request.gameType != 'spellcheck':
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        game_id = random.randint(1000, 9999)
        
        all_pages_responses = []
        typo_word_ids = set()
        page_idx = 1

        while True:
            page_content = read_page(extract_path, page_idx)
            if not page_content:
                break
            
            word_tokens = get_token_info2(page_content)
            if not word_tokens:
                page_idx += 1
                continue

            maskable_indices = [
                i for i, t in enumerate(word_tokens) 
                if len(t.original_text) >= 5
            ]
            
            n_typos = min(len(maskable_indices), random.randint(3, 8))
            chosen_indices = set(random.sample(maskable_indices, n_typos)) if maskable_indices else set()
            
            riddle_words = []
            last_idx = 0
            
            for i, token in enumerate(word_tokens):
                prefix_text = page_content[last_idx:token.start]
                if prefix_text:
                    riddle_words.append(RiddleWord(id=str(uuid.uuid4()), value=prefix_text))
                
                word_id = str(uuid.uuid4())
                word_value = token.original_text
                
                if i in chosen_indices:
                    word_value = generate_typo_distractor(word_value)
                    typo_word_ids.add(word_id)
                
                riddle_words.append(RiddleWord(id=word_id, value=word_value))
                last_idx = token.finish
            
            trailing_text = page_content[last_idx:]
            if trailing_text:
                riddle_words.append(RiddleWord(id=str(uuid.uuid4()), value=trailing_text))

            all_pages_responses.append(SpellcheckResponse(
                gameId=game_id,
                riddle=SpellcheckRiddle(
                    prompt=GameText(words=riddle_words)
                )
            ))
            page_idx += 1

        if not all_pages_responses:
            raise HTTPException(status_code=404, detail="Content not found")

        active_games[game_id] = {
            "start_time": datetime.now(),
            "correct_ids": typo_word_ids,
            "pages_count": len(all_pages_responses)
        }

        return all_pages_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spellcheck/submit", response_model=ResultResponse)
async def submit_spellcheck_answers(request: SpellcheckAnswerRequest):
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_data = active_games[request.gameId]
    correct_ids = game_data["correct_ids"]
    submitted_ids = set(request.selectedWordIds)
    
    hits = len(submitted_ids.intersection(correct_ids))
    misses = len(submitted_ids - correct_ids)
    unfound = len(correct_ids - submitted_ids)
    
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
        pagesCompleted=game_data["pages_count"]
    )