# Event Analytics — Timezone Bug (React + FastAPI + PostgreSQL)

A small analytics dashboard: it counts events per day and charts the daily
series. The business operates in Australia/Adelaide, but the starter
version buckets events by UTC date, so events in the local early morning
land on the wrong calendar day. The chart shows a phantom day and a
half-empty day at the edges, and every day's total is built from the wrong
hours.

## Architecture

```
event-analytics/
├── db/
│   ├── schema.sql   # events (occurred_at TIMESTAMPTZ)
│   └── seed.py      # 7 local days, identical shape (36/day), heavy local late-night
├── server/          # FastAPI + psycopg2  (port 4000)
│   └── app/
│       ├── main.py
│       ├── db.py
│       ├── analytics_service.py        # ⚠️ groups by UTC date (the bug)
│       └── analytics_service_fixed.py  # ✅ groups by business time zone
└── client/          # React + Vite     (port 5173)
    └── src/App.jsx  # daily bar chart, off-days highlighted
```

## Requirements

- Python 3.10+, Node.js 18+, PostgreSQL 14+
  - macOS: `brew install python node postgresql@16`

## Setup

```bash
createdb analytics
PGUSER=postgres PGDATABASE=analytics python3 db/seed.py

cd server
pip install -r requirements.txt
PGUSER=postgres PGDATABASE=analytics ./run.sh        # http://localhost:4000

cd client
npm install && npm run dev                            # http://localhost:5173
```

Open http://localhost:5173 — every business day should have exactly 36
events, but the chart shows 2026-03-09 with 24 (a day that shouldn't exist
in the range) and 2026-03-16 with 12.

## The bug, in one line

```sql
-- Adelaide is UTC+10:30, so local early-morning events fall on the
-- previous UTC day:
SELECT date_trunc('day', occurred_at)::date FROM events;                          -- UTC day  (wrong)
SELECT date_trunc('day', occurred_at AT TIME ZONE 'Australia/Adelaide')::date;    -- local day (right)
```
