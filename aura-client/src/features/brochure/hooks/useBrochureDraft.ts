import { useCallback, useEffect, useRef, useState } from 'react';
import { brochureDraftService } from '../../../services/brochureDrafts';
import type { BrochureDraft } from '../../../types/brochure';

export function useBrochureDraft(draftId: string | undefined) {
  const [draft, setDraft] = useState<BrochureDraft | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedVisible, setSavedVisible] = useState(false);

  useEffect(() => {
    if (!draftId) return;
    let mounted = true;
    (async () => {
      try {
        const d = await brochureDraftService.getDraft(draftId);
        if (mounted) setDraft(d);
      } catch (e: any) {
        if (mounted) setError(e?.message || 'Failed to load draft');
      }
    })();
    return () => { mounted = false; };
  }, [draftId]);

  const timeoutRef = useRef<number | null>(null);
  const update = useCallback((patch: Partial<BrochureDraft>) => {
    if (!draftId) return;
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    timeoutRef.current = window.setTimeout(async () => {
      try {
        setSaving(true);
        const updated = await brochureDraftService.updateDraft(draftId, patch);
        setDraft(updated);
        setSaving(false);
        setSavedVisible(true);
        window.setTimeout(() => setSavedVisible(false), 1200);
      } catch (e) {
        setSaving(false);
      }
    }, 500);
  }, [draftId]);

  return { draft, setDraft, error, saving, savedVisible, update };
}

