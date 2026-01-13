from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import random

from helpers import read_page, get_token_info2
from anagram import generate_riddle, get_anagram

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


@router.post("/anagram/start", response_model=List[AnagramResponse])
async def start_anagram_game(request: GameRequest):
    if request.gameType != 'anagram':
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        responses = []
        all_correct_word_ids = set()
        game_id = random.randint(1000, 9999)
        page_idx = 1

        while True:
            page_content = read_page(extract_path, page_idx)
            if not page_content:
                break
            
            tokens = get_token_info2(page_content)
            if not tokens:
                page_idx += 1
                continue

            max_to_mask = min(len(tokens), 8)
            n_to_anagram = random.randint(3, max_to_mask)
            indices_to_anagram = set(random.sample(range(len(tokens)), n_to_anagram))
            
            words_list = []
            last_idx = 0
            
            for i, token in enumerate(tokens):
                prefix_text = page_content[last_idx:token.start]
                if prefix_text:
                    words_list.append(RiddleWord(id=str(uuid.uuid4()), value=prefix_text))
                
                word_id = str(uuid.uuid4())
                word_value = token.original_text
                
                if i in indices_to_anagram:
                    word_value = get_anagram(word_value)
                    all_correct_word_ids.add(word_id)
                
                words_list.append(RiddleWord(id=word_id, value=word_value))
                last_idx = token.finish
            
            trailing_text = page_content[last_idx:]
            if trailing_text:
                words_list.append(RiddleWord(id=str(uuid.uuid4()), value=trailing_text))

            responses.append(AnagramResponse(
                gameId=game_id,
                riddle=AnagramRiddle(prompt=GameText(words=words_list))
            ))
            page_idx += 1

        if not responses:
            raise HTTPException(status_code=404, detail="Content not found")

        active_games[game_id] = {
            "correct_word_ids": all_correct_word_ids,
            "start_time": datetime.now(),
            "pages_count": len(responses)
        }

        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anagram/submit", response_model=ResultResponse)
async def submit_anagram_answers(request: AnagramAnswerRequest):
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_data = active_games[request.gameId]
    correct_ids = game_data["correct_word_ids"]
    submitted_ids = set(request.selectedWordIds)
    
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
        pagesCompleted=game_data["pages_count"]
    )

@router.get("/anagram/active")
async def get_active_anagram_games():
    return {
        "active_games_count": len(active_games),
        "game_ids": list(active_games.keys())
    }