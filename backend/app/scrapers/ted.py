"""
TED (Tenders Electronic Daily) API client
Docs: https://ted.europa.eu/api/v3.0/
"""
import httpx
from typing import Optional
from app.models.tender import Tender

TED_API_BASE = "https://api.ted.europa.eu/v3"
# Geen API key nodig voor publieke endpoints; optioneel voor hogere rate limits


def _parse_tender(notice: dict) -> Optional[Tender]:
    try:
        nid = notice.get("publicationNumber", "")
        title_obj = notice.get("title") or {}
        title = (
            title_obj.get("NLD")
            or title_obj.get("FRA")
            or next(iter(title_obj.values()), "Onbekend")
        )
        authority = notice.get("buyer", {}).get("officialName", "Onbekend")
        pub_date = notice.get("publicationDate")  # "YYYY-MM-DD"
        deadline = (notice.get("submissionDeadlineDate") or "").split("T")[0] or None
        value_obj = notice.get("estimatedValue") or {}
        est_value = value_obj.get("value")
        cpv = (notice.get("cpvCode") or {})
        nuts = (notice.get("placeOfPerformance") or [{}])[0].get("nutsCode")
        url = f"https://ted.europa.eu/en/notice/-/detail/{nid}"

        return Tender(
            id=nid,
            title=title,
            contracting_authority=authority,
            publication_date=pub_date or None,
            deadline=deadline or None,
            estimated_value=est_value,
            cpv_code=cpv.get("code"),
            cpv_description=cpv.get("description"),
            nuts_code=nuts,
            description=None,
            url=url,
            source="TED",
        )
    except Exception:
        return None


async def fetch_belgian_tenders(
    page: int = 1,
    page_size: int = 20,
    query: Optional[str] = None,
    cpv: Optional[str] = None,
    nuts: Optional[str] = None,
) -> tuple[list[Tender], int]:
    """Haal Belgische aanbestedingen op via TED search API."""
    filters = ["BT-09(b)-Procedure in ['BE']"]  # alleen België
    if cpv:
        filters.append(f"CPVCode = '{cpv}'")
    if nuts:
        filters.append(f"BT-728-Place LIKE '{nuts}%'")

    search_query = " AND ".join(filters)
    if query:
        search_query = f"({query}) AND {search_query}"

    payload = {
        "query": search_query,
        "page": page,
        "limit": page_size,
        "fields": [
            "publicationNumber",
            "title",
            "buyer",
            "publicationDate",
            "submissionDeadlineDate",
            "estimatedValue",
            "cpvCode",
            "placeOfPerformance",
        ],
        "sort": [{"field": "publicationDate", "order": "DESC"}],
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{TED_API_BASE}/notices/search", json=payload)
        resp.raise_for_status()
        data = resp.json()

    notices = data.get("notices", [])
    total = data.get("total", 0)
    tenders = [t for n in notices if (t := _parse_tender(n)) is not None]
    return tenders, total
