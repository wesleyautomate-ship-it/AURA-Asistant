import React from 'react';
import { ChevronLeft, MoreVertical, Clock } from 'lucide-react';
import { Contact } from '../../types/contacts';
import { useNavigate } from 'react-router-dom';

export interface ContactDetailHeaderProps {
  contact: Contact;
  nextFollowUpLabel?: string;
}

export default function ContactDetailHeader({ contact, nextFollowUpLabel }: ContactDetailHeaderProps) {
  const navigate = useNavigate();
  const initials = contact.initials ?? getInitials(contact.name);

  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-3">
        <button
          onClick={() => navigate('/contacts')}
          aria-label="Back to Contacts"
          className="flex items-center gap-1 p-2 rounded-lg hover:bg-gray-100"
        >
          <ChevronLeft className="w-5 h-5 text-gray-700" />
          <span className="text-xs text-gray-500 hidden sm:inline">Back to Contacts</span>
        </button>

        {contact.avatarUrl ? (
          <img src={contact.avatarUrl} alt={contact.name} className="w-9 h-9 rounded-full border border-gray-200" />
        ) : (
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 border border-gray-200 flex items-center justify-center">
            <span className="text-xs font-semibold text-gray-700">{initials}</span>
          </div>
        )}

        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-gray-900 truncate">{contact.name}</p>
          <p className="text-xs text-gray-500 truncate">{contact.email ?? contact.phone ?? '—'}</p>
        </div>

        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] ${pillStyles(contact.temperature).bg} ${pillStyles(contact.temperature).text}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${pillStyles(contact.temperature).dot}`} />
          {contact.temperature}
        </span>

        <button className="p-2 rounded-lg hover:bg-gray-100" aria-label="More actions">
          <MoreVertical className="w-5 h-5 text-gray-700" />
        </button>
      </div>
    </header>
  );
}

function pillStyles(temp: Contact['temperature']) {
  return (
    {
      Active: { bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500' },
      New: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
      Warm: { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500' },
      Cold: { bg: 'bg-gray-100', text: 'text-gray-700', dot: 'bg-gray-400' },
      Dormant: { bg: 'bg-slate-100', text: 'text-slate-700', dot: 'bg-slate-400' },
    } as const
  )[temp];
}

function getInitials(name: string) {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

