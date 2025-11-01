import type { ReactNode } from 'react';
import { ChevronLeft, Mail, MapPin, MoreVertical, Phone, Wallet } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { LeadTemperature } from '../../types/contacts';

interface ContactHeaderProps {
  name: string;
  initials?: string;
  avatarUrl?: string;
  temperature: LeadTemperature;
  phone?: string;
  email?: string;
  area?: string | null;
  budgetLabel?: string | null;
  pipeline?: string | null;
  onBack?: () => void;
}

const tempStyles: Record<LeadTemperature, { bg: string; text: string; dot: string }> = {
  Active: { bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500' },
  New: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
  Warm: { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500' },
  Cold: { bg: 'bg-gray-100', text: 'text-gray-700', dot: 'bg-gray-400' },
  Dormant: { bg: 'bg-slate-100', text: 'text-slate-700', dot: 'bg-slate-400' },
};

export default function ContactHeader({
  name,
  initials,
  avatarUrl,
  temperature,
  phone,
  email,
  area,
  budgetLabel,
  pipeline,
  onBack,
}: ContactHeaderProps) {
  const navigate = useNavigate();
  const chips = tempStyles[temperature] ?? tempStyles.Warm;

  const renderInitials = () => {
    if (avatarUrl) {
      return <img src={avatarUrl} alt={name} className="w-11 h-11 rounded-full border border-gray-200 object-cover" />;
    }
    const derivedInitials = initials ?? buildInitials(name);
    return (
      <div className="w-11 h-11 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 border border-gray-200 flex items-center justify-center">
        <span className="text-sm font-semibold text-gray-700">{derivedInitials}</span>
      </div>
    );
  };

  const phoneHref = phone ? `tel:${phone.replace(/\s+/g, '')}` : undefined;
  const emailHref = email ? `mailto:${email}` : undefined;

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate('/contacts');
    }
  };

  return (
    <section className="bg-white border border-gray-200 rounded-3xl shadow-sm max-w-3xl mx-auto mt-4 mb-4 px-4 py-4 sm:px-6 sm:py-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleBack}
            className="inline-flex items-center justify-center w-9 h-9 rounded-xl border border-gray-200 text-gray-600 hover:bg-gray-50"
            aria-label="Back to contacts"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          {renderInitials()}
          <div className="min-w-0">
            <p className="text-base font-semibold text-gray-900 truncate">{name}</p>
            {pipeline ? (
              <p className="text-xs text-gray-500 truncate">{pipeline}</p>
            ) : (
              <p className="text-xs text-gray-500 truncate">&nbsp;</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs ${chips.bg} ${chips.text}`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${chips.dot}`} aria-hidden="true" />
            {temperature}
          </span>
          <button
            type="button"
            className="inline-flex items-center justify-center w-9 h-9 rounded-xl border border-gray-200 text-gray-500 hover:bg-gray-50"
            aria-label="More actions"
          >
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mt-4 grid gap-2 text-sm sm:text-base">
        <InfoRow
          icon={<Phone className="w-4 h-4 text-blue-600" />}
          label={phone ? formatPhone(phone) : 'No phone on file'}
          href={phoneHref}
        />
        <InfoRow
          icon={<Mail className="w-4 h-4 text-emerald-600" />}
          label={email || 'No email on file'}
          href={emailHref}
        />
        <InfoRow
          icon={<MapPin className="w-4 h-4 text-purple-600" />}
          label={area || 'No area specified'}
        />
        <InfoRow
          icon={<Wallet className="w-4 h-4 text-amber-600" />}
          label={budgetLabel || 'Budget not provided'}
        />
      </div>
    </section>
  );
}

function InfoRow({ icon, label, href }: { icon: ReactNode; label: string; href?: string }) {
  const content = (
    <div className="flex items-center gap-3 rounded-2xl border border-gray-200 px-3 py-2 hover:border-gray-300 transition">
      <span className="inline-flex items-center justify-center w-8 h-8 rounded-xl bg-gray-100">{icon}</span>
      <span className="text-sm text-gray-800 truncate">{label}</span>
    </div>
  );

  if (href) {
    return (
      <a href={href} className="block" rel="noreferrer">
        {content}
      </a>
    );
  }

  return content;
}

function buildInitials(name: string) {
  const parts = name.trim().split(/\s+/);
  if (!parts.length) return '?';
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return `${parts[0].charAt(0)}${parts[parts.length - 1].charAt(0)}`.toUpperCase();
}

function formatPhone(phone: string) {
  return phone.trim();
}
