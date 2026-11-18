from datetime import date

from fastapi import APIRouter, Depends, status

from app.api.deps import enforce_rate_limit, get_llm, get_repository
from app.db.repository import ReportRepository
from app.llm import LLMProvider
from app.schemas.report import GenerateRequest, Report, ReportCreate, ReportItem
from app.services.report_service import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", dependencies=[Depends(enforce_rate_limit)])
def generate(request: GenerateRequest, llm: LLMProvider = Depends(get_llm)) -> Report:
    """Turn a transcript into a structured report. Nothing is saved."""
    return generate_report(request.transcript, request.language, llm, date.today())


@router.post("", status_code=status.HTTP_201_CREATED)
def create(item: ReportCreate, repository: ReportRepository = Depends(get_repository)) -> ReportItem:
    """Save a report after the user has checked it."""
    return repository.add(item)


@router.get("")
def list_reports(repository: ReportRepository = Depends(get_repository)) -> list[ReportItem]:
    """Saved reports, newest first."""
    return repository.list_recent()
