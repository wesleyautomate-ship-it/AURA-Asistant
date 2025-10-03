# Transaction Workflow

This document describes the end-to-end transaction coordination workflow implemented in the web frontend for PropertyPro AI. It is intended for Beta-4 (Strategy) and Alpha-2 (API) integration.

## Scope
- Timeline generation from contract dates
- Milestone tracking (inspection, appraisal, financing, closing, possession)
- Document management
- Communication templates for milestone updates
- Progress tracking and daily coordination view

## UI Components
- `src/components/TransactionsView.tsx`
  - Master-detail layout listing transactions and a detail view
  - Progress computation and status badges (orange scheme #ea580c)
  - Integrates Timeline, Documents, and future MilestoneTracker
- `src/components/TransactionTimeline.tsx`
  - Sorted timeline view with icons, completion indicator and document counts
- `src/components/DocumentManager.tsx`
  - Web file input (multiple) with preview links and removal
- `src/components/TransactionTemplates.tsx`
  - Modal selector for communication templates, filtered by milestone
- `src/utils/transactionUtils.ts`
  - `generateMilestonesFromContract(seed)` generates milestones from a contract date with sensible offsets
  - `computeProgress(tx)` calculates completion percentage

## Data Contracts
- Transactions shape is defined in `src/types.ts`: `Transaction`, `TransactionMilestone`, `TransactionDocument`, `TransactionTemplate`.
- Mock data provided in `src/constants.tsx` under `MOCK_TRANSACTIONS`.

## Timeline Generation
Use `generateMilestonesFromContract({ contractSignedDate: 'YYYY-MM-DD' })` from `src/utils/transactionUtils.ts` to scaffold milestones at the time a contract is executed. Offsets can be customized per market/regulation.

```ts
import { generateMilestonesFromContract } from '@/utils/transactionUtils';

const milestones = generateMilestonesFromContract({ contractSignedDate: '2025-10-01' });
```

## Milestone Communications
`src/components/TransactionTemplates.tsx` includes default templates for:
- Offer Submitted
- Inspection Scheduled
- Closing Instructions

Tokens supported: `{{clientName}}`, `{{propertyTitle}}`, `{{offerAmount}}`, `{{inspectionDate}}`, etc.

## Daily Workflow
- Agents can scan the list, view progress bars, and open a transaction.
- Timeline highlights due dates and completion.
- DocumentManager supports quick uploads for contracts, disclosures, and photos.
- Templates modal provides rapid communication drafts.

## Integrations
- Client and property data can be merged by joining `transaction.clientId` and `transaction.propertyId` with CRM and property stores.
- Alpha-2 endpoints to be used when available:
  - `GET /api/v1/transactions` — list transactions
  - `POST /api/v1/transactions` — create transaction (use milestone generator)
  - `PATCH /api/v1/transactions/:id` — update milestones/documents/status

## Color & UX
- Primary accent for transactions and workflow: orange `#ea580c`.
- Progress bars, buttons, and badges align with this scheme.

## Next Steps for Beta-4
- Consume `MOCK_TRANSACTIONS` or API data to generate strategy summaries.
- Leverage `computeProgress` to prioritize at-risk transactions (low completion, near due dates).
- Use templates to orchestrate automated communications.
