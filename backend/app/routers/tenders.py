from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.models.tender import TenderList
from app.scrapers.ted import fetch_belgian_tenders

router = APIRouter()


@router.get("", response_model=TenderList)
async def list_tenders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="Vrije zoekterm"),
    cpv: Optional[str] = Query(None, description="CPV-code filter"),
    nuts: Optional[str] = Query(None, description="NUTS-regio filter (bijv. BE2)"),
):
    try:
        tenders, total = await fetch_belgian_tenders(
            page=page, page_size=page_size, query=q, cpv=cpv, nuts=nuts
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Data ophalen mislukt: {e}")

    return TenderList(total=total, page=page, page_size=page_size, items=tenders)


@router.get("/{tender_id}")
async def get_tender(tender_id: str):
    # Placeholder: detail ophalen via TED publicationNumber
    return {
        "id": tender_id,
        "url": f"https://ted.europa.eu/en/notice/-/detail/{tender_id}",
        "note": "Detail endpoint - nog te implementeren",
    }
