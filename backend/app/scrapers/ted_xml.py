"""
TED XML parser — haalt alle betrokken organisaties op uit een notice,
inclusief hun KBO-nummers en rollen (buyer / tenderer / winner).
"""
import re
import httpx
from xml.etree import ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}

_KBO_RE = re.compile(r"(?:BE\s*)?(\d[\d.]{8,11})")


def _clean_kbo(raw: str) -> Optional[str]:
    """'BE 0475.480.736', 'BE 0887229108', or bare '0415962823' → '0415962823'"""
    if not raw:
        return None
    m = _KBO_RE.search(raw)
    if not m:
        return None
    cleaned = m.group(1).replace(".", "").replace(" ", "").zfill(10)
    # Must be exactly 10 digits to be a valid KBO number
    if not cleaned.isdigit() or len(cleaned) != 10:
        return None
    return cleaned


def _text(el, path: str) -> Optional[str]:
    found = el.find(path, NS)
    return found.text.strip() if found is not None and found.text else None


@dataclass
class TedOrganisation:
    internal_id: str          # ORG-0001
    name: str
    kbo_number: Optional[str] # 10-cijferig, bijv. "0887229108"
    kbo_raw: Optional[str]    # origineel uit XML, bijv. "BE 0887.229.108"
    city: Optional[str]
    country: Optional[str]
    email: Optional[str]
    roles: list[str] = field(default_factory=list)   # ["buyer","tenderer","winner"]
    awarded_amounts: list[float] = field(default_factory=list)


def _parse_organisations(root: ET.Element) -> dict[str, TedOrganisation]:
    """Bouw een map van internal_id → TedOrganisation."""
    orgs: dict[str, TedOrganisation] = {}

    for org_el in root.findall(".//efac:Organization", NS):
        company = org_el.find("efac:Company", NS)
        if company is None:
            continue

        internal_id = _text(company, "cac:PartyIdentification/cbc:ID")
        if not internal_id:
            continue

        name = _text(company, "cac:PartyName/cbc:Name") or "Onbekend"
        kbo_raw = _text(company, "cac:PartyLegalEntity/cbc:CompanyID")
        kbo_number = _clean_kbo(kbo_raw) if kbo_raw else None

        addr = company.find("cac:PostalAddress", NS)
        city = _text(addr, "cbc:CityName") if addr is not None else None
        country = _text(addr, "cac:Country/cbc:IdentificationCode") if addr is not None else None

        contact = company.find("cac:Contact", NS)
        email = _text(contact, "cbc:ElectronicMail") if contact is not None else None

        orgs[internal_id] = TedOrganisation(
            internal_id=internal_id,
            name=name,
            kbo_number=kbo_number,
            kbo_raw=kbo_raw,
            city=city,
            country=country,
            email=email,
        )

    return orgs


def _assign_roles(root: ET.Element, orgs: dict[str, TedOrganisation]) -> None:
    """Voeg rollen toe: buyer, tenderer, winner."""

    # Buyers via cac:ContractingParty
    for cp in root.findall(".//cac:ContractingParty", NS):
        for id_el in cp.findall(".//cac:PartyIdentification/cbc:ID", NS):
            org_id = id_el.text
            if org_id in orgs and "buyer" not in orgs[org_id].roles:
                orgs[org_id].roles.append("buyer")

    # TenderingParty → tenderer org mapping (TPA-id → ORG-id)
    tpa_to_org: dict[str, str] = {}
    for tp in root.findall(".//efac:TenderingParty", NS):
        tpa_id = _text(tp, "cbc:ID")
        for tenderer in tp.findall("efac:Tenderer", NS):
            org_id = _text(tenderer, "cbc:ID")
            if tpa_id and org_id:
                tpa_to_org[tpa_id] = org_id
                if org_id in orgs and "tenderer" not in orgs[org_id].roles:
                    orgs[org_id].roles.append("tenderer")

    # Winners: LotTender met PayableAmount verwijst naar TenderingParty
    for lot_tender in root.findall(".//efac:LotTender", NS):
        amount_el = lot_tender.find("cac:LegalMonetaryTotal/cbc:PayableAmount", NS)
        tpa_ref = _text(lot_tender.find("efac:TenderingParty", NS), "cbc:ID") if lot_tender.find("efac:TenderingParty", NS) is not None else None

        if amount_el is not None and tpa_ref and tpa_ref in tpa_to_org:
            org_id = tpa_to_org[tpa_ref]
            if org_id in orgs:
                org = orgs[org_id]
                if "winner" not in org.roles:
                    org.roles.append("winner")
                try:
                    org.awarded_amounts.append(float(amount_el.text))
                except (ValueError, TypeError):
                    pass


async def fetch_notice_organisations(publication_number: str) -> list[TedOrganisation]:
    """
    Haal alle organisaties op uit de XML van een TED notice.
    publication_number bijv. '1573-2024'
    """
    url = f"https://ted.europa.eu/en/notice/{publication_number}/xml"
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    root = ET.fromstring(resp.text)
    orgs = _parse_organisations(root)
    _assign_roles(root, orgs)
    return list(orgs.values())
