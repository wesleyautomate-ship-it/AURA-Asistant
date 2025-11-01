import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Calendar, Lightbulb, Plus } from 'lucide-react';
import ContactHeader from '../../components/contact/ContactHeader';
import ContactInsightsCard from '../../components/contact/ContactInsightsCard';
import ContactActionBar, { type ContactActionBarHandle } from '../../components/contact/ContactActionBar';
import ContactNotes, { type ContactNotesHandle } from '../../components/contact/ContactNotes';
import RefineModal from '../../components/RefineModal';
import type { Contact, ContactDetail } from '../../types/contacts';
import { getContact } from '../../services/contactApi';
import { listFollowUps, type FollowUpItem } from '../../services/schedulesApi';

type NextBestSuggestion = { label: string; actionKey: string; payload?: unknown };

const DEFAULT_INTENT_SCORE = 62;

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation() as { state?: { contact?: Contact } } | null;
  const navigate = useNavigate();
  const contactFromState = location?.state?.contact ?? null;

  const contact: Contact = useMemo(
    () => ({
      id: id || contactFromState?.id || 'unknown',
      name: contactFromState?.name || `Contact ${id}`,
      temperature: (contactFromState?.temperature as Contact['temperature']) || 'Warm',
      avatarUrl: contactFromState?.avatarUrl,
      email: contactFromState?.email,
      phone: contactFromState?.phone,
      lastActivityAt: contactFromState?.lastActivityAt,
    }),
    [contactFromState, id],
  );

  const [detail, setDetail] = useState<ContactDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nextFollowUp, setNextFollowUp] = useState<FollowUpItem | null>(null);
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [summaryText, setSummaryText] = useState('');
  const [nextBest, setNextBest] = useState<NextBestSuggestion | null>(null);

  const notesRef = useRef<ContactNotesHandle>(null);
  const actionBarRef = useRef<ContactActionBarHandle | null>(null);

  const isCanceledError = (err: any) =>
    err?.name === 'AbortError' || err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED';

  const fetchDetail = useCallback(
    async (signal?: AbortSignal) => {
      setLoading(true);
      setError(null);
      try {
        const data = await getContact(contact.id, signal);
        setDetail({ ...data, timeline: data.timeline ?? [] });
      } catch (err: any) {
        if (isCanceledError(err)) return;
        console.error('[ContactDetail] failed to load contact', err);
        setError('Failed to load contact');
      } finally {
        setLoading(false);
      }
    },
    [contact.id],
  );

  const refreshFollowUps = useCallback(
    async (signal?: AbortSignal) => {
      try {
        const items = await listFollowUps(contact.id, signal);
        const now = Date.now();
        const upcoming =
          items
            .slice()
            .sort((a, b) => new Date(a.dueAt).getTime() - new Date(b.dueAt).getTime())
            .find((item) => new Date(item.dueAt).getTime() >= now) || null;
        setNextFollowUp(upcoming);
      } catch (err: any) {
        if (isCanceledError(err)) return;
        console.warn('[ContactDetail] failed to refresh follow-ups', err);
      }
    },
    [contact.id],
  );

  const refreshDetailSilently = useCallback(async () => {
    try {
      const data = await getContact(contact.id);
      setDetail({ ...data, timeline: data.timeline ?? [] });
    } catch (err: any) {
      if (isCanceledError(err)) return;
      console.warn('[ContactDetail] silent refresh failed', err);
    }
  }, [contact.id]);

  const handleSummaryApply = (mode: 'append' | 'replace') => {
    if (!summaryText) return;
    if (mode === 'append') {
      notesRef.current?.appendText(summaryText);
    } else {
      notesRef.current?.replaceText(summaryText);
    }
    setSummaryOpen(false);
  };

  useEffect(() => {
    const controller = new AbortController();
    void fetchDetail(controller.signal);
    void refreshFollowUps(controller.signal);
    return () => controller.abort();
  }, [fetchDetail, refreshFollowUps]);

  const displayContact = detail ?? contact;
  const area = deriveArea(detail);
  const budgetLabel = formatBudget(detail?.budget);
  const headerPhone = detail?.phone ?? contact.phone;
  const headerEmail = detail?.email ?? contact.email;
  const showLoadingCard = loading && !detail;

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-blue-50 pb-28">
      <ContactHeader
        name={displayContact.name}
        initials={displayContact.initials}
        avatarUrl={displayContact.avatarUrl}
        temperature={displayContact.temperature}
        phone={headerPhone}
        email={headerEmail}
        area={area}
        budgetLabel={budgetLabel}
        pipeline={detail?.pipeline ?? null}
        onBack={() => navigate('/contacts')}
      />

      <div className="max-w-3xl mx-auto px-4 space-y-4 pb-24">
        {nextFollowUp && (
          <UpcomingFollowUpCard
            followUp={nextFollowUp}
            onReview={() => actionBarRef.current?.openFollowUp?.()}
          />
        )}

        {error && <ErrorCard message={error} />}
        {showLoadingCard && <LoadingCard />}

        {!showLoadingCard && !error && detail && (
          <>
            <ContactActionBar
              ref={actionBarRef}
              contactId={contact.id}
              notesEmpty={!detail.notes || !detail.notes.trim()}
              disabled={loading}
              onFollowUpCreated={async () => {
                await refreshFollowUps();
                await refreshDetailSilently();
              }}
              onNotesSummarized={(summary) => {
                setSummaryText(summary);
                setSummaryOpen(true);
              }}
              onNextBestAction={(payload) => setNextBest(payload)}
            />

            {nextBest && (
              <NextBestActionCard
                suggestion={nextBest}
                onDismiss={() => setNextBest(null)}
                onSchedule={() => {
                  actionBarRef.current?.openFollowUp?.();
                  setNextBest(null);
                }}
                onNavigate={(route) => {
                  navigate(route);
                  setNextBest(null);
                }}
              />
            )}

            <ContactInsightsCard
              temperature={displayContact.temperature}
              intentScore={detail.intentScore ?? DEFAULT_INTENT_SCORE}
              signals={detail.signals ?? undefined}
              risks={detail.risks ?? undefined}
            />

            <ContactNotes
              ref={notesRef}
              contactId={contact.id}
              initialText={detail.notes}
              onTextChange={(value) => setDetail((prev) => (prev ? { ...prev, notes: value } : prev))}
            />

            <ActivityFeed timeline={detail.timeline} />
          </>
        )}
      </div>

      <button
        type="button"
        onClick={() => actionBarRef.current?.openFollowUp?.()}
        className="fixed bottom-24 right-5 sm:bottom-20 sm:right-8 inline-flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-purple-600 text-white shadow-lg focus:outline-none focus:ring-4 focus:ring-purple-200"
        aria-label="Log new activity"
      >
        <Plus className="w-6 h-6" />
      </button>

      <RefineModal
        isOpen={summaryOpen}
        onClose={() => {
          setSummaryOpen(false);
          setSummaryText('');
        }}
        variant="preview"
        headerTitle="AI Summary"
      >
        <div className="space-y-3">
          <div className="rounded-xl border border-gray-200 p-3 bg-gray-50">
            <p className="text-sm text-gray-800 whitespace-pre-wrap">{summaryText}</p>
          </div>
          <div className="flex flex-wrap items-center justify-end gap-2">
            <button
              className="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-sm hover:bg-blue-700"
              onClick={() => handleSummaryApply('append')}
            >
              Append to Notes
            </button>
            <button
              className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm hover:bg-gray-100"
              onClick={() => handleSummaryApply('replace')}
            >
              Replace Notes
            </button>
            <button
              className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm"
              onClick={() => {
                setSummaryOpen(false);
                setSummaryText('');
              }}
            >
              Close
            </button>
          </div>
        </div>
      </RefineModal>
    </main>
  );
}

