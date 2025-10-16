Contact Detail AIActionBar — Crash Fix QA Log

Summary
- Root cause: AIActionBar referenced `onScheduleFollowUp` in JSX but did not destructure it from props with a safe default, causing a ReferenceError when the component rendered without that prop.

Files Changed
- aura-client/src/components/contacts/AIActionBar.tsx
  - Added safe default handlers in function args for all actions, including `onScheduleFollowUp`.
  - Ensured the Schedule button uses `onScheduleFollowUp` prop and updated label to "Schedule Follow-Up".
- aura-client/src/pages/contacts/[id].tsx
  - Refactored to define stable handler functions and pass them to AIActionBar.
  - Verified Schedule handler opens the scheduling modal (stubbed) without crashing.

Before
- Visiting `/contacts/:id` could crash with `onScheduleFollowUp is not defined` during render if the prop was not present.

After
- `/contacts/:id` renders reliably.
- AIActionBar shows buttons; clicking Schedule opens the stub modal (or logs if not wired), and other buttons run stubbed async actions.

Next Steps
- Wire `onScheduleFollowUp` to the real `FollowUpModal` flow and persist events via schedules API.
- Consider adding a tiny error boundary around AIActionBar to prevent future action faults from affecting the whole page.

Manual Verification
1) Navigate to `/contacts/1`.
2) Confirm AIActionBar renders.
3) Click "Schedule Follow-Up"; confirm no crash and stub flow triggers (modal/log).
4) Click other actions; confirm stubbed behavior without errors.

