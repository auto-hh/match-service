from fastapi import APIRouter, Depends
from schemas import Resume, MatchResult, ExplorationResult, Vacancy, CoverLetterResult
from core import Matcher, Explorer, LetterGenerator
from service import get_letter_generator, get_explorer, get_matcher

router = APIRouter()

@router.post("/search")
async def match(resume: Resume, matcher: Matcher = Depends(get_matcher)) -> MatchResult:
    result = matcher.match(resume)
    print(result)
    return result

@router.post("/analyze")
async def analyze_resume(resume: Resume, explorer: Explorer = Depends(get_explorer)) -> ExplorationResult:
    return explorer.analyze(resume)

@router.post("/generate")
async def generate_cover_letter(resume: Resume, vacancy: Vacancy, letter_generator: LetterGenerator = Depends(get_letter_generator)) -> CoverLetterResult:
    return letter_generator.generate(resume, vacancy)

@router.get("/health")
async def check_health():
    return {"status": "ok"}
