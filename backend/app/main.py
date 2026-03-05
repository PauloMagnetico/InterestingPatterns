from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tenders

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


@app.get("/")
def root():
    return {"status": "ok", "message": "InterestingPatterns API"}
