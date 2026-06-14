from zoneinfo import ZoneInfo
from datetime import date, datetime

from .db import get_conn

BUSINESS_TZ = "Australia/Sydney"


def daily_counts(start: date, end: date, tz: str = BUSINESS_TZ):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """SELECT date_trunc('day', occurred_at AT TIME ZONE %(tz)s)::date AS day,
                  count(*)
             FROM events
            WHERE (occurred_at AT TIME ZONE %(tz)s) >= %(start)s
              AND (occurred_at AT TIME ZONE %(tz)s) <  %(end)s
            GROUP BY day
            ORDER BY day""",
        {"tz": tz, "start": start, "end": end},          
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"day": str(r[0]), "count": r[1]} for r in rows]



def counts_for_today(tz: str = BUSINESS_TZ):
    today = datetime.now(timezone.utc).date()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT count(*) FROM events
            WHERE date_trunc('day', occurred_at AT TIME ZONE %(tz)s)::date = %(day)s""",
        {"tz": tz, "day": today},
    )
    n = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"day": str(today), "count": n, "timezone": "tz"}
