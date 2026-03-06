"""
Detail endpoint voor een TED notice:
- alle betrokken organisaties met KBO-nummers en rollen
- optioneel: mandatarissen per org ophalen via KBO
- optioneel: overlap detectie tussen buyers en winners
"""
import asyncio
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.scrapers.ted_xml import fetch_notice_organisations, TedOrganisation
from app.scrapers.kbo import fetch_company, KboCompany, Mandatary

router = APIRouter()


# ── Response modellen ───────────────────────────────────────────────────────

class MandataryOut(BaseModel):
    role: str
    name: str
    first_name: str
    last_name: str
    since: Optional[str]


class OrganisationOut(BaseModel):
    internal_id: str
    name: str
    kbo_number: Optional[str]
    kbo_raw: Optional[str]
    city: Optional[str]
    country: Optional[str]
    email: Optional[str]
    roles: list[str]
    awarded_amounts: list[float]
    mandataries: Optional[list[MandataryOut]] = None
    kbo_status: Optional[str] = None


class OverlapPerson(BaseModel):
    name: str
    buyer_org: str
    buyer_org_kbo: Optional[str]
    buyer_role: str
    winner_org: str
    winner_org_kbo: Optional[str]
    winner_role: str


class NoticeDetailOut(BaseModel):
    publication_number: str
    organisations: list[OrganisationOut]
    overlaps: list[OverlapPerson]


# ── Helper ──────────────────────────────────────────────────────────────────

def _to_out(org: TedOrganisation, kbo: Optional[KboCompany] = None) -> OrganisationOut:
    mandataries = None
    kbo_status = None
    if kbo:
        mandataries = [
            MandataryOut(
                role=m.role,
                name=m.name,
                first_name=m.first_name,
                last_name=m.last_name,
                since=m.since,
            )
            for m in kbo.mandataries
        ]
        kbo_status = kbo.status

    return OrganisationOut(
        internal_id=org.internal_id,
        name=org.name,
        kbo_number=org.kbo_number,
        kbo_raw=org.kbo_raw,
        city=org.city,
        country=org.country,
        email=org.email,
        roles=org.roles,
        awarded_amounts=org.awarded_amounts,
        mandataries=mandataries,
        kbo_status=kbo_status,
    )


def _detect_overlaps(
    orgs_with_kbo: list[tuple[TedOrganisation, Optional[KboCompany]]]
) -> list[OverlapPerson]:
    """
    Vergelijk mandatarissen van buyers vs. winners.
    Overlap = dezelfde persoon (naam-match) bij zowel een buyer als een winner.
    """
    buyers = [(o, k) for o, k in orgs_with_kbo if "buyer" in o.roles and k]
    winners = [(o, k) for o, k in orgs_with_kbo if "winner" in o.roles and k]

    overlaps: list[OverlapPerson] = []
    seen = set()

    for buyer_org, buyer_kbo in buyers:
        for m_buyer in buyer_kbo.mandataries:
            for winner_org, winner_kbo in winners:
                if winner_org.internal_id == buyer_org.internal_id:
                    continue
                for m_winner in winner_kbo.mandataries:
                    # Naam-match: zelfde achternaam + voornaam (case-insensitive)
                    if (
                        m_buyer.last_name.lower() == m_winner.last_name.lower()
                        and m_buyer.first_name.lower() == m_winner.first_name.lower()
                        and m_buyer.name.strip()
                    ):
                        key = (m_buyer.name, buyer_org.internal_id, winner_org.internal_id)
                        if key not in seen:
                            seen.add(key)
                            overlaps.append(OverlapPerson(
                                name=m_buyer.name,
                                buyer_org=buyer_org.name,
                                buyer_org_kbo=buyer_org.kbo_number,
                                buyer_role=m_buyer.role,
                                winner_org=winner_org.name,
                                winner_org_kbo=winner_org.kbo_number,
                                winner_role=m_winner.role,
                            ))
    return overlaps


# ── Endpoint ────────────────────────────────────────────────────────────────

@router.get("/{publication_number}", response_model=NoticeDetailOut)
async def get_notice_detail(
    publication_number: str,
    include_mandataries: bool = Query(
        True,
        description="Haal mandatarissen op via KBO (trager maar rijker)"
    ),
):
    """
    Geeft alle organisaties in een TED notice terug,
    inclusief KBO-nummers, rollen en (optioneel) mandatarissen.
    Detecteert ook overlappende personen tussen buyers en winners.
    """
    try:
        orgs = await fetch_notice_organisations(publication_number)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TED XML ophalen mislukt: {e}")

    orgs_with_kbo: list[tuple[TedOrganisation, Optional[KboCompany]]] = []

    if include_mandataries:
        # Parallel alle KBO-nummers ophalen
        async def safe_kbo(org: TedOrganisation):
            if not org.kbo_number:
                return org, None
            try:
                kbo = await fetch_company(org.kbo_number)
                return org, kbo
            except Exception:
                return org, None

        results = await asyncio.gather(*[safe_kbo(o) for o in orgs])
        orgs_with_kbo = list(results)
    else:
        orgs_with_kbo = [(o, None) for o in orgs]

    overlaps = _detect_overlaps(orgs_with_kbo) if include_mandataries else []

    return NoticeDetailOut(
        publication_number=publication_number,
        organisations=[_to_out(o, k) for o, k in orgs_with_kbo],
        overlaps=overlaps,
    )
