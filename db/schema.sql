-- Event analytics schema.
-- Each event records WHAT happened and WHEN, as an absolute instant.
--
-- `occurred_at` is TIMESTAMPTZ (timestamp with time zone) — the correct
-- choice: it stores an absolute point in time (internally UTC), not a
-- wall-clock string. The bug in this tutorial is NOT in the storage; it is
-- introduced later when the application groups these instants into
-- "days" using the wrong time zone.

DROP TABLE IF EXISTS events;

CREATE TABLE events (
  id           BIGSERIAL PRIMARY KEY,
  event_type   TEXT NOT NULL,         -- e.g. 'signup', 'purchase', 'login'
  source       TEXT NOT NULL,         -- e.g. 'web', 'ios', 'android'
  occurred_at  TIMESTAMPTZ NOT NULL   -- absolute instant the event happened
);

CREATE INDEX idx_events_occurred_at ON events(occurred_at);
CREATE INDEX idx_events_type ON events(event_type);
