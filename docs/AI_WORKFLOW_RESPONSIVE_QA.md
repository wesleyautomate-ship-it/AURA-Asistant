AI Workflow Responsive QA Checklist

- Target: iPhone 12/13 (390x844)
- Page: `aura-client/src/pages/ai-workflow/index.tsx`

What to verify

- Header is compact: title `text-base`, subtitle `text-xs`, minimal vertical padding.
- Grid shows all three cards on first screen, no scroll.
- Grid: 2 columns, third card spans full width on mobile; uses gap-3.
- Cards use compact variant: `rounded-2xl`, `shadow-md`, `p-3`, `h-[118px]`, tight spacing.
- Icons are smaller with `opacity-80`; titles `text-[15px]`, subtitles `text-[12px]`, line-clamp-2.
- Tap targets are >= 44px (cards exceed 44px height).
- FAB does not overlap last row; bottom padding `pb-[calc(64px+env(safe-area-inset-bottom))]` applied.
- Safe areas respected (uses `env(safe-area-inset-*)`).
- Dark mode: text and surfaces remain legible.

Additional checks

- Global body remains scrollable elsewhere; this page content fits within `min-h-[100dvh]` without scrolling.
- Smaller Android (360x800): still no scroll; if borderline, compact styling keeps under 10% scroll.

Notes

- Mobile uses compact; at `sm` breakpoint, cards fall back to regular aspect and padding.
