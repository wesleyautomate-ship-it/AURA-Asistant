import React, { useEffect, useState } from 'react';
import { X, Calendar, Clock, Phone, Mail, MessageSquare, Users as UsersIcon } from 'lucide-react';
import type { FollowUpChannel } from '../../services/schedulesApi';

export interface FollowUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: { channel: FollowUpChannel; dueAt: string; notes?: string }) => void;
}

const CHANNELS: Array<{ value: FollowUpChannel; label: string; icon: React.ReactNode }> = [
  { value: 'call', label: 'Call', icon: <Phone className="w-4 h-4" /> },
  { value: 'email', label: 'Email', icon: <Mail className="w-4 h-4" /> },
  { value: 'whatsapp', label: 'WhatsApp', icon: <MessageSquare className="w-4 h-4" /> },
  { value: 'meeting', label: 'Meeting', icon: <UsersIcon className="w-4 h-4" /> },
];

export default function FollowUpModal({ isOpen, onClose, onSave }: FollowUpModalProps) {
  const [channel, setChannel] = useState<FollowUpChannel>('call');
  const [dueAt, setDueAt] = useState<string>(defaultDateTimeLocal());
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (isOpen) {
      setChannel('call');
      setDueAt(defaultDateTimeLocal());
      setNotes('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="w-full max-w-md bg-white rounded-t-2xl sm:rounded-2xl shadow-xl" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h3 className="font-semibold text-gray-900">Schedule Follow-Up</h3>
            <p className="text-sm text-gray-600">Choose channel and time</p>
          </div>
          <button className="p-2 rounded-full hover:bg-gray-100" onClick={onClose} aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Channel</label>
            <div className="grid grid-cols-2 gap-2">
              {CHANNELS.map(c => (
                <button
                  key={c.value}
                  className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-sm ${channel === c.value ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-300 text-gray-700 hover:bg-gray-50'}`}
                  onClick={() => setChannel(c.value)}
                  type="button"
                >
                  {c.icon}
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3">
            <div>
              <label className="block text-xs text-gray-600 mb-1">Due Date & Time</label>
              <div className="relative">
                <input
                  type="datetime-local"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  value={dueAt}
                  onChange={(e) => setDueAt(e.target.value)}
                />
                <Clock className="w-4 h-4 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-600 mb-1">Notes</label>
            <textarea
              className="w-full min-h-[100px] border border-gray-300 rounded-lg p-3 text-sm"
              placeholder="Add context (optional)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm" onClick={onClose}>Cancel</button>
            <button
              className="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-sm hover:bg-blue-700"
              onClick={() => onSave({ channel, dueAt: toISO(dueAt), notes: notes.trim() || undefined })}
            >Save</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function defaultDateTimeLocal() {
  const d = new Date(Date.now() + 60 * 60 * 1000); // +1h
  d.setMinutes( Math.round(d.getMinutes()/5)*5 );
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function toISO(dtLocal: string) {
  // Treat as local time and convert to ISO
  const [date, time] = dtLocal.split('T');
  const [y, m, d] = date.split('-').map(Number);
  const [hh, mm] = time.split(':').map(Number);
  const dt = new Date(y, (m-1), d, hh, mm, 0);
  return dt.toISOString();
}