function LoadingCard() {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 sm:p-5">
      <p className="text-sm text-gray-600">Loading contact details…</p>
    </div>
  );
}

function ErrorCard({ message }: { message: string }) {
  return (
    <div className="bg-white rounded-2xl border border-red-200 shadow-sm p-4 sm:p-5">
      <p className="text-sm text-red-600">{message}</p>
    </div>
  );
}

function UpcomingFollowUpCard({ followUp, onReview }: { followUp: FollowUpItem; onReview: () => void }) {
  return (
    <section className="bg-white rounded-2xl border border-amber-200 shadow-sm p-4 flex items-center gap-3">
      <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-amber-100 text-amber-700">
        <Calendar className="w-4 h-4" />
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Next follow-up</p>
        <p className="text-sm text-gray-800">
          {formatDue(followUp.dueAt)} · {capitalize(followUp.channel)}
        </p>
      </div>
      <button
        type="button"
        onClick={onReview}
        className="inline-flex items-center rounded-lg border border-amber-300 px-3 py-1.5 text-xs font-medium text-amber-700 hover:bg-amber-50"
      >
        Review
      </button>
    </section>
  );
}

function NextBestActionCard({
  suggestion,
  onDismiss,
  onSchedule,
  onNavigate,
}: {
  suggestion: NextBestSuggestion;
  onDismiss: () => void;
  onSchedule: () => void;
  onNavigate: (route: string) => void;
}) {
  const route = typeof (suggestion.payload as any)?.route === 'string' ? (suggestion.payload as any).route : null;
  const recommendsFollowUp = suggestion.actionKey?.toLowerCase().includes('follow');

  return (
    <section className="bg-white rounded-2xl border border-amber-200 shadow-sm p-4 sm:p-5">
      <div className="flex items-start gap-3">
        <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-amber-100 text-amber-600">
          <Lightbulb className="w-4 h-4" />
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-amber-800">Next Best Action</p>
          <p className="text-sm text-amber-700 mt-1">{suggestion.label}</p>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {route && (
          <button
            type="button"
            onClick={() => onNavigate(route)}
            className="inline-flex items-center rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
          >
            View
          </button>
        )}
        {recommendsFollowUp && (
          <button
            type="button"
            onClick={onSchedule}
            className="inline-flex items-center rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
          >
            Schedule
          </button>
        )}
        <button
          type="button"
          onClick={onDismiss}
          className="inline-flex items-center rounded-lg border border-amber-300 px-3 py-1.5 text-xs font-medium text-amber-700 hover:bg-amber-50"
        >
          Dismiss
        </button>
      </div>
    </section>
  );
}

