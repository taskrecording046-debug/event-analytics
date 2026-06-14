#!/usr/bin/env python3
"""Seed the event analytics DB with data that exposes a timezone-grouping bug.

Run:  python db/seed.py   (with PG env vars set)

The business operates in Australia/Adelaide (UTC+10:30). Each LOCAL day has
a steady daytime baseline PLUS a heavy late-night block between 00:00 and
02:00 local time. In UTC, Adelaide local 00:00-02:00 maps to ~13:30-15:30
on the PREVIOUS UTC day, so a report that groups by UTC date pushes each
local day's early-morning traffic onto the day before.

The data is fully deterministic: every local day has exactly the same
shape, so the correct per-local-day count is a constant. A UTC-based
report instead shows a sawtooth that is wrong on every single day.
"""
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import psycopg2

LOCAL_TZ = ZoneInfo("Australia/Adelaide")
UTC = ZoneInfo("UTC")

EVENT_TYPES = ["signup", "purchase", "login"]
SOURCES = ["web", "ios", "android"]

START_LOCAL_DATE = datetime(2026, 3, 10).date()
NUM_DAYS = 7

# Events per local hour. The 00:00-01:00 block is heavy and lands on the
# PREVIOUS day in UTC, which is what a UTC-grouped report misattributes.
HOURLY_PLAN = {
    0: 10, 1: 10,            # heavy local late-night -> previous UTC day
    9: 4, 12: 4, 15: 4, 18: 4,
}


def main():
    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
        dbname=os.environ.get("PGDATABASE", "analytics"),
    )
    conn.autocommit = True
    cur = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
        cur.execute(f.read())
    print("Schema created.")

    total = 0
    per_local_day = {}
    for day_offset in range(NUM_DAYS):
        local_date = START_LOCAL_DATE + timedelta(days=day_offset)
        day_count = 0
        for hour, n in HOURLY_PLAN.items():
            for i in range(n):
                minute = (i * 6) % 60
                local_dt = datetime(
                    local_date.year, local_date.month, local_date.day,
                    hour, minute, tzinfo=LOCAL_TZ,
                )
                occurred_at = local_dt.astimezone(UTC)
                etype = EVENT_TYPES[(hour + i) % len(EVENT_TYPES)]
                source = SOURCES[(hour + i) % len(SOURCES)]
                cur.execute(
                    "INSERT INTO events (event_type, source, occurred_at) "
                    "VALUES (%s, %s, %s)",
                    (etype, source, occurred_at),
                )
                total += 1
                day_count += 1
        per_local_day[str(local_date)] = day_count

    print(f"Inserted {total} events across {NUM_DAYS} local days.")
    print("Expected per-LOCAL-day counts (Australia/Adelaide):")
    for d, c in per_local_day.items():
        print(f"  {d}: {c}")

    cur.close()
    conn.close()
    print("Seed complete.")


if __name__ == "__main__":
    main()
