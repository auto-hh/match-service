from fastapi import APIRouter, Depends
from schemas import Resume
from core import Matcher, Explorer
from service import get_letter_generator, get_explorer, get_matcher

router = APIRouter()

@router.post("/analyze")
async def analyze(resume: Resume, explorer: Explorer = Depends(get_explorer)):
    result = explorer.analyze(resume)
    return result.to_dict()

@router.post("/search")
async def match(resume: Resume, matcher: Matcher = Depends(get_matcher)):
    result = matcher.match(resume)
    return result.to_dict()

@router.get("/health")
async def health():
    return {"status": "ok"}