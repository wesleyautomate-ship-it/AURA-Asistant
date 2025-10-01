import React, { useMemo } from 'react';
import {
  ScrollView,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Image,
} from 'react-native';
import { ACTION_ITEMS, MOCK_REQUESTS } from '../constants';
import type { ActionId, Request } from '../types';

interface DashboardViewProps {
  onActionClick: (id: ActionId) => void;
  onRequestClick: (request: Request) => void;
}

// Mobile layout sections: header, KPI stack, AI workspace queue, action grid, recent activity
const DashboardViewMobile: React.FC<DashboardViewProps> = ({ onActionClick, onRequestClick }) => {
  const metrics = useMemo(
    () => {
      const activeRequests = MOCK_REQUESTS.length;
      const averageProgress =
        activeRequests === 0
          ? 0
          : Math.round(
              MOCK_REQUESTS.reduce((total, request) => total + request.progress, 0) /
                activeRequests,
            );

      return [
        { label: 'Active Requests', value: String(activeRequests) },
        { label: 'Average Progress', value: `${averageProgress}%` },
        { label: 'AI Efficiency', value: '92%' },
      ];
    },
    [],
  );

  const recentActivity = useMemo(
    () =>
      MOCK_REQUESTS.map((request) => ({
        id: request.id,
        title: request.title,
        status: request.status,
        eta: request.eta,
      })),
    [],
  );

  const renderRequestCard = (request: Request) => (
    <TouchableOpacity
      key={request.id}
      onPress={() => onRequestClick(request)}
      activeOpacity={0.85}
      style={styles.requestCard}
    >
      {request.image ? (
        <Image source={{ uri: request.image }} style={styles.requestImage} />
      ) : (
        <View style={styles.requestPlaceholder}>
          <Text style={styles.requestPlaceholderText}>AI</Text>
        </View>
      )}
      <View style={styles.requestBody}>
        <View style={styles.requestHeader}>
          <View style={styles.categoryPill}>
            <Text style={styles.categoryPillText}>{request.category}</Text>
          </View>
          <Text style={styles.requestEta}>{request.eta}</Text>
        </View>
        <Text style={styles.requestTitle} numberOfLines={2}>
          {request.title}
        </Text>
        <View style={styles.requestFooter}>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${request.progress}%` }]} />
          </View>
          <Text style={styles.requestStatus}>{request.status}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>PropertyPro AI</Text>
        <Text style={styles.subtitle}>Your mobile real estate operations hub</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionHeading}>Today's KPIs</Text>
        <View style={styles.metricsColumn}>
          {metrics.map((item) => (
            <View key={item.label} style={styles.metricCard}>
              <Text style={styles.metricValue}>{item.value}</Text>
              <Text style={styles.metricLabel}>{item.label}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionHeading}>AI Workspace</Text>
        <View style={styles.sectionDescriptionWrap}>
          <Text style={styles.sectionDescription}>
            Stay on top of active marketing and analytics automations.
          </Text>
          <View style={styles.badge}>
            <Text style={styles.badgeText}>{MOCK_REQUESTS.length}</Text>
          </View>
        </View>
        <View>{MOCK_REQUESTS.map(renderRequestCard)}</View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionHeading}>Quick Actions</Text>
        <Text style={styles.sectionDescription}>
          Launch a workspace or workflow with a single tap.
        </Text>
        <View style={styles.actionGrid}>
          {ACTION_ITEMS.map((item) => (
            <TouchableOpacity
              key={item.id}
              style={styles.actionCard}
              activeOpacity={0.85}
              onPress={() => onActionClick(item.id)}
            >
              <View style={[styles.actionIcon, { backgroundColor: resolveColor(item.color) }]}>
                <Text style={styles.actionIconText}>{getInitials(item.title)}</Text>
              </View>
              <Text style={styles.actionTitle}>{item.title}</Text>
              <Text style={styles.actionSubtitle} numberOfLines={2}>
                {item.subtitle}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={[styles.section, styles.sectionLast]}>
        <Text style={styles.sectionHeading}>Recent Activity</Text>
        <View style={styles.activityList}>
          {recentActivity.map((item, index) => (
            <View
              key={item.id}
              style={[styles.activityRow, index === recentActivity.length - 1 && styles.activityRowLast]}
            >
              <View>
                <Text style={styles.activityTitle} numberOfLines={1}>
                  {item.title}
                </Text>
                <Text style={styles.activityMeta}>{item.status}</Text>
              </View>
              <Text style={styles.activityEta}>{item.eta}</Text>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
};

const TAILWIND_COLOR_MAP: Record<string, string> = {
  'bg-red-100': '#fee2e2',
  'bg-indigo-100': '#e0e7ff',
  'bg-amber-100': '#fef3c7',
  'bg-teal-100': '#d1fae5',
  'bg-emerald-100': '#d1fae5',
  'bg-fuchsia-100': '#fae8ff',
  'bg-orange-100': '#ffedd5',
};

function resolveColor(colorToken: string) {
  return TAILWIND_COLOR_MAP[colorToken] ?? '#e5e7eb';
}

function getInitials(text: string) {
  const words = text.trim().split(' ');
  if (words.length === 1) {
    return words[0].slice(0, 2).toUpperCase();
  }
  return `${words[0][0]}${words[1][0]}`.toUpperCase();
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 20,
    paddingBottom: 32,
    backgroundColor: '#F9FAFB',
  },
  header: {
    paddingTop: 24,
    paddingBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
  },
  subtitle: {
    marginTop: 4,
    fontSize: 14,
    color: '#6B7280',
  },
  section: {
    marginBottom: 24,
  },
  sectionLast: {
    marginBottom: 48,
  },
  sectionHeading: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  sectionDescriptionWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  sectionDescription: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 12,
  },
  badge: {
    backgroundColor: '#111827',
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  badgeText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 13,
  },
  metricsColumn: {
    flexDirection: 'column',
  },
  metricCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingVertical: 16,
    paddingHorizontal: 20,
    shadowColor: '#000000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 1,
    marginBottom: 12,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 13,
    color: '#6B7280',
  },
  requestCard: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    marginBottom: 12,
  },
  requestImage: {
    width: 96,
    height: 96,
  },
  requestPlaceholder: {
    width: 96,
    height: 96,
    backgroundColor: '#111827',
    alignItems: 'center',
    justifyContent: 'center',
  },
  requestPlaceholderText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '700',
  },
  requestBody: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  requestHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  categoryPill: {
    backgroundColor: '#EEF2FF',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  categoryPillText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#4338CA',
  },
  requestEta: {
    fontSize: 11,
    color: '#6B7280',
  },
  requestTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    flexShrink: 1,
  },
  requestFooter: {
    marginTop: 10,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#E5E7EB',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: 4,
    backgroundColor: '#2563EB',
  },
  requestStatus: {
    marginTop: 6,
    fontSize: 12,
    fontWeight: '600',
    color: '#2563EB',
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 12,
  },
  actionCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    paddingVertical: 18,
    paddingHorizontal: 16,
    shadowColor: '#000000',
    shadowOpacity: 0.04,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 1,
    marginBottom: 16,
  },
  actionIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  actionIconText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 6,
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#6B7280',
  },
  activityList: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  activityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    paddingHorizontal: 18,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  activityRowLast: {
    borderBottomWidth: 0,
  },
  activityTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4,
    maxWidth: 200,
  },
  activityMeta: {
    fontSize: 12,
    color: '#6B7280',
  },
  activityEta: {
    fontSize: 12,
    fontWeight: '600',
    color: '#2563EB',
  },
});

export default DashboardViewMobile;
