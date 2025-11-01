import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'
import { aiDraftNotes, patchNotes } from '../../services/contactApi'

type SavingState = 'idle' | 'saving' | 'saved' | 'error'

export interface ContactNotesProps {
  contactId: string
  initialText: string
  onTextChange?: (text: string) => void
}

export interface ContactNotesHandle {
  appendText: (value: string) => void
  replaceText: (value: string) => void
  getText: () => string
}

export default forwardRef<ContactNotesHandle, ContactNotesProps>(function ContactNotes(
  { contactId, initialText, onTextChange },
  ref,
) {
  const [text, setText] = useState(initialText)
  const [saving, setSaving] = useState<SavingState>('idle')
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null)
  const lastSavedTextRef = useRef(initialText)
  const debounceRef = useRef<number | null>(null)
  const inFlightRef = useRef<Promise<void> | null>(null)

  const [composerOpen, setComposerOpen] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [draft, setDraft] = useState<string | null>(null)
  const [draftLoading, setDraftLoading] = useState(false)
  const [draftError, setDraftError] = useState<string | null>(null)

  const previousContactId = useRef(contactId)

  useEffect(() => {
    if (previousContactId.current !== contactId) {
      previousContactId.current = contactId
      setText(initialText)
      lastSavedTextRef.current = initialText
      setSaving('idle')
      setLastSavedAt(null)
    }
  }, [contactId, initialText])

  useEffect(() => {
    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current)
    }
    debounceRef.current = window.setTimeout(() => {
      void persist()
    }, 800)

    return () => {
      if (debounceRef.current) {
        window.clearTimeout(debounceRef.current)
        debounceRef.current = null
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text, contactId])

  const persist = async () => {
    if (inFlightRef.current) {
      await inFlightRef.current
    }
    if (text === lastSavedTextRef.current) {
      if (saving !== 'idle') setSaving('saved')
      return
    }

    const operation = (async () => {
      try {
        setSaving('saving')
        const { savedAt } = await patchNotes(contactId, text)
        lastSavedTextRef.current = text
        setSaving('saved')
        setLastSavedAt(savedAt)
      } catch (error) {
        console.error('[ContactNotes] failed to save notes', error)
        setSaving('error')
      } finally {
        inFlightRef.current = null
      }
    })()

    inFlightRef.current = operation
    await operation
  }

  const statusLabel = () => {
    switch (saving) {
      case 'saving':
        return 'Saving...'
      case 'saved':
        return lastSavedAt ? `Saved ${formatTimeAgo(lastSavedAt)}` : 'Saved'
      case 'error':
        return 'Save failed'
      default:
        return ''
    }
  }

  const disabled = saving === 'saving' || draftLoading

  useImperativeHandle(
    ref,
    () => ({
      appendText: (value: string) => {
        const appended = text ? `${text.trimEnd()}\n\n${value}` : value
        setText(appended)
        onTextChange?.(appended)
      },
      replaceText: (value: string) => {
        setText(value)
        onTextChange?.(value)
      },
      getText: () => text,
    }),
    [text, onTextChange],
  )

  return (
    <section className="bg-white rounded-2xl shadow border border-gray-200 p-4 sm:p-5">
      <div className="flex items-center justify-between gap-2 mb-3">
        <h2 className="text-sm font-semibold text-gray-900">Notes</h2>
        <div className="flex items-center gap-2">
          {saving === 'error' && (
            <button
              type="button"
              className="text-xs text-red-600 underline"
              onClick={() => {
                void persist()
              }}
            >
              Retry
            </button>
          )}
          <span className="text-xs text-gray-500 min-w-[90px] text-right">{statusLabel()}</span>
          <button
            type="button"
            className="inline-flex items-center gap-1 rounded-lg border border-gray-200 px-2.5 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            onClick={() => {
              setComposerOpen((open) => !open)
              setDraft(null)
              setDraftError(null)
            }}
            disabled={disabled}
          >
            <Sparkles className="h-3.5 w-3.5 text-purple-600" />
            AI Compose
          </button>
        </div>
      </div>

      <div className="relative">
        <textarea
          value={text}
          onChange={(event) => {
            const next = event.target.value
            setText(next)
            onTextChange?.(next)
          }}
          className="w-full min-h-[180px] border border-gray-200 rounded-xl p-3 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          placeholder="Capture client history, preferences, and next steps..."
        />
        <span className="absolute bottom-2 right-3 text-xs text-gray-400">{text.length}</span>
      </div>
      <p className="mt-2 text-xs text-gray-400">Autosaves as you type</p>

      {composerOpen && (
        <div className="mt-4 rounded-xl border border-gray-200 p-3 space-y-2 bg-gray-50">
          <p className="text-xs text-gray-600">What would you like to draft?</p>
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
            rows={3}
            placeholder="e.g. Draft follow-up notes for a buyer interested in waterfront condos"
          />
          {draftError && <p className="text-xs text-red-600">{draftError}</p>}
          {draft && (
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-2 text-xs text-blue-800 whitespace-pre-wrap">
              {draft}
            </div>
          )}
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              onClick={async () => {
                try {
                  setDraftError(null)
                  setDraft(null)
                  setDraftLoading(true)
                  const { draft: generated } = await aiDraftNotes(contactId, {
                    prompt: prompt.trim() || undefined,
                    context: text || undefined,
                  })
                  setDraft(generated)
                } catch (error) {
                  console.error('[ContactNotes] AI compose failed', error)
                  setDraftError('AI draft failed. Try again.')
                } finally {
                  setDraftLoading(false)
                }
              }}
              disabled={draftLoading}
            >
              {draftLoading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              Draft
            </button>
            {draft && (
              <>
                <button
                  type="button"
                  className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-100"
                  onClick={() => {
                    const appended = text ? `${text.trimEnd()}\n\n${draft}` : draft
                    setText(appended)
                    onTextChange?.(appended)
                    setDraft(null)
                    setComposerOpen(false)
                  }}
                >
                  Append
                </button>
                <button
                  type="button"
                  className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-100"
                  onClick={() => {
                    setText(draft)
                    onTextChange?.(draft)
                    setDraft(null)
                    setComposerOpen(false)
                  }}
                >
                  Replace
                </button>
              </>
            )}
            <button
              type="button"
              className="ml-auto text-xs text-gray-500 hover:text-gray-700"
              onClick={() => {
                setComposerOpen(false)
                setDraft(null)
                setPrompt('')
                setDraftError(null)
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </section>
  )
})

function formatTimeAgo(iso: string) {
  const saved = new Date(iso).getTime()
  const diff = Date.now() - saved
  if (diff < 60_000) return 'just now'
  if (diff < 3_600_000) {
    const mins = Math.round(diff / 60_000)
    return `${mins}m ago`
  }
  const date = new Date(iso)
  return date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
}
