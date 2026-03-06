import asyncio
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.models.tender import TenderList
from app.models.analysis import TenderAnalysis, BoardOverlap
from app.scrapers.ted import fetch_belgian_tenders, fetch_tender_detail, _pick_lang
from app.scrapers.opencorporates import lookup_organization

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


@router.get("/{tender_id}/analyze", response_model=TenderAnalysis)
async def analyze_tender(tender_id: str):
    """
    Analyseer een aanbesteding: haal de aanbestedende organisatie en de
    gegunde partijen op, inclusief hun bestuur. Markeer overlappende bestuurders.
    """
    notice = await fetch_tender_detail(tender_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Aanbesteding niet gevonden in TED")

    # Aanbestedende organisatie
    authority_name = _pick_lang(notice.get("buyer-name")) or "Onbekend"

    # Gegunde partijen (winner-name kan een string, lijst of None zijn)
    raw_winners = notice.get("winner-name") or []
    if isinstance(raw_winners, str):
        raw_winners = [raw_winners]
    winner_names: list[str] = []
    for w in raw_winners[:5]:  # max 5 partijen
        name = _pick_lang(w) if isinstance(w, dict) else w
        if name:
            winner_names.append(name)

    # Haal alle organisaties parallel op
    tasks = [lookup_organization(authority_name)] + [
        lookup_organization(n) for n in winner_names
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    authority_org = results[0] if not isinstance(results[0], Exception) else None
    if not authority_org:
        raise HTTPException(status_code=502, detail="Fout bij ophalen organisatiedata")

    awarded_orgs = [
        r for r in results[1:] if not isinstance(r, Exception)
    ]

    # Bereken overlappende bestuurders
    person_orgs: dict[str, list[str]] = {}
    for member in authority_org.board:
        person_orgs.setdefault(member.name, []).append(authority_org.name)
    for org in awarded_orgs:
        for member in org.board:
            person_orgs.setdefault(member.name, []).append(org.name)

    overlaps = [
        BoardOverlap(person_name=name, organizations=orgs)
        for name, orgs in person_orgs.items()
        if len(orgs) > 1
    ]

    note = None if winner_names else "Geen gegunde partijen gevonden (mogelijk een openstaande procedure)"

    return TenderAnalysis(
        tender_id=tender_id,
        contracting_authority=authority_org,
        awarded_parties=awarded_orgs,
        board_overlaps=overlaps,
        note=note,
    )
