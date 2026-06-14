def test_daily_series_is_flat_36():
    series = daily_counts(date(2026,3,10), date(2026,3,17))
    assert [r["count"] for r in series] == [36] * 7
    assert all(r["day"]) != "2026-03-09" for r in series