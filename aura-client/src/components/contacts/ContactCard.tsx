import React from 'react';
import { Contact } from '../../types/contacts';

const tempStyles: Record<Contact['temperature'], { bg: string; text: string; dot: string }> = {
  Active: { bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500' },
  New: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
  Warm: { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500' },
  Cold: { bg: 'bg-gray-100', text: 'text-gray-700', dot: 'bg-gray-400' },
  Dormant: { bg: 'bg-slate-100', text: 'text-slate-700', dot: 'bg-slate-400' },
};

export interface ContactCardProps {
  contact: Contact;
  onClick?: (contact: Contact) => void;
}

export default function ContactCard({ contact, onClick }: ContactCardProps) {
  const style = tempStyles[contact.temperature];
  const initials = contact.initials ?? getInitials(contact.name);

  return (
    <button
      onClick={() => onClick?.(contact)}
      className="w-full text-left"
      aria-label={`Open ${contact.name}`}
    >
      <div className="flex items-center gap-3">
        {/* Avatar */}
        {contact.avatarUrl ? (
          <img
            src={contact.avatarUrl}
            alt={contact.name}
            className="w-10 h-10 rounded-full object-cover border border-gray-200"
          />
        ) : (
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 border border-gray-200 flex items-center justify-center">
            <span className="text-sm font-semibold text-gray-700">{initials}</span>
          </div>
        )}

        {/* Main */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm sm:text-base font-medium text-gray-900 truncate">{contact.name}</p>
            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] sm:text-xs ${style.bg} ${style.text}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} aria-hidden="true" />
              {contact.temperature}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            Last activity • {contact.lastActivityAt ? timeAgo(contact.lastActivityAt) : '—'}
          </p>
        </div>
      </div>
    </button>
  );
}

function getInitials(name: string) {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

function timeAgo(iso: string) {
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

