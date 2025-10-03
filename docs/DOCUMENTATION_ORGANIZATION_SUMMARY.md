# Documentation Organization Summary

This summary explains where to find authoritative information across the PropertyPro AI repository. It replaces the legacy structure and points to the new canonical handbook produced in October 2025.

## Core Sources
- `docs/handbook/README.md` — Table of contents for the backend, frontend, and platform handbooks.
- `docs/handbook/backend.md` — Detailed backend architecture, routers, domain services, data flow, and security posture.
- `docs/handbook/frontend.md` — Web and mobile client architecture, shared packages, testing, and UX guidelines.
- `docs/handbook/platform.md` — Data, AI, infrastructure, monitoring, governance, and operations playbook.

## Progress & Planning
- `docs/progress/release-readiness.md` — Stage gate tracker for releases; update status, owner, and evidence per milestone.
- `docs/progress/dev-journal.md` — Running log for sprint updates, blockers, decisions.
- `docs/ImplementationPlan/` — Historical execution plans now aligned with current roadmap (see updated README).

## Specialized References
- `docs/api-endpoints.md` — Quick reference of REST/WebSocket endpoints.
- `docs/CONTENT_GENERATION_GUIDE.md` — Updated AI content generation and prompt guidance.
- `docs/business/` — Product strategy, phased go-to-market plans, and stakeholder briefs.
- `docs/AuditReports/` — Prior audit artifacts retained for compliance history (read-only unless reprised).

## How To Maintain Documentation
1. Update the relevant handbook section when you introduce or modify features.
2. Link new artifacts from this summary so future contributors can discover them quickly.
3. Archive obsolete documents by removing them or moving to an `/archive` folder with a pointer back to current sources.
4. Note documentation updates in PR descriptions and the dev journal for traceability.
5. Conduct quarterly documentation reviews alongside architecture reviews.

## Quick Links For Onboarding
- Start with `docs/handbook/README.md` for architecture context.
- Follow with `docs/api-endpoints.md` when integrating new features.
- Record sprint outcomes in `docs/progress/dev-journal.md`.
- Coordinate release readiness in `docs/progress/release-readiness.md`.

Keeping documentation organized around these pillars ensures engineers, designers, and operators share the same source of truth while iterating on PropertyPro AI.
