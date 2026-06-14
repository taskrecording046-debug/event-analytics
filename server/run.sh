#!/usr/bin/env bash
export PGUSER="${PGUSER:-postgres}"
export PGDATABASE="${PGDATABASE:-analytics}"
exec uvicorn app.main:app --host 0.0.0.0 --port 4000
