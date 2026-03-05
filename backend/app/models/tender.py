from pydantic import BaseModel
from typing import Optional
from datetime import date


class Tender(BaseModel):
    id: str
    title: str
    contracting_authority: str
    publication_date: Optional[date]
    deadline: Optional[date]
    estimated_value: Optional[float]
    currency: Optional[str] = "EUR"
    cpv_code: Optional[str]
    cpv_description: Optional[str]
    nuts_code: Optional[str]        # regio (bijv. BE2 = Vlaanderen)
    description: Optional[str]
    url: str
    source: str                     # "TED" | "eNotification"


class TenderList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[Tender]
