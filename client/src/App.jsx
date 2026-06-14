import { useEffect, useState } from "react";
import { api } from "./api/client";

const START = "2026-03-09";
const END = "2026-03-17";
const EXPECTED = 36; // each local day should have exactly this many events

export default function App() {
  const [series, setSeries] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .getDaily(START, END)
      .then((d) => setSeries(d.series))
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="state error">{error}</div>;
  if (!series) return <div className="state">Loading…</div>;

  const max = Math.max(...series.map((d) => d.count), EXPECTED);

  return (
    <div className="page">
      <header className="head">
        <p className="eyebrow">ANALYTICS · DAILY EVENTS</p>
        <h1>Events per day</h1>
        <p className="sub">
          Expected: a steady {EXPECTED} events on every business day.
        </p>
      </header>

      <div className="chart">
        {series.map((d) => {
          const off = d.count !== EXPECTED;
          const h = Math.round((d.count / max) * 180);
          return (
            <div className="bar-col" key={d.day}>
              <span className={`bar-count ${off ? "off" : ""}`}>{d.count}</span>
              <div
                className={`bar ${off ? "bar-off" : ""}`}
                style={{ height: `${h}px` }}
              />
              <span className="bar-label">{d.day.slice(5)}</span>
            </div>
          );
        })}
      </div>

      <div className="legend">
        <span className="dot ok" /> matches expected&nbsp;&nbsp;
        <span className="dot off" /> off (suspicious)
      </div>
    </div>
  );
}
