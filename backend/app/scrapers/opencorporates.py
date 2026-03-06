"""
OpenCorporates API client voor bedrijfsbestuur lookup.
Docs: https://api.opencorporates.com/documentation/API-Reference
"""
import httpx
from typing import Optional
from app.models.analysis import BoardMember, Organization

OC_BASE = "https://api.opencorporates.com/v0.4"


async def _search_company(name: str) -> Optional[dict]:
    """Zoek een Belgisch bedrijf op naam, geeft het eerste resultaat terug."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                f"{OC_BASE}/companies/search",
                params={"q": name, "jurisdiction_code": "be", "per_page": 1},
            )
            if not resp.is_success:
                return None
            data = resp.json()
            companies = data.get("results", {}).get("companies", [])
            if not companies:
                return None
            return companies[0].get("company")
    except Exception:
        return None


async def _get_company_officers(jurisdiction: str, company_number: str) -> list[dict]:
    """Haal bestuurders op voor een bedrijf via het detail-endpoint."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                f"{OC_BASE}/companies/{jurisdiction}/{company_number}",
                params={"sparse": "false"},
            )
            if not resp.is_success:
                return []
            data = resp.json()
            company = data.get("results", {}).get("company", {})
            raw = company.get("officers") or []
            return [o.get("officer", {}) for o in raw]
    except Exception:
        return []


def _parse_officers(raw_officers: list[dict]) -> list[BoardMember]:
    members = []
    seen = set()
    for o in raw_officers:
        name = (o.get("name") or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        members.append(BoardMember(
            name=name,
            role=o.get("position"),
            nationality=o.get("nationality"),
        ))
    return members


async def lookup_organization(company_name: str) -> Organization:
    """
    Zoek een bedrijf op naam en geef Organization terug met board-leden.
    Valt graceful terug op een lege board als niets gevonden wordt.
    """
    company = await _search_company(company_name)
    if not company:
        return Organization(name=company_name)

    company_number = company.get("company_number")
    jurisdiction = company.get("jurisdiction_code", "be")

    officers = []
    if company_number:
        officers = await _get_company_officers(jurisdiction, company_number)

    return Organization(
        name=company_name,
        company_number=company_number,
        board=_parse_officers(officers),
    )
