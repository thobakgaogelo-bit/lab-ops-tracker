# Lab Operations Tracker

A Streamlit app for University of Johannesburg lab assistants to submit daily
lab maintenance reports, and for team leaders to review them — replacing the
manual Excel-based Daily Lab Maintenance Report. Reports are persisted to a
Supabase (PostgreSQL) database.

## Features

- **Lab Assistant view** — select a venue/lab, log any issues found
  (equipment, category, description, notes), and submit a daily report.
- **Team Leader Dashboard** — see totals, filter reports by venue/lab/date,
  view full report detail, and generate a downloadable text report.

## Tech stack

- [Streamlit](https://streamlit.io/) — UI and app framework
- [Supabase](https://supabase.com/) (PostgreSQL) — persistent storage
- [supabase-py](https://github.com/supabase/supabase-py) — Python client

## Database schema

Run this once in the Supabase SQL Editor for a new project:

```sql
create table if not exists lab_reports (
    id           uuid primary key default gen_random_uuid(),
    created_at   timestamptz not null default now(),
    report_date  date not null,
    venue        text not null,
    lab          text not null,
    staff        text not null,
    status       text not null check (status in ('No Issues', 'Issues Identified')),
    issues       jsonb not null default '[]'::jsonb
);

create index if not exists idx_lab_reports_report_date on lab_reports (report_date desc);
create index if not exists idx_lab_reports_venue_lab   on lab_reports (venue, lab);

alter table lab_reports enable row level security;
```

No RLS policy is required as long as the app connects with the
**service_role** key (see below) — that key bypasses RLS by design.

## Environment variables

| Variable        | Description                                              |
|-----------------|------------------------------------------------------------|
| `SUPABASE_URL`  | Your Supabase project URL (Project Settings → API)         |
| `SUPABASE_KEY`  | Your Supabase **service_role** key (Project Settings → API)|

Never commit these to git. Set them as actual environment variables, or —
in GitHub Codespaces — as [Codespaces secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-encrypted-secrets-for-your-codespaces)
so they're injected automatically on startup.

## Running locally / in Codespaces

```bash
pip install -r requirements.txt

export SUPABASE_URL="https://YOUR-PROJECT-REF.supabase.co"
export SUPABASE_KEY="YOUR-SERVICE-ROLE-KEY"

streamlit run app.py
```

If `SUPABASE_URL`/`SUPABASE_KEY` aren't set, the app still starts, but shows
a warning banner and reports cannot be saved until they're configured.

## Deployment (Render)

`render.yaml` is already configured to deploy this as a web service. In the
Render dashboard, set `SUPABASE_URL` and `SUPABASE_KEY` under the service's
**Environment** tab (they're declared in `render.yaml` but their values are
not stored in git — `sync: false`).

## Data model

Each submitted report is one row in `lab_reports`:

- `venue`, `lab`, `staff`, `report_date`, `status`
- `issues` — a JSON array of `{equipment, category, description, notes}`,
  one entry per issue logged for that report (empty array when status is
  "No Issues")
