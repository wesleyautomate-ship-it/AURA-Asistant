# Track 4: Quick Start Guide 🚀

## What We've Done So Far

### ✅ Phase 1: COMPLETE
- Created `ProgressTracker.tsx` component with 3 variants:
  - Full tracker with steps
  - Compact progress bar
  - Progress badge for tiles

- Updated `CommandCenter.tsx` with:
  - New orchestrator imports
  - Pipeline progress state variables

---

## What's Next: 3 Simple Steps

### Step 1: Complete CommandCenter Integration (1-2 hours)

**Files to Edit**: `src/components/ui/CommandCenter.tsx`

**Actions**:
1. Add progress polling functions (copy from integration guide)
2. Replace `orchestrateCommand` with `generateContent` in voice mode
3. Replace `orchestrateCommand` with `generateContent` in text mode
4. Add `<ProgressTracker />` to the UI
5. Add cleanup for progress polling

**Result**: Users will see real-time pipeline progress!

---

### Step 2: Enhance Request Tiles (30 min)

**Files to Edit**: `src/components/ui/RequestItem.tsx`

**Actions**:
1. Add retry button for failed requests
2. Show progress badge for in-progress requests
3. Add collapsible enrichment sources section
4. Add collapsible generation logs section

**Result**: Users can see why fields were auto-filled and retry failed requests!

---

### Step 3: Add Error Dialog (30 min)

**Files to Create**: `src/components/ui/ErrorDialog.tsx`

**Actions**:
1. Create error dialog component (copy from integration guide)
2. Add error dialog to CommandCenter
3. Show helpful suggestions when errors occur

**Result**: Better error handling with actionable suggestions!

---

## Testing (1 hour)

### Quick Test Scenarios

1. **Full Input Test**:
   ```
   "Create a CMA report for 123 Main St, Seattle with 5 comps"
   ```
   Expected: Progress shows → Content generates → Success

2. **Minimal Input Test** (Tests Enrichment):
   ```
   "CMA for downtown Seattle"
   ```
   Expected: Progress shows → Auto-fills missing fields → Success

3. **Error Test** (Disconnect backend):
   ```
   "Create a CMA"
   ```
   Expected: Progress shows → Graceful fallback → Error dialog

4. **Retry Test**:
   - Trigger an error
   - Click retry button
   - Should regenerate content

---

## Quick Reference

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `ProgressTracker.tsx` | Progress UI | ✅ Done |
| `CommandCenter.tsx` | Main integration | ⏳ In Progress |
| `RequestItem.tsx` | Request tiles | ⏳ Todo |
| `ErrorDialog.tsx` | Error handling | ⏳ Todo |
| `commandStore.ts` | Store updates | ⏳ Todo |

### Key Functions

```tsx
// NEW: Generate content with pipeline
generateContent({ userInput, requestId })

// NEW: Get real-time status
getGenerationStatus(requestId)

// NEW: Retry failed generation
retryGeneration(requestId)

// NEW: Cancel in-progress
cancelGeneration(requestId)
```

### Pipeline Steps

1. **Normalizing** (20%) - Understanding request
2. **Validating** (40%) - Checking parameters
3. **Enriching** (60%) - Auto-filling fields
4. **Generating** (80%) - Creating content
5. **Saving** (90%) - Finalizing
6. **Completed** (100%) - Done!

---

## Code Snippets

### Replace This (Old):
```tsx
const result = await orchestrateCommand(command);
```

### With This (New):
```tsx
const result = await generateContent({
  userInput: command,
  requestId,
});

if (result.success) {
  console.log('Content ID:', result.contentId);
  console.log('Logs:', result.logs);
} else {
  console.error('Error:', result.error);
}
```

---

## Common Issues & Solutions

### Issue: Progress not updating
**Solution**: Make sure you're calling `startProgressPolling(requestId)`

### Issue: Content not saving
**Solution**: The orchestrator saves automatically - don't call `saveGeneratedContent` again

### Issue: Old orchestrator still being called
**Solution**: Search for `orchestrateCommand` and replace with `generateContent`

### Issue: Progress polling not stopping
**Solution**: Call `stopProgressPolling()` in cleanup and on success/error

---

## Performance Tips

1. **Polling Interval**: 500ms is optimal (don't go lower)
2. **Progress Updates**: Debounce setState calls if needed
3. **Cleanup**: Always stop polling on unmount
4. **Error Recovery**: Use retry with exponential backoff

---

## Visual Preview

### Before (Legacy):
```
User Input → [Loading...] → Done
```

### After (Track 4):
```
User Input
  ↓
[Understanding... 20%]
  ↓
[Validating... 40%]
  ↓
[Enriching... 60%]
  ↓
[Generating... 80%]
  ↓
[Saving... 90%]
  ↓
[Complete! 100%] ✓
```

---

## Next Actions

### Immediate:
1. Open `src/components/ui/CommandCenter.tsx`
2. Follow **Step 1** from integration guide
3. Test with: "Create a CMA for 123 Main St"

### After Testing:
1. Complete **Step 2** (Request Tiles)
2. Complete **Step 3** (Error Dialog)
3. Update store interface
4. Full QA testing

---

## Success Metrics

Track 4 is complete when:
- ✅ Progress shows in real-time
- ✅ Users can see enrichment sources
- ✅ Retry button works for failed requests
- ✅ Error dialog shows helpful suggestions
- ✅ All tests pass
- ✅ No console errors

---

## Time Estimate

- **Total Time**: 3-4 hours
- **Core Integration**: 1-2 hours
- **UI Enhancements**: 1 hour
- **Testing**: 1 hour

---

## Need Help?

See detailed instructions in:
- **`track4-integration-guide.md`** - Full step-by-step guide
- **`track3-summary.md`** - Orchestrator API reference
- **`TRACK3_COMPLETE.md`** - Implementation details

---

## Let's Go! 🎉

You now have:
- ✅ Track 3 orchestrator (fully implemented & tested)
- ✅ Progress tracker component (ready to use)
- ✅ Integration guide (step-by-step instructions)
- ✅ State variables added (ready for polling)

**Start with Phase 2, Step 3** in the integration guide and you'll be up and running in no time!

Good luck! 🚀
