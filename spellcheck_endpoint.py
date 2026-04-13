from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

from helpers import read_page, get_token_info_basic
from spellcheck import generate_level, transform_to_spellcheck_model

'''this module handles endpoints responsible for spellcheck riddle'''

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

def cleanup_expired_games():
    ''' cleans games that have been active for over an hour'''
    now = datetime.now()
    expired_ids = [
        gid for gid, data in active_games.items()
        if now - data["start_time"] > timedelta(hours=1)
    ]
    for gid in expired_ids:
        del active_games[gid]

@router.post("/spellcheck/start", response_model=List[SpellcheckResponse])
async def start_spellcheck_game(request: GameRequest, background_tasks: BackgroundTasks):
    ''' generates a spellcheck riddle of a specific extract'''
    background_tasks.add_task(cleanup_expired_games)
    if request.gameType != 'spellcheck':
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    try:
        extract_path = f"extracts/book_{request.bookId}/chapter_{request.chapter}.txt"
        game_id = random.randint(1000, 9999)
        while (game_id in active_games):
            game_id = random.randint(1000, 9999)
        pages_with_typos = generate_level(extract_path)
        
        all_pages_responses = []
        all_typo_ids = set()
        page_to_ids = {}
        current_word_id = 1
        
        for page_idx, (masked_page, typo_data) in enumerate(pages_with_typos, 1):
            original_page = read_page(extract_path, page_idx)
            if not original_page: continue
                
            word_tokens = get_token_info_basic(original_page)
            if not word_tokens: continue

            typos_with_positions = []
            for correct_word, typo_word in typo_data:
                for token in word_tokens:
                    if token.original_text == correct_word and not token.original_text == typo_word:
                        typos_with_positions.append((correct_word, typo_word, token.start))
                        break


            spellcheck_model, next_id, page_typo_ids = transform_to_spellcheck_model(
                masked_page, 
                word_tokens, 
                typos_with_positions,
                current_word_id 
            )
            
            p_ids = {w["id"] for w in spellcheck_model["riddle"]["prompt"]["words"]}
            page_to_ids[page_idx] = p_ids
            all_typo_ids.update(page_typo_ids)
            current_word_id = next_id
            
            riddle_words = [RiddleWord(id=w["id"], value=w["value"]) for w in spellcheck_model["riddle"]["prompt"]["words"]]
            all_pages_responses.append(SpellcheckResponse(
                gameId=game_id,
                riddle=SpellcheckRiddle(prompt=GameText(words=riddle_words))
            ))
        
        active_games[game_id] = {
            "start_time": datetime.now(),
            "correct_ids": all_typo_ids,
            "page_to_ids": page_to_ids,
            "total_pages": len(all_pages_responses)
        }
        return all_pages_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spellcheck/submit", response_model=ResultResponse)
async def submit_spellcheck_answers(request: SpellcheckAnswerRequest):
    ''' checks solution '''
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_data = active_games[request.gameId]
    correct_ids = game_data["correct_ids"]
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

@router.get("/spellcheck/active")
async def get_active_games():
    ''' this gives an endpoint to see all active games of spellcheck type'''

    return {
        "active_games_count": len(active_games),
        "game_ids": list(active_games.keys())
    }