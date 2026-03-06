import asyncio
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.models.tender import TenderList
from app.models.analysis import TenderAnalysis, BoardOverlap
from app.scrapers.ted import fetch_belgian_tenders, fetch_tender_detail, _pick_lang_all
from app.scrapers.opencorporates import lookup_organization

router = APIRouter()


@router.get("", response_model=TenderList)
async def list_tenders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="Vrije zoekterm"),
    cpv: Optional[str] = Query(None, description="CPV-code filter"),
    nuts: Optional[str] = Query(None, description="NUTS-regio filter (bijv. BE2)"),
    awarded_only: bool = Query(False, description="Toon enkel gegunde opdrachten"),
):
    try:
        tenders, total = await fetch_belgian_tenders(
            page=page, page_size=page_size, query=q, cpv=cpv, nuts=nuts,
            awarded_only=awarded_only,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Data ophalen mislukt: {e}")

    return TenderList(total=total, page=page, page_size=page_size, items=tenders)


@router.get("/{tender_id}/analyze", response_model=TenderAnalysis)
async def analyze_tender(tender_id: str):
    """
    Analyseer een aanbesteding: haal de aanbestedende organisatie en de
    gegunde partijen op, inclusief hun bestuur. Markeer overlappende bestuurders.
    """
    notice = await fetch_tender_detail(tender_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Aanbesteding niet gevonden in TED")

    # Aanbestedende organisaties — kan er meerdere zijn bij gezamenlijke aanbesteding
    authority_names = _pick_lang_all(notice.get("buyer-name")) or ["Onbekend"]

    # Gegunde partijen — alleen aanwezig na gunning
    winner_names = _pick_lang_all(notice.get("winner-name"))[:5]  # max 5

    # Haal alle organisaties parallel op
    all_names = authority_names + winner_names
    results = await asyncio.gather(
        *[lookup_organization(n) for n in all_names],
        return_exceptions=True,
    )

    authority_orgs = [
        r for r in results[: len(authority_names)]
        if not isinstance(r, Exception)
    ]
    awarded_orgs = [
        r for r in results[len(authority_names):]
        if not isinstance(r, Exception)
    ]

    if not authority_orgs:
        raise HTTPException(status_code=502, detail="Fout bij ophalen organisatiedata")

    # Bereken overlappende bestuurders over alle betrokken organisaties
    person_orgs: dict[str, list[str]] = {}
    for org in authority_orgs + awarded_orgs:
        for member in org.board:
            person_orgs.setdefault(member.name, []).append(org.name)

    overlaps = [
        BoardOverlap(person_name=name, organizations=orgs)
        for name, orgs in person_orgs.items()
        if len(orgs) > 1
    ]

    note = None if winner_names else "Openstaande procedure — nog geen gegunde partijen"

    return TenderAnalysis(
        tender_id=tender_id,
        contracting_authorities=authority_orgs,
        awarded_parties=awarded_orgs,
        board_overlaps=overlaps,
        note=note,
    )
