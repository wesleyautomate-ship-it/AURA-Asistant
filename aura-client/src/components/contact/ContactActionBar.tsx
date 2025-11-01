import { forwardRef, useImperativeHandle, useState } from 'react'
import { MessageSquare, FileText, Lightbulb } from 'lucide-react'
import FollowUpModal from '../contacts/FollowUpModal'
import { createFollowUp, fetchNextBestAction, summarizeNotes, type NextBestAction as NextBestActionType } from '../../services/contactApi'

type Props = {
  contactId: string
  notesEmpty?: boolean
  onFollowUpCreated?: () => void
  onNotesSummarized?: (summary: string) => void
  onNextBestAction?: (nba: NextBestActionType) => void
  disabled?: boolean
}

type ToastState = { kind: 'success' | 'error'; message: string } | null

export interface ContactActionBarHandle {
  openFollowUp: () => void
}

export default forwardRef<ContactActionBarHandle, Props>(function ContactActionBar(
  { contactId, notesEmpty = false, onFollowUpCreated, onNotesSummarized, onNextBestAction, disabled = false },
  ref,
) {
  const [followUpOpen, setFollowUpOpen] = useState(false)
  const [pending, setPending] = useState<'followup' | 'summary' | 'nba' | null>(null)
  const [toast, setToast] = useState<ToastState>(null)

  const buttonBase =
    'flex-1 min-w-0 flex items-center justify-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-800 transition hover:bg-gray-50 active:scale-95 disabled:opacity-50 disabled:pointer-events-none'

  const showToast = (next: ToastState) => {
    setToast(next)
    if (next) {
      window.setTimeout(() => {
        setToast((current) => (current === next ? null : current))
      }, 3200)
    }
  }

  useImperativeHandle(
    ref,
    () => ({
      openFollowUp: () => setFollowUpOpen(true),
    }),
    [],
  )

  return (
    <div className="bg-white rounded-2xl shadow border border-gray-200 p-3 sm:p-4">
      <div className="flex flex-col gap-2">
        <div className="flex flex-col sm:flex-row gap-2">
          <button
            type="button"
            className={buttonBase}
            onClick={() => setFollowUpOpen(true)}
            disabled={disabled || pending !== null}
          >
            <MessageSquare className="h-4 w-4 text-blue-600" />
            Follow-Up
          </button>
          <button
            type="button"
            className={buttonBase}
            onClick={async () => {
              if (disabled || pending) return
              try {
                setPending('summary')
                const { summary } = await summarizeNotes(contactId)
                onNotesSummarized?.(summary)
                showToast({ kind: 'success', message: 'Notes summarised' })
              } catch (error) {
                console.error('[ContactActionBar] summarizeNotes failed', error)
                showToast({ kind: 'error', message: 'Failed to summarise notes' })
              } finally {
                setPending(null)
              }
            }}
            disabled={disabled || pending !== null || notesEmpty}
          >
            <FileText className="h-4 w-4 text-emerald-600" />
            Summarize Notes
          </button>
          <button
            type="button"
            className={buttonBase}
            onClick={async () => {
              if (disabled || pending) return
              try {
                setPending('nba')
                const nba = await fetchNextBestAction(contactId)
                onNextBestAction?.(nba)
                showToast({ kind: 'success', message: 'Next best action ready' })
              } catch (error) {
                console.error('[ContactActionBar] next best action failed', error)
                showToast({ kind: 'error', message: 'Unable to fetch action' })
              } finally {
                setPending(null)
              }
            }}
            disabled={disabled || pending !== null}
          >
            <Lightbulb className="h-4 w-4 text-amber-500" />
            Next Best Action
          </button>
        </div>
        {toast && (
          <div
            className={`text-xs px-3 py-1.5 rounded-lg border ${
              toast.kind === 'success'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                : 'bg-red-50 border-red-200 text-red-600'
            }`}
          >
            {toast.message}
          </div>
        )}
      </div>

      <FollowUpModal
        isOpen={followUpOpen}
        onClose={() => {
          if (pending !== 'followup') setFollowUpOpen(false)
        }}
        onSave={async ({ channel, dueAt, notes }) => {
          if (pending) return
          try {
            setPending('followup')
            const normalizedChannel = channel === 'whatsapp' ? 'call' : channel
            await createFollowUp(contactId, { when: dueAt, channel: normalizedChannel, note: notes })
            showToast({ kind: 'success', message: 'Follow-up scheduled' })
            onFollowUpCreated?.()
            setFollowUpOpen(false)
          } catch (error) {
            console.error('[ContactActionBar] createFollowUp failed', error)
            showToast({ kind: 'error', message: 'Failed to schedule follow-up' })
          } finally {
            setPending(null)
          }
        }}
      />
    </div>
  )
})
