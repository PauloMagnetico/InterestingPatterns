from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tenders, notices
from app.scrapers.kbo import fetch_company

app = FastAPI(
    title="InterestingPatterns API",
    description="Openbare aanbestedingen in België - we tonen enkel interessante patronen",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenders.router, prefix="/tenders", tags=["tenders"])
app.include_router(notices.router, prefix="/notices", tags=["notices"])


@app.get("/kbo/{kbo_number}", tags=["kbo"])
async def get_kbo(kbo_number: str):
    """Haal bedrijfsinfo en mandatarissen op via KBO-nummer."""
    try:
        company = await fetch_company(kbo_number)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"KBO ophalen mislukt: {e}")
    return {
        "kbo_number": company.kbo_number,
        "name": company.name,
        "status": company.status,
        "legal_form": company.legal_form,
        "mandataries": [
            {
                "role": m.role,
                "name": m.name,
                "first_name": m.first_name,
                "last_name": m.last_name,
                "since": m.since,
            }
            for m in company.mandataries
        ],
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "InterestingPatterns API"}