function ActivityFeed({ timeline }: { timeline: ContactDetail['timeline'] }) {
  const groups = useMemo(() => groupByDate(timeline), [timeline]);
  return (
    <section className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 sm:p-5">
      <p className="text-sm font-semibold text-gray-900 mb-3">Activity</p>
      <div className="space-y-4">
        {groups.map((group) => (
          <div key={group.label}>
            <p className="text-xs font-medium text-gray-500 mb-2">{group.label}</p>
            <ul className="space-y-2">
              {group.items.map((item) => (
                <li key={item.id} className="rounded-xl border border-gray-200 p-3">
                  <p className="text-sm text-gray-900">{item.text}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatTime(item.ts)} · {item.type}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}

function deriveArea(detail: ContactDetail | null): string | null {
  if (!detail) return null;
  if (detail.area) return detail.area;
  if (detail.preferences && detail.preferences.length > 0) return detail.preferences[0];
  return null;
}

function formatBudget(budget?: ContactDetail['budget']): string | null {
  if (!budget) return null;
  const { min, max, currency } = budget;
  if (min == null && max == null) return null;

  const formattedMin = typeof min === 'number' ? formatAmount(min) : null;
  const formattedMax = typeof max === 'number' ? formatAmount(max) : null;

  const range =
    formattedMin && formattedMax && formattedMin !== formattedMax
      ? `${formattedMin} - ${formattedMax}`
      : formattedMax || formattedMin;

  if (!range) return null;
  return [currency || 'AED', range].filter(Boolean).join(' ');
}

function formatAmount(value: number) {
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 1,
    notation: 'compact',
  }).format(value);
}

function groupByDate(items: ContactDetail['timeline']) {
  const days = new Map<string, ContactDetail['timeline']>();
  items
    .slice()
    .sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime())
    .forEach((item) => {
      const date = new Date(item.ts);
      const key = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
      if (!days.has(key)) days.set(key, []);
      days.get(key)!.push(item);
    });

  const now = new Date();
  const todayKey = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
  const yesterdayDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const yesterdayKey = `${yesterdayDate.getFullYear()}-${yesterdayDate.getMonth() + 1}-${yesterdayDate.getDate()}`;

  return Array.from(days.entries()).map(([key, value]) => ({
    label: key === todayKey ? 'Today' : key === yesterdayKey ? 'Yesterday' : formatDate(value[0].ts),
    items: value,
  }));
}

function formatDate(iso: string) {
  const date = new Date(iso);
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatTime(iso: string) {
  const date = new Date(iso);
  return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

function formatDue(iso: string) {
  const date = new Date(iso);
  const now = new Date();
  const sameDay = date.toDateString() === now.toDateString();
  const yesterdayDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const isYesterday = date.toDateString() === yesterdayDate.toDateString();
  const dayLabel = sameDay ? 'Today' : isYesterday ? 'Yesterday' : date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  return `${dayLabel} ${date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}`;
}

function capitalize<T extends string>(value: T): T {
  if (!value) return value;
  return ((value.charAt(0).toUpperCase() + value.slice(1)) as unknown) as T;
}

