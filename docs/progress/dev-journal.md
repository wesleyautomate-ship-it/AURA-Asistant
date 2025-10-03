# Development Journal

Log sprint updates, architectural decisions, and follow-ups here. Create a new entry for each working session so history stays centralized.

## Template
```
## YYYY-MM-DD — Sprint / Workstream Name
- Focus:
- Key changes merged:
- Blockers / Risks:
- Decisions:
- Next actions:
```

## Entries
*No entries yet. Add the first update after your next working session.*
## 2025-10-02 - Workspace Stabilization Sprint
- Focus: Replace marketing demo data with live backend wiring and publish CI coverage artefacts.
- Key changes merged: MarketingView web/mobile now use property store data with campaign APIs; marketing service normalized responses; CI uploads pytest coverage and Playwright HTML reports.
- Blockers / Risks: Lower environments still require seeded listings; coverage HTML may grow if not pruned after 14-day retention.
- Decisions: Alembic onboarding workshop booked for 2025-10-07 09:00 GST with Platform and Data co-hosts.
- Next actions: Coordinate property seed data refresh before next smoke run; monitor CI runtime impact from coverage uploads.
