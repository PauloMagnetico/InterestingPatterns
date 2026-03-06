"""
TED (Tenders Electronic Daily) API client — v3
Docs: https://api.ted.europa.eu/swagger-ui/index.html
"""
import httpx
from typing import Optional
from app.models.tender import Tender

TED_API_BASE = "https://api.ted.europa.eu/v3"

TED_FIELDS = [
    "publication-number",
    "notice-title",
    "buyer-name",
    "publication-date",
    "deadline-date-lot",
    "classification-cpv",
    "place-of-performance",
]


def _pick_lang(obj: dict | None, langs=("nld", "fra", "eng")) -> str | None:
    """Kies de beste taalversie uit een meertalig TED veld."""
    if not obj:
        return None
    for lang in langs:
        values = obj.get(lang)
        if values:
            return values[0] if isinstance(values, list) else values
    # Fallback: eerste beschikbare taal
    for values in obj.values():
        if values:
            return values[0] if isinstance(values, list) else values
    return None


def _pick_lang_all(obj: dict | list | None, langs=("nld", "fra", "eng")) -> list[str]:
    """
    Geeft ALLE waarden terug uit een meertalig TED veld, zodat meerdere kopers
    of winnaars niet worden afgekapt.

    TED kan dit veld op twee manieren structureren:
      - dict  {"nld": ["Stad Gent", "OCMW Gent"], "fra": [...]}
      - list  [{"nld": ["Stad Gent"]}, {"nld": ["OCMW Gent"]}]
    """
    if not obj:
        return []

    # Lijst van meertalige dicts → haal per item de beste taalversie op
    if isinstance(obj, list):
        results = []
        for item in obj:
            v = _pick_lang(item, langs) if isinstance(item, dict) else str(item)
            if v:
                results.append(v)
        return results

    # Enkelvoudige dict → alle waarden per voorkeurstaal, daarna fallback
    for lang in langs:
        values = obj.get(lang)
        if values:
            return values if isinstance(values, list) else [values]
    for values in obj.values():
        if values:
            return values if isinstance(values, list) else [values]
    return []


def _parse_date(raw: str | None) -> str | None:
    """Verwijder tijdzone suffix van TED datumstrings ("2025-01-02+01:00" → "2025-01-02")."""
    if not raw:
        return None
    return raw[:10]


def _parse_tender(notice: dict) -> Optional[Tender]:
    try:
        nid = notice.get("publication-number", "")
        title = _pick_lang(notice.get("notice-title"))
        authority = _pick_lang(notice.get("buyer-name")) or "Onbekend"
        pub_date = _parse_date(notice.get("publication-date"))

        # deadline: kan een lijst zijn per lot
        deadline_raw = notice.get("deadline-date-lot")
        deadline = None
        if isinstance(deadline_raw, list) and deadline_raw:
            deadline = _parse_date(deadline_raw[0])
        elif isinstance(deadline_raw, str):
            deadline = _parse_date(deadline_raw)

        # CPV: eerste code in de lijst
        cpv_list = notice.get("classification-cpv") or []
        cpv_code = cpv_list[0] if cpv_list else None

        # NUTS: filter op BE-codes, neem de meest specifieke
        nuts_list = notice.get("place-of-performance") or []
        be_nuts = [n for n in nuts_list if n.startswith("BE") and n != "BEL"]
        nuts_code = be_nuts[0] if be_nuts else ("BEL" if "BEL" in nuts_list else None)

        # URL: gebruik NL html link als beschikbaar
        links = notice.get("links") or {}
        html_links = links.get("html") or links.get("htmlDirect") or {}
        url = (
            html_links.get("NLD")
            or html_links.get("FRA")
            or html_links.get("ENG")
            or f"https://ted.europa.eu/en/notice/-/detail/{nid}"
        )

        return Tender(
            id=nid,
            title=title or f"Aanbesteding {nid}",
            contracting_authority=authority,
            publication_date=pub_date,
            deadline=deadline,
            estimated_value=None,   # TED v3 geeft waarde enkel in detail-endpoint
            cpv_code=cpv_code,
            cpv_description=None,
            nuts_code=nuts_code,
            description=None,
            url=url,
            source="TED",
        )
    except Exception:
        return None


DETAIL_FIELDS = TED_FIELDS + [
    "winner-name",
    "winner-country",
    "award-value",
    "contract-nature",
]


async def fetch_tender_detail(tender_id: str) -> Optional[dict]:
    """Haal het volledige TED-dossier op via publication-number."""
    payload = {
        "query": f"publication-number={tender_id}",
        "fields": DETAIL_FIELDS,
        "limit": 1,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{TED_API_BASE}/notices/search", json=payload)
        resp.raise_for_status()
        data = resp.json()
    notices = data.get("notices", [])
    return notices[0] if notices else None


async def fetch_belgian_tenders(
    page: int = 1,
    page_size: int = 25,
    query: Optional[str] = None,
    cpv: Optional[str] = None,
    nuts: Optional[str] = None,
) -> tuple[list[Tender], int]:
    """Haal recente Belgische aanbestedingen op via TED Search API."""
    filters = [
        "buyer-country=BEL",
        "publication-date>=20240101",  # enkel recente dossiers
    ]

    if cpv:
        filters.append(f"classification-cpv={cpv}")
    if nuts:
        filters.append(f"place-of-performance={nuts}*")
    if query:
        filters.append(f"notice-title~{query}")

    search_query = " AND ".join(filters)

    payload = {
        "query": search_query,
        "page": page,
        "limit": page_size,
        "fields": TED_FIELDS,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{TED_API_BASE}/notices/search", json=payload)
        resp.raise_for_status()
        data = resp.json()

    notices = data.get("notices", [])
    total = data.get("totalNoticeCount", 0)
    tenders = [t for n in notices if (t := _parse_tender(n)) is not None]
    return tenders, total
