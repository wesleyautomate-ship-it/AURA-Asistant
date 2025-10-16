Brochure Drafts E2E QA Summary

Scope

- Draft data model + light store
- Editor wizard (Property, Content, Branding, Review)
- Generation flow (HTML + mock PDF)
- Preview page with actions
- Requests stub integration

Devices / Layout

- iPhone 12/13 (390x844): Editor and Preview fit with sticky footers, safe-area respected
- Android 360x800: Content scroll remains minimal; sticky footer stays visible

Test Runs

- Create Draft via Templates
  - Select template → Use Template → navigates to /ai-workflow/brochure/editor/:draftId
  - Draft appears in AI Workflow > Recent Drafts

- Editor Steps
  - Property: search + select from seeded listings, Next disabled until propertyId set
  - Content: fields prefilled from listingData; changes auto-save (300ms debounce), shows Saved tick
  - Branding: pick logo (file), set colors; auto-save (300ms debounce), shows Saved tick
  - Review: summary visible; Generate triggers status=generating → ready or error with Retry

- Generation
  - generateBrochureHTML returns branded HTML using draft data
  - exportBrochurePDF returns mock object URL
  - On success, navigates to Preview

- Preview Actions
  - HTML renders in iframe safely (sandboxed)
  - Download PDF enabled when pdfUrl present
  - Share uses Web Share API or copies URL
  - Save to Requests performs stub POST, local mirror, toast with link to /requests

Safe Areas / FAB

- Editor container uses min-h-[100dvh], padding includes env(safe-area-inset-bottom)
- Sticky footers avoid overlap with any FAB; toast positioned above footers

Dark Mode

- Surfaces and text contrast verified for Editor/Preview cards and footers

Screenshots (placeholders)

- editor_property.png
- editor_content.png
- editor_branding.png
- editor_review.png
- preview_actions.png

Final File List

- aura-client/src/types/brochure.ts
- aura-client/src/store/brochureDraftStore.ts
- aura-client/src/services/brochureDrafts.ts
- aura-client/src/services/brochureEngine.ts
- aura-client/src/services/requestsApi.ts
- aura-client/src/pages/ai-workflow/brochure.tsx (wiring Use Template)
- aura-client/src/pages/ai-workflow/brochure/Editor.tsx
- aura-client/src/pages/ai-workflow/brochure/Preview.tsx
- aura-client/src/pages/ai-workflow/index.tsx (Recent Drafts list)
- aura-client/src/routes/index.tsx (editor/preview routes)

