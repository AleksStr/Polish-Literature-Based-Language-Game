from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import random
from datetime import datetime
import uuid

from helpers import read_page, get_token_info2
from word_token import Word_Token  
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

router = APIRouter(prefix="/games", tags=["fill-gaps"])


active_games: Dict[int, Dict[str, Any]] = {}

def get_book_path(book_id: int, chapter: int) -> str:

    return f"extracts/book_{book_id}/chapter_{chapter}.txt"

@router.post("/fill-gaps/start", response_model=FillGapsResponse)
async def start_fill_gaps_game(request: GameRequest):

    if request.gameType != 'fill-gaps':
        raise HTTPException(status_code=400, detail="This endpoint is only for fill-gaps game type")
    
    try:
        extract_path = get_book_path(request.bookId, request.chapter)
        
        page_content = read_page(extract_path, 1)
        if not page_content:
            raise HTTPException(status_code=404, detail="Page content not found")
        
        word_tokens_data = get_token_info2(page_content)
        if not word_tokens_data:
            raise HTTPException(status_code=600, detail="Failed to process text")
        
        word_tokens = []
        for token in word_tokens_data:
            if not hasattr(token, 'display_word'):
                token.display_word = token.original_text.lower()
            word_tokens.append(token)
        

        n_words = random.randint(3, 8)  
        n_words = min(n_words, len(word_tokens))
        words_to_remove = pick_words_to_remove(word_tokens, n_words)
        

        game_data = transform_to_fill_model(page_content, word_tokens, words_to_remove)
        

        game_id = random.randint(1000, 9999)
        while game_id in active_games:
            game_id = random.randint(1000, 9999)
        

        active_games[game_id] = {
            "book_id": request.bookId,
            "chapter": request.chapter,
            "start_time": datetime.now(),
            "page_content": page_content,
            "words_to_remove": words_to_remove,
            "correct_answers": {}, 
            "options": game_data["riddle"]["options"]
        }
        

        sorted_words = sorted(words_to_remove, key=lambda x: x.start)
        for i, word in enumerate(sorted_words):
            for option in game_data["riddle"]["options"]:
                if option["label"] == word.display_word:
                    active_games[game_id]["correct_answers"][i] = option["id"]
                    break
        

        return FillGapsResponse(
            gameId=game_id,
            riddle=game_data["riddle"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting game: {str(e)}")

@router.post("/fill-gaps/submit", response_model=ResultResponse)
async def submit_fill_gaps_answers(request: FillGapsAnswerRequest):
    """
    Submit answers for a fill-gaps game
    """
    if request.type != 'fill-gaps':
        raise HTTPException(status_code=400, detail="Invalid game type")
    
    if request.gameId not in active_games:
        raise HTTPException(status_code=404, detail="Game not found or expired")
    
    game_data = active_games[request.gameId]
    
    try:

        correct_answers = 0
        total_gaps = len(game_data["words_to_remove"])
        

        for answer in request.answers:
            if answer.gapIndex in game_data["correct_answers"]:
                correct_option_id = game_data["correct_answers"][answer.gapIndex]
                if answer.optionId == correct_option_id:
                    correct_answers += 1
        

        score = int((correct_answers / total_gaps) * 100) if total_gaps > 0 else 0
        mistakes = total_gaps - correct_answers
        accuracy = correct_answers / total_gaps if total_gaps > 0 else 0
        

        if request.elapsedTimeMs:
            total_seconds = request.elapsedTimeMs // 1000
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
        else:
            time_delta = datetime.now() - game_data["start_time"]
            total_seconds = int(time_delta.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
        

        del active_games[request.gameId]
        
        return ResultResponse(
            score=score,
            mistakes=mistakes,
            time=time_str,
            accuracy=accuracy,
            pagesCompleted=1  
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answers: {str(e)}")

@router.get("/fill-gaps/active")
async def get_active_games():

    return {
        "active_games_count": len(active_games),
        "game_ids": list(active_games.keys())
    }