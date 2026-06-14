"""Daily analytics — STARTER VERSION (contains the timezone bug).

⚠️ This module buckets events into "days" by truncating the absolute
timestamp directly, which truncates in UTC. The business operates in
Australia/Adelaide, so events in the local early morning (which are the
previous day's date in UTC) get counted on the wrong day. Daily totals are
wrong near the midnight boundary, and "today" is computed from the
server/UTC clock rather than the business time zone.

See analytics_service_fixed.py for the corrected version.
"""
from datetime import datetime, timezone, date

from .db import get_conn


def daily_counts(start: date, end: date):
    """Return per-day event counts between start and end (inclusive)."""
    conn = get_conn()
    cur = conn.cursor()

    # ⚠️ date_trunc on a timestamptz truncates in UTC, so each bucket is a
    # UTC calendar day — not an Adelaide one.
    cur.execute(
        """SELECT date_trunc('day', occurred_at)::date AS day, count(*)
             FROM events
            WHERE occurred_at >= %s AND occurred_at < %s
            GROUP BY day
            ORDER BY day""",
        (start, end),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"day": str(r[0]), "count": r[1]} for r in rows]


def counts_for_today():
    """Count events that happened 'today'."""
    # ⚠️ 'today' is taken from the server clock in UTC, not the business
    # time zone, so the window is the wrong 24 hours.
    today = datetime.now(timezone.utc).date()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT count(*) FROM events
            WHERE date_trunc('day', occurred_at)::date = %s""",
        (today,),
    )
    n = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"day": str(today), "count": n, "timezone": "UTC"}
