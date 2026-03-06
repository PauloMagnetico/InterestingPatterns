from pydantic import BaseModel
from typing import Optional


class BoardMember(BaseModel):
    name: str
    role: Optional[str] = None
    nationality: Optional[str] = None


class Organization(BaseModel):
    name: str
    company_number: Optional[str] = None
    board: list[BoardMember] = []


class BoardOverlap(BaseModel):
    person_name: str
    organizations: list[str]


class TenderAnalysis(BaseModel):
    tender_id: str
    contracting_authority: Organization
    awarded_parties: list[Organization] = []
    board_overlaps: list[BoardOverlap] = []
    note: Optional[str] = None
