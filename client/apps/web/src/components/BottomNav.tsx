import React, { useMemo } from 'react';
import type { View as AppView } from '../types';
import type { CommandMode, CommandStatus } from '../store/uiStore';

const classNames = (...classes: Array<string | false | null | undefined>) =>
  classes.filter(Boolean).join(' ');

interface Props {
  activeView: AppView;
  onNavigate: (v: AppView) => void;
  onOpenCommandCenter: () => void;
  commandMode: CommandMode;
  commandStatus: CommandStatus;
  isCommandCenterOpen: boolean;
}

const BottomNav: React.FC<Props> = ({
  activeView,
  onNavigate,
  onOpenCommandCenter,
  commandMode,
  commandStatus,
  isCommandCenterOpen,
}) => {
  const navItems: Array<{ label: string; view: AppView }> = useMemo(
    () => [
      { label: 'Dashboard', view: 'dashboard' },
      { label: 'Tasks', view: 'tasks' },
      { label: 'Chat', view: 'chat' },
      { label: 'Properties', view: 'properties' },
      { label: 'Profile', view: 'profile' },
    ],
    []
  );

  const renderCommandIcon = () => {
    if (commandStatus === 'processing') {
      return (
        <span className="relative flex h-6 w-6 items-center justify-center" aria-hidden>
          <span className="absolute h-full w-full animate-spin rounded-full border-2 border-white/40 border-t-white" />
        </span>
      );
    }

    if (commandMode === 'audio' && commandStatus === 'recording') {
      return (
        <span className="flex h-6 w-6 items-center justify-center" aria-hidden>
          <span className="h-3 w-3 animate-pulse rounded-full bg-red-400" />
        </span>
      );
    }

    if (commandMode === 'text' && (commandStatus === 'typing' || isCommandCenterOpen)) {
      return (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          className="h-6 w-6 text-white"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.8}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M16.862 4.487a2.25 2.25 0 113.182 3.182L7.5 20.213l-4.5 1.031 1.031-4.5 12.831-12.257z"
          />
        </svg>
      );
    }

    return <span className="text-2xl font-bold leading-none text-white">+</span>;
  };

  return (
    <nav className="sticky bottom-0 z-30 flex items-center justify-between border-t border-slate-200 bg-white px-6 py-3">
      <div className="flex items-center gap-4">
        {navItems.slice(0, 2).map((item) => (
          <button
            key={item.view}
            type="button"
            onClick={() => onNavigate(item.view)}
            className={classNames(
              'text-xs font-semibold transition-colors focus:outline-none',
              activeView === item.view ? 'text-slate-900' : 'text-slate-500 hover:text-slate-900'
            )}
          >
            {item.label}
          </button>
        ))}
      </div>

      <button
        type="button"
        onClick={onOpenCommandCenter}
        className={classNames(
          'flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition-all focus:outline-none',
          isCommandCenterOpen || commandStatus === 'processing'
            ? 'bg-slate-900 shadow-slate-500/40'
            : commandMode === 'audio' && commandStatus === 'recording'
            ? 'bg-red-500'
            : 'bg-slate-900 hover:scale-105 hover:shadow-xl'
        )}
        aria-label="Open command center"
      >
        {renderCommandIcon()}
      </button>

      <div className="flex items-center gap-4">
        {navItems.slice(2).map((item) => (
          <button
            key={item.view}
            type="button"
            onClick={() => onNavigate(item.view)}
            className={classNames(
              'text-xs font-semibold transition-colors focus:outline-none',
              activeView === item.view ? 'text-slate-900' : 'text-slate-500 hover:text-slate-900'
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
    </nav>
  );
};

export default BottomNav;
