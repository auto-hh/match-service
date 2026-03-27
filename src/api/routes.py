from fastapi import APIRouter, Depends
from schemas import Resume, MatchResult, ExplorationResult
from core import Matcher, Explorer
from service import get_letter_generator, get_explorer, get_matcher

router = APIRouter()

@router.post("/search")
async def match(resume: Resume, matcher: Matcher = Depends(get_matcher)) -> MatchResult:
    result = matcher.match(resume)
    print(result)
    return result

@router.post("/analyze")
async def analyze(resume: Resume, explorer: Explorer = Depends(get_explorer)) -> ExplorationResult:
    return explorer.analyze(resume)

@router.get("/health")
async def health():
    return {"status": "ok"}
