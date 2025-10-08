# Aura Command Center – v2.6.4 Animation & Motion Spec (Audio-Inspired Waveform)

Aligned with the visual reference: a centered, symmetric waveform around a baseline (studio-style recording UI).

---

## 1) Waveform Structure

Goal: Recreate a centered, symmetric waveform where bars rise and fall around a baseline, producing a calm, professional recording feel.

Geometry

- Bars count: 24–28
- Bar width: 2.5–3px
- Horizontal spacing: 5–6px
- Baseline: centered vertically within a 60–80px container
- Height (idle): 8px total (4px above + 4px below)
- Height (active): 12–42px total (6–21px per side)
- Shape: rounded ends (border-radius: 2px)
- Layout: horizontal flex, justify-center
- Color: gradient #1E2A78 → #3C4EF5 (e.g., from-indigo-700 to-blue-500)
- Optional shadow: drop-shadow(0 1px 2px rgba(60,78,245,0.25))

---

## 2) Waveform Animation Behavior

Idle

- Static bars at baseline height; no motion
- Subtle fade on the entire waveform (opacity 0.8 → 1 → 0.8, 3s loop)

Listening (Recording)

- Each bar animates vertically to random/mic-driven heights, symmetric about the center line
- Motion is smooth and liquid—neighboring bars update with slight phase offsets
- Upper and lower halves mirror exactly
- Use mic amplitude if available; otherwise random mock values

Paused

- Freeze at current heights (no reset)

Thinking / Responding

- Fade waveform to 0.6 opacity
- Reduce amplitude range by ~70% (gentle idle pulse)

---

## 3) Timing & Dynamics

- Target: 60 FPS
- Animation period per bar: 0.8–1.0s
- Delay offset per bar: i * 0.03s
- Easing: easeInOutSine
- Amplitude range per side: ±4px (quiet) → ±20px (loud)
- Phase offset variance: ±0.02s
- Smooth interpolation of amplitude changes—no jumps
- Opacity modulation: [0.8, 1, 0.8] in idle

Example (Framer Motion)

```tsx
<motion.div
  key={i}
  className="w-[3px] bg-indigo-500 rounded-full"
  animate={{
    height: phase === 'listening' ? [8, 32, 12, 40, 10] : 8,
    y: phase === 'listening' ? [0, -10, 0, 10, 0] : 0
  }}
  transition={{
    duration: 0.9,
    repeat: phase === 'listening' ? Infinity : 0,
    ease: 'easeInOutSine',
    delay: i * 0.03
  }}
/>
```

---

## 4) Button Animation Specs

- Mic (Start): circular 48px, gradient blue→purple; scale-in 1.05, subtle pulsing ring
- Pause: circular 48px, Yellow #FBBF24; hover bounce 1.05
- Stop: circular 56px, Red #EF4444; press shrink 0.95
- Send: circular 48px, gradient blue→purple; slide-in + fade-up on appear

Interaction Timing

- Hover: 0.15s cubic-bezier(0.22,1,0.36,1)
- Tap: 0.2s shrink-bounce
- Send entrance: opacity 0 → 1, translateY 12px → 0px, 0.3s

---

## 5) Panel Transitions

- Open: slide up (translateY 60px → 0), fade-in 0 → 1, 0.5s easeOutCubic
- Close: fade-out + translateY +40px, 0.4s easeInCubic
- Mode switch: crossfade content (0.25s linear)

---

## 6) Implementation Notes

Dual-bar render technique: each bar renders as upper and lower halves mirrored around the center line. Keep both halves synchronized and animate heights via mic amplitude or a mock sine/random generator.

---

## 7) Overall Feel

- Minimal and data-driven—never purely decorative
- Stable baseline symmetry for a pro recording aesthetic
- Smooth, fluid motion; no jitter or overshoot
- Tactile button animations
- Maintain 60 FPS; prefer GPU-friendly transforms and lightweight height animations

---

## File Update Summary

- src/components/ui/VoiceUI.tsx (implemented within CommandCenter.tsx in this codebase): replace waveform with symmetric line logic
- src/components/ui/CommandCenter.tsx: ensure bottom spacing ~1rem
- docs/design/animation-specs-v2.6.4.md: this file

---

## Changelog Snippet

```
[v2.6.4]
Aligned waveform animation to studio-style "Simple Audio UI":
- Symmetric bar waveform around baseline
- Static until recording begins
- Realistic amplitude reactivity (mic or mock)
- Icon-only controls with tactile feedback
- Tighter layout near BottomNav
```
