"""Event analytics API.

GET /api/daily?start=YYYY-MM-DD&end=YYYY-MM-DD  — per-day event counts.
GET /api/today                                   — count for 'today'.
GET /api/health
"""
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .analytics_service import daily_counts, counts_for_today

app = FastAPI(title="Event Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/daily")
def daily(start: str = "2026-03-01", end: str = "2026-04-01"):
    return {
        "start": start,
        "end": end,
        "series": daily_counts(date.fromisoformat(start), date.fromisoformat(end)),
    }


@app.get("/api/today")
def today():
    return counts_for_today()
