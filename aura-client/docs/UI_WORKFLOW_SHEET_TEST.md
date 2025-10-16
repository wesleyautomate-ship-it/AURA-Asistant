# AI Workflow Bottom Sheet – Test Checklist

This checklist verifies the AI Workflow Bottom Sheet behavior on the Dashboard (mobile-first):

- Opens above navbar: Tap the "AI Workflow" tile and confirm the sheet sits above the bottom navbar (z-index higher).
- Backdrop visible: Semi-transparent scrim (black/40) is displayed behind the sheet.
- No body scroll: Attempt to scroll the background content while the sheet is open – the page should not scroll.
- Close via Esc: Press Escape to close the sheet.
- Close via scrim: Tap on the scrim to close the sheet.
- Safe area padding: Bottom padding accounts for iOS safe-area using env(safe-area-inset-bottom).
- Focus trap: Tab/Shift+Tab cycles focus within the sheet content; Esc closes.
- Keyboard-safe: On Android, opening the keyboard should not push content under the keyboard.
- No black void: The sheet has a white background; scrim uses semi-transparent overlay.
- Animation: Scrim fades ~240ms; Sheet slides up with cubic-bezier easing over ~320ms.

Optional
- Drag to close: Drag the sheet downward. If the drag exceeds ~25% of sheet height, it should close.

Accessibility
- Quick Lighthouse/axe pass for basic a11y issues.

Notes
- The Dashboard remains a single, non-scrolling page. The sheet provides interaction without changing underlying layout.
- The tile is placed early in the core cards row to be visible on first screen on mobile.

