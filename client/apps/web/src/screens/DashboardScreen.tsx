import React, { useMemo } from 'react';
import { useWindowDimensions } from 'react-native';
import DashboardView from '../components/DashboardView';
import DashboardViewMobile from '../components/DashboardView.mobile';
import type { ActionId, Request, View as AppView } from '../types';

interface Props {
  onActionClick: (id: ActionId) => void;
  onRequestClick: (request: Request) => void;
  onNavigate: (view: AppView) => void;
}

const MOBILE_BREAKPOINT = 768;

export default function DashboardScreen({ onActionClick, onRequestClick, onNavigate }: Props) {
  const { width } = useWindowDimensions();

  const isMobile = width < MOBILE_BREAKPOINT;

  // Hook up navigation by proxying request or action taps.
  const handleActionClick = useMemo(() => onActionClick, [onActionClick]);
  const handleRequestClick = useMemo(() => onRequestClick, [onRequestClick]);

  if (isMobile) {
    return (
      <DashboardViewMobile
        onActionClick={(id) => {
          handleActionClick(id);
          onNavigate('tasks');
        }}
        onRequestClick={handleRequestClick}
      />
    );
  }

  return <DashboardView onActionClick={handleActionClick} onRequestClick={handleRequestClick} />;
}
