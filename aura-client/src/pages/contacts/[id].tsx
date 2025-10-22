import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import ContactDetailHeader from '../../components/contacts/ContactDetailHeader';
import AIActionBar from '../../components/contacts/AIActionBar';
import SmartInsightsPanel from '../../components/contacts/SmartInsightsPanel';
import NotesEditor from '../../components/contacts/NotesEditor';
import type { Contact, ContactDetail } from '../../types/contacts';
import { getContactDetail, getTimeline, saveNotes } from '../../services/contactsApi';
import { generateFollowUp, summarizeNotes, recommendProperties, nextBestAction, type FollowUpTone, type FollowUpGoal } from '../../services/aiClient';
import FollowUpModal from '../../components/contacts/FollowUpModal';
import { listFollowUps, createFollowUp, type FollowUpItem } from '../../services/schedulesApi';
import BottomSheet from '../../components/ui/BottomSheet';
import RefineModal from '../../components/RefineModal';

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation() as any;
  const navigate = useNavigate();
  const contactFromState = (location?.state?.contact || null) as Partial<Contact> | null;

  const contact: Contact = useMemo(() => ({
    id: id || contactFromState?.id || 'unknown',
    name: contactFromState?.name || `Contact ${id}`,
    temperature: (contactFromState?.temperature as Contact['temperature']) || 'Warm',
    avatarUrl: contactFromState?.avatarUrl,
    email: contactFromState?.email,
    phone: contactFromState?.phone,
    lastActivityAt: contactFromState?.lastActivityAt,
  }), [id, contactFromState]);

  const [detail, setDetail] = useState<ContactDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aiBusy, setAiBusy] = useState(false);
  const [followUps, setFollowUps] = useState<FollowUpItem[]>([]);
  const [nextFU, setNextFU] = useState<FollowUpItem | null>(null);

  // Follow-up compose drawer state
  const [composeOpen, setComposeOpen] = useState(false);
  const [composeTone, setComposeTone] = useState<FollowUpTone>('Friendly');
  const [composeGoal, setComposeGoal] = useState<FollowUpGoal>('Re-engage');
  const [composeText, setComposeText] = useState('');

  // Summary modal state
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [summaryText, setSummaryText] = useState('');
  const [scheduleOpen, setScheduleOpen] = useState(false);

  // Recommendations & NBA
  const [recs, setRecs] = useState<Array<{ id: string; title: string; area: string; price: string; route: string }>>([]);
  const [nba, setNba] = useState<{ title: string; detail: string } | null>(null);
  const [recsLoading, setRecsLoading] = useState(false);
  const [recsError, setRecsError] = useState<string | null>(null);
  const [nbaLoading, setNbaLoading] = useState(false);
  const [nbaError, setNbaError] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    setLoading(true);
    setError(null);
    getContactDetail(contact.id, ac.signal)
      .then((d) => setDetail(d))
      .catch((e) => { if (e?.name !== 'AbortError') setError('Failed to load contact'); })
      .finally(() => setLoading(false));
    // also load follow-ups
    listFollowUps(contact.id, ac.signal)
      .then((items) => {
        setFollowUps(items);
        const now = Date.now();
        const upcoming = items.filter(i => new Date(i.dueAt).getTime() >= now)
          .sort((a,b) => new Date(a.dueAt).getTime() - new Date(b.dueAt).getTime())[0] || null;
        setNextFU(upcoming);
      })
      .catch(() => {})
      .finally(() => {});
    return () => ac.abort();
  }, [contact.id]);

  return (
    <main className="min-h-screen bg-gray-50" style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
      <ContactDetailHeader contact={contact} />
      {nextFU && (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 mt-2">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-[11px]">
            Next follow-up: {formatDue(nextFU.dueAt)} ({capitalize(nextFU.channel)})
          </span>
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-6" style={{ paddingTop: 'env(safe-area-inset-top)' }}>
        <div className="space-y-4 sm:space-y-5">
          <AIActionBar
            isProcessing={aiBusy}
            onGenerateFollowUp={async () => {
              setComposeOpen(true);
              setAiBusy(true);
              try {
                const txt = await generateFollowUp(contact.id, { tone: composeTone, goal: composeGoal });
                setComposeText(txt);
              } finally {
                setAiBusy(false);
              }
            }}
            onScheduleFollowUp={() => setScheduleOpen(true)}
            onSummarizeNotes={async () => {
              setAiBusy(true);
              try {
                const sum = await summarizeNotes(contact.id);
                setSummaryText(sum);
                setSummaryOpen(true);
              } finally { setAiBusy(false); }
            }}
            onRecommendProperties={async () => {
              setRecsError(null);
              setRecsLoading(true);
              try {
                const items = await recommendProperties(contact.id);
                setRecs(items);
              } catch (e) {
                setRecsError('Failed to load recommendations');
              } finally { setRecsLoading(false); }
            }}
            onNextBestAction={async () => {
              setNbaError(null);
              setNbaLoading(true);
              try {
                const val = await nextBestAction(contact.id);
                setNba(val);
              } catch (e) {
                setNbaError('Failed to load next best action');
              } finally { setNbaLoading(false); }
            }}
          />
          {(() => {
            const handleScheduleFollowUp = () => { setComposeOpen(false); setScheduleOpen(true); };
            const handleGenerateFollowUp = async () => {
              setComposeOpen(true);
              setAiBusy(true);
              try {
                const txt = await generateFollowUp(contact.id, { tone: composeTone, goal: composeGoal });
                setComposeText(txt);
              } finally {
                setAiBusy(false);
              }
            };
            const handleSummarizeNotes = async () => {
              setAiBusy(true);
              try {
                const sum = await summarizeNotes(contact.id);
                setSummaryText(sum);
                setSummaryOpen(true);
              } finally {
                setAiBusy(false);
              }
            };
            const handleRecommendProperties = async () => {
              setAiBusy(true);
              try {
                const r = await recommendProperties(contact.id);
                setRecs(r);
              } finally {
                setAiBusy(false);
              }
            };
            const handleNextBestAction = async () => {
              setAiBusy(true);
              try {
                const a = await nextBestAction(contact.id);
                setNba(a);
              } finally {
                setAiBusy(false);
              }
            };
            return (
              <AIActionBar
                isProcessing={aiBusy}
                onGenerateFollowUp={handleGenerateFollowUp}
                onScheduleFollowUp={handleScheduleFollowUp}
                onSummarizeNotes={handleSummarizeNotes}
                onRecommendProperties={handleRecommendProperties}
                onNextBestAction={handleNextBestAction}
              />
            );
          })()}

          {loading && (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
              <p className="text-sm text-gray-600">Loading contact...</p>
            </div>
          )}

          {!loading && error && (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {!loading && !error && detail && (
            <>
              <SmartInsightsPanel intentScore={detail.intentScore ?? 62} />
              <NotesEditor
                initial={detail.notes}
                onAutoSave={(value) => {
                  const controller = new AbortController();
                  saveNotes(contact.id, value, controller.signal)
                    .then(async (res) => {
                      setDetail(prev => (prev ? { ...prev, notes: res.notes } : prev));
                      try {
                        const timeline = await getTimeline(contact.id, controller.signal);
                        setDetail(prev => (prev ? { ...prev, timeline } : prev));
                      } catch (err: any) {
                        if (err?.name !== 'AbortError') {
                          console.warn('Failed to refresh timeline', err);
                        }
                      }
                    })
                    .catch((err: any) => {
                      if (err?.name !== 'AbortError') {
                        console.error('Failed to save notes', err);
                      }
                    });
                }}
              />
              {/* Recommendations List */}
              {recsLoading && (
                <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
                  <p className="text-sm text-gray-600">Loading recommendations…</p>
                </section>
              )}
              {!recsLoading && recsError && (
                <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
                  <p className="text-sm text-red-600">{recsError}</p>
                </section>
              )}
              {!recsLoading && !recsError && recs.length === 0 && (
                <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
                  <p className="text-sm text-gray-600">No recommendations yet.</p>
                </section>
              )}
              {!recsLoading && !recsError && recs.length > 0 && (
                <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-semibold text-gray-900">Recommendations</p>
                    <button
                      className="text-xs text-gray-500 hover:text-gray-700"
                      onClick={() => setRecs([])}
                    >Clear</button>
                  </div>
                  <ul className="space-y-2">
                    {recs.map((r) => (
                      <li key={r.id} className="flex items-center justify-between gap-3 rounded-xl border border-gray-200 p-3">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{r.title}</p>
                          <p className="text-xs text-gray-500">{r.area} · {r.price}</p>
                        </div>
                        <button
                          className="shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-600 text-white text-xs sm:text-sm hover:bg-blue-700"
                          onClick={() => navigate(r.route)}
                        >Open</button>
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              {/* Next Best Action Card */}
              {nbaLoading && (
                <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
                  <p className="text-sm text-gray-600">Loading next best action…</p>
                </section>
              )}
              {!nbaLoading && nbaError && (
                <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
                  <p className="text-sm text-red-600">{nbaError}</p>
                </section>
              )}
              {!nbaLoading && !nbaError && nba && (
                <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-900">Next Best Action</p>
                      <p className="text-sm text-gray-700 mt-1">{nba.title}</p>
                      <p className="text-xs text-gray-500">{nba.detail}</p>
                    </div>
                    <button className="text-xs text-gray-500 hover:text-gray-700" onClick={() => setNba(null)}>Dismiss</button>
                  </div>
                </section>
              )}
              <ActivityFeed timeline={detail.timeline} />
            </>
          )}
        </div>
      </div>

      {/* Compose Follow-Up Drawer */}
      <BottomSheet isOpen={composeOpen} onClose={() => setComposeOpen(false)} title="Compose Follow-Up" initialHeight="full">
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs text-gray-600 mb-1">Tone</label>
              <select
                className="w-full border border-gray-300 rounded-lg px-2 py-2 text-sm"
                value={composeTone}
                onChange={(e) => setComposeTone(e.target.value as any)}
              >
                {(['Friendly','Professional','Persuasive','Casual'] as const).map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">Goal</label>
              <select
                className="w-full border border-gray-300 rounded-lg px-2 py-2 text-sm"
                value={composeGoal}
                onChange={(e) => setComposeGoal(e.target.value as any)}
              >
                {(['Re-engage','Schedule Call','Share Brochure','Nurture'] as const).map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-600 mb-1">Draft</label>
            <textarea
              className="w-full min-h-[180px] border border-gray-300 rounded-xl p-3 text-sm"
              value={composeText}
              onChange={(e) => setComposeText(e.target.value)}
            />
          </div>

          <div className="flex items-center justify-end gap-2">
            <button
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-300 text-gray-700 text-sm hover:bg-gray-50"
              onClick={async () => {
                setAiBusy(true);
                try {
                  const txt = await generateFollowUp(contact.id, { tone: composeTone, goal: composeGoal });
                  setComposeText(txt);
                } finally {
                  setAiBusy(false);
                }
              }}
              disabled={aiBusy}
            >Regenerate</button>
            <button
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 text-white text-sm hover:bg-blue-700"
              onClick={() => {
                if (detail) {
                  setDetail({ ...detail, notes: `${detail.notes}\n\n---\nFollow-up draft:\n${composeText}` });
                }
                setComposeOpen(false);
              }}
            >Save Draft</button>
          </div>
        </div>
      </BottomSheet>

      {/* Schedule Follow-Up Modal */}
      <FollowUpModal
        isOpen={scheduleOpen}
        onClose={() => setScheduleOpen(false)}
        onSave={async (data) => {
          const ac = new AbortController();
          await createFollowUp({ contactId: contact.id, ...data }, ac.signal);
          const items = await listFollowUps(contact.id);
          setFollowUps(items);
          const now = Date.now();
          const upcoming = items.filter(i => new Date(i.dueAt).getTime() >= now)
            .sort((a,b) => new Date(a.dueAt).getTime() - new Date(b.dueAt).getTime())[0] || null;
          setNextFU(upcoming);
          try {
            const refreshedTimeline = await getTimeline(contact.id, ac.signal);
            setDetail(prev => (prev ? { ...prev, timeline: refreshedTimeline } : prev));
          } catch (err: any) {
            if (err?.name !== 'AbortError') {
              console.warn('Failed to refresh timeline after follow-up creation', err);
            }
          }
          setScheduleOpen(false);
        }}
      />

      {/* Summary Modal */}
      <RefineModal isOpen={summaryOpen} onClose={() => setSummaryOpen(false)} variant="preview" headerTitle="AI Summary">
        <div className="space-y-3">
          <div className="rounded-xl border border-gray-200 p-3 bg-gray-50">
            <p className="text-sm text-gray-800 whitespace-pre-wrap">{summaryText}</p>
          </div>
          <div className="flex items-center justify-end gap-2">
            <button className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm" onClick={() => setSummaryOpen(false)}>Close</button>
            <button
              className="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-sm hover:bg-blue-700"
              onClick={() => {
                if (detail) {
                  setDetail({ ...detail, notes: `${detail.notes}\n\n${summaryText}` });
                }
                setSummaryOpen(false);
              }}
            >Insert into Notes</button>
          </div>
        </div>
      </RefineModal>
    </main>
  );
}

//

function ActivityFeed({ timeline }: { timeline: ContactDetail['timeline'] }) {
  const groups = useMemo(() => groupByDate(timeline), [timeline]);
  return (
    <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
      <p className="text-sm font-semibold text-gray-900 mb-3">Activity</p>
      <div className="space-y-4">
        {groups.map(g => (
          <div key={g.label}>
            <p className="text-xs font-medium text-gray-500 mb-2">{g.label}</p>
            <ul className="space-y-2">
              {g.items.map(item => (
                <li key={item.id} className="rounded-xl border border-gray-200 p-3">
                  <p className="text-sm text-gray-900">{item.text}</p>
                  <p className="text-xs text-gray-500 mt-1">{formatTime(item.ts)} · {item.type}</p>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}

function groupByDate(items: ContactDetail['timeline']) {
  const days = new Map<string, ContactDetail['timeline']>();
  items
    .slice()
    .sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime())
    .forEach(i => {
      const d = new Date(i.ts);
      const key = `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
      if (!days.has(key)) days.set(key, []);
      days.get(key)!.push(i);
    });
  const now = new Date();
  const todayKey = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
  const y = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const yKey = `${y.getFullYear()}-${y.getMonth() + 1}-${y.getDate()}`;
  return Array.from(days.entries()).map(([key, val]) => ({
    label: key === todayKey ? 'Today' : key === yKey ? 'Yesterday' : formatDate(val[0].ts),
    items: val,
  }));
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}
function formatTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

function formatDue(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  const y = new Date(now.getTime() - 24*60*60*1000);
  const yesterday = d.toDateString() === y.toDateString();
  const dayLabel = sameDay ? 'Today' : yesterday ? 'Yesterday' : d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  return `${dayLabel} ${d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}`;
}

function capitalize<T extends string>(s: T): T {
  return ((s.charAt(0).toUpperCase() + s.slice(1)) as unknown) as T;
}
