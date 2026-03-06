"""
KBO Public Search scraper
Haalt mandatarissen (bestuurders, dagelijks bestuur, ...) op per ondernemingsnummer.
Bron: https://kbopub.economie.fgov.be/kbopub/toonondernemingps.html
"""
import re
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional

KBO_BASE = "https://kbopub.economie.fgov.be/kbopub"
_SINCE_RE = re.compile(r"Sinds\s+(.+)", re.IGNORECASE)


@dataclass
class Mandatary:
    role: str               # "Bestuurder", "Persoon belast met dagelijks bestuur", ...
    name: str               # "Leeman, Bert"
    first_name: str
    last_name: str
    since: Optional[str]    # "4 juni 2019"


@dataclass
class KboCompany:
    kbo_number: str         # "0887229108"
    name: Optional[str]
    status: Optional[str]   # "Actief" / "Gestopt"
    legal_form: Optional[str]
    mandataries: list[Mandatary]


def _parse_name(raw: str) -> tuple[str, str]:
    """'Leeman ,  Bert' → ('Leeman', 'Bert')"""
    parts = [p.strip() for p in raw.split(",", 1)]
    last = parts[0] if parts else raw
    first = parts[1] if len(parts) > 1 else ""
    return last, first


def _parse_mandataries(soup: BeautifulSoup) -> list[Mandatary]:
    html = str(soup)
    idx = html.find("Functies")
    if idx == -1:
        return []

    functies_html = html[idx:]
    functies_soup = BeautifulSoup(functies_html, "lxml")

    mandataries = []
    for row in functies_soup.find_all("tr"):
        cells = [td.get_text(separator=" ", strip=True) for td in row.find_all("td")]
        if len(cells) < 2:
            continue

        role = cells[0]
        name_raw = cells[1]

        # Stop bij een nieuwe sectieheader (h2 in td)
        if row.find("h2"):
            break
        if not name_raw or not role:
            continue
        # Filter lege/onnodige rijen
        if name_raw.strip() in ("", "\xa0") or "geen gegevens" in name_raw.lower():
            continue

        since = None
        if len(cells) >= 3:
            m = _SINCE_RE.search(cells[2])
            since = m.group(1) if m else cells[2] or None

        last, first = _parse_name(name_raw)
        mandataries.append(Mandatary(
            role=role,
            name=f"{first} {last}".strip(),
            first_name=first,
            last_name=last,
            since=since,
        ))

    return mandataries


async def fetch_company(kbo_number: str) -> KboCompany:
    """
    Haal bedrijfsinfo + mandatarissen op voor een KBO-nummer.
    kbo_number: enkel cijfers, bijv. '0887229108'
    """
    clean = kbo_number.replace(".", "").replace(" ", "").lstrip("BE").lstrip("be")
    url = f"{KBO_BASE}/toonondernemingps.html?lang=nl&ondernemingsnummer={clean}"
    headers = {"Accept-Language": "nl-BE,nl;q=0.9"}

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        # Establish session (JSESSIONID) before querying company page
        await client.get(f"{KBO_BASE}/zoeken.html?lang=nl", headers=headers)
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # Basisinfo uit de Algemeen tabel
    name = status = legal_form = None
    for row in soup.find_all("tr"):
        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) >= 2:
            label, value = cells[0], cells[1]
            if "naam" in label.lower():
                name = value
            elif label.strip() == "Status:":
                status = value.split("Sinds")[0].strip()
            elif "rechtsvorm" in label.lower():
                legal_form = value.split("Sinds")[0].strip()

    mandataries = _parse_mandataries(soup)

    return KboCompany(
        kbo_number=clean,
        name=name,
        status=status,
        legal_form=legal_form,
        mandataries=mandataries,
    )
