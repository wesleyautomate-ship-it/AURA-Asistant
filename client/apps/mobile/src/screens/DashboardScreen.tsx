import React, { useState, useEffect, useCallback } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  ScrollView, 
  RefreshControl,
  ActivityIndicator,
  Alert
} from 'react-native';
import type { ActionId, View as AppView } from '../types';
import { 
  AURAService, 
  AnalyticsService,
  DashboardOverview, 
  PerformanceMetrics,
  MarketInsights,
  WorkflowExecutionResponse
} from '../services/aura';

interface Props {
  actions: { id: ActionId; title: string; icon?: string }[];
  onActionClick: (id: ActionId) => void;
  onNavigate: (v: AppView) => void;
}

interface DashboardData {
  overview?: DashboardOverview;
  performance?: PerformanceMetrics;
  market_insights?: MarketInsights;
  recent_executions?: WorkflowExecutionResponse[];
}

export default function DashboardScreen({ actions, onActionClick, onNavigate }: Props) {
  const [dashboardData, setDashboardData] = useState<DashboardData>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'degraded' | 'unhealthy' | null>(null);

  // Load dashboard data from AURA APIs
  const loadDashboardData = useCallback(async () => {
    try {
      // Get comprehensive dashboard data
      const data = await AURAService.getDashboard('30days');
      setDashboardData(data);

      // Check AURA system health
      const health = await AURAService.healthCheck();
      setHealthStatus(health.status);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Don't show error for dashboard - just log it
      // This allows the app to work even if AURA backend is not available
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    loadDashboardData();
  }, [loadDashboardData]);

  // Load data on component mount
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Format currency for display
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-AE', {
      style: 'currency',
      currency: 'AED',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Format percentage
  const formatPercentage = (value: number) => `${value.toFixed(1)}%`;

  return (
    <ScrollView 
      contentContainerStyle={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>PropertyPro AI</Text>
          <Text style={styles.subtitle}>AURA-Powered Real Estate Assistant</Text>
        </View>
        {healthStatus && (
          <View style={[
            styles.healthIndicator, 
            { backgroundColor: getHealthColor(healthStatus) }
          ]}>
            <Text style={styles.healthText}>
              {healthStatus === 'healthy' ? '●' : healthStatus === 'degraded' ? '◐' : '○'}
            </Text>
          </View>
        )}
      </View>

      {/* Quick Navigation */}
      <View style={styles.quickNav}>
        <TouchableOpacity style={styles.quickBtn} onPress={() => onNavigate('tasks')}>
          <Text style={styles.quickText}>Tasks</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickBtn} onPress={() => onNavigate('chat')}>
          <Text style={styles.quickText}>Chat</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.quickBtn, styles.workflowBtn]} onPress={() => onNavigate('workflows')}>
          <Text style={styles.quickText}>🚀 AURA</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickBtn} onPress={() => onNavigate('analytics')}>
          <Text style={styles.quickText}>Analytics</Text>
        </TouchableOpacity>
      </View>

      {/* AURA Dashboard Stats */}
      {dashboardData.overview && !loading ? (
        <View style={styles.statsSection}>
          <Text style={styles.sectionTitle}>Performance Overview</Text>
          
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{dashboardData.overview.property_performance.total_listings}</Text>
              <Text style={styles.statLabel}>Total Listings</Text>
            </View>
            
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{dashboardData.overview.property_performance.sold_listings}</Text>
              <Text style={styles.statLabel}>Sold</Text>
            </View>
            
            <View style={styles.statCard}>
              <Text style={[styles.statValue, styles.statValueCurrency]}>
                {formatCurrency(dashboardData.overview.property_performance.total_revenue)}
              </Text>
              <Text style={styles.statLabel}>Revenue</Text>
            </View>
            
            <View style={styles.statCard}>
              <Text style={styles.statValue}>
                {formatPercentage(dashboardData.overview.lead_performance.conversion_rate)}
              </Text>
              <Text style={styles.statLabel}>Conversion</Text>
            </View>
          </View>
          
          {/* Market Insights */}
          {dashboardData.market_insights && (
            <View style={styles.marketCard}>
              <Text style={styles.marketTitle}>Dubai Market Snapshot</Text>
              <View style={styles.marketRow}>
                <Text style={styles.marketLabel}>Avg Price/SqFt:</Text>
                <Text style={styles.marketValue}>
                  {formatCurrency(dashboardData.market_insights.avg_price_psf)}
                </Text>
              </View>
              <View style={styles.marketRow}>
                <Text style={styles.marketLabel}>Price Trend:</Text>
                <Text style={[
                  styles.marketValue, 
                  { color: dashboardData.market_insights.price_trend > 0 ? '#4CAF50' : '#F44336' }
                ]}>
                  {dashboardData.market_insights.price_trend > 0 ? '+' : ''}
                  {formatPercentage(dashboardData.market_insights.price_trend)}
                </Text>
              </View>
              <View style={styles.marketRow}>
                <Text style={styles.marketLabel}>Market Activity:</Text>
                <Text style={styles.marketValue}>{dashboardData.market_insights.inventory_levels}</Text>
              </View>
            </View>
          )}
          
          {/* Recent AURA Executions */}
          {dashboardData.recent_executions && dashboardData.recent_executions.length > 0 && (
            <View style={styles.executionsCard}>
              <Text style={styles.executionsTitle}>Recent AURA Workflows</Text>
              {dashboardData.recent_executions.slice(0, 3).map((execution, index) => (
                <View key={execution.execution_id || index} style={styles.executionItem}>
                  <View style={styles.executionHeader}>
                    <Text style={styles.executionName}>{execution.package_name}</Text>
                    <View style={[
                      styles.executionStatus, 
                      { backgroundColor: getStatusColor(execution.status) }
                    ]}>
                      <Text style={styles.executionStatusText}>{execution.status}</Text>
                    </View>
                  </View>
                  {execution.progress !== undefined && (
                    <View style={styles.progressBar}>
                      <View style={[
                        styles.progressFill, 
                        { width: `${execution.progress}%` }
                      ]} />
                    </View>
                  )}
                </View>
              ))}
            </View>
          )}
        </View>
      ) : loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading AURA Dashboard...</Text>
        </View>
      ) : null}

      {/* Action Grid */}
      <View style={styles.actionsSection}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.grid}>
          {actions.map((a) => (
            <TouchableOpacity 
              key={a.id} 
              style={[
                styles.card, 
                a.id === 'workflows' && styles.workflowCard
              ]} 
              onPress={() => onActionClick(a.id)}
            >
              <Text style={[
                styles.cardTitle,
                a.id === 'workflows' && styles.workflowCardTitle
              ]}>
                {a.id === 'workflows' ? '🚀 ' : ''}{a.title}
              </Text>
              {a.id === 'workflows' && (
                <Text style={styles.cardSubtitle}>One-click automation</Text>
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

// Helper functions
function getHealthColor(status: string): string {
  switch (status) {
    case 'healthy': return '#4CAF50';
    case 'degraded': return '#FF9800';
    case 'unhealthy': return '#F44336';
    default: return '#9E9E9E';
  }
}

function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'completed': return '#4CAF50';
    case 'running': case 'pending': return '#2196F3';
    case 'paused': return '#FF9800';
    case 'failed': case 'cancelled': return '#F44336';
    default: return '#9E9E9E';
  }
}

const styles = StyleSheet.create({
  container: { 
    padding: 16,
    backgroundColor: '#F5F5F5'
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  title: { 
    fontSize: 24, 
    fontWeight: 'bold', 
    color: '#333',
    marginBottom: 4
  },
  subtitle: { 
    fontSize: 14, 
    color: '#666' 
  },
  healthIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center'
  },
  healthText: {
    color: '#FFF',
    fontSize: 8,
    fontWeight: 'bold'
  },
  quickNav: { 
    flexDirection: 'row', 
    gap: 8, 
    marginBottom: 16 
  },
  quickBtn: { 
    backgroundColor: '#111827', 
    paddingHorizontal: 12, 
    paddingVertical: 8, 
    borderRadius: 20,
    minWidth: 70,
    alignItems: 'center'
  },
  workflowBtn: {
    backgroundColor: '#007AFF'
  },
  quickText: { 
    color: 'white', 
    fontWeight: '700',
    fontSize: 12
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 32,
    backgroundColor: '#FFF',
    borderRadius: 12,
    marginBottom: 16
  },
  loadingText: {
    marginTop: 8,
    color: '#666',
    fontSize: 16
  },
  statsSection: {
    marginBottom: 20
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16
  },
  statCard: {
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 12,
    width: '48%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4
  },
  statValueCurrency: {
    fontSize: 18
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center'
  },
  marketCard: {
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1
  },
  marketTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12
  },
  marketRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  marketLabel: {
    fontSize: 14,
    color: '#666'
  },
  marketValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333'
  },
  executionsCard: {
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1
  },
  executionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12
  },
  executionItem: {
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'
  },
  executionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  executionName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    flex: 1
  },
  executionStatus: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8
  },
  executionStatusText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#FFF'
  },
  progressBar: {
    height: 4,
    backgroundColor: '#E0E0E0',
    borderRadius: 2,
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF'
  },
  actionsSection: {
    marginTop: 8
  },
  grid: { 
    flexDirection: 'row', 
    flexWrap: 'wrap', 
    gap: 12 
  },
  card: { 
    backgroundColor: '#F9FAFB', 
    padding: 16, 
    borderRadius: 12, 
    width: '48%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1
  },
  workflowCard: {
    backgroundColor: '#E3F2FD',
    borderWidth: 1,
    borderColor: '#007AFF'
  },
  cardTitle: { 
    color: '#111827', 
    fontWeight: '700',
    fontSize: 14,
    marginBottom: 4
  },
  workflowCardTitle: {
    color: '#007AFF'
  },
  cardSubtitle: {
    fontSize: 12,
    color: '#666'
  }
});

