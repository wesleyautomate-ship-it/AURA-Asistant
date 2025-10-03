/**
 * Workflows Screen - AURA Package Execution
 * ============================================
 * 
 * Main screen for AURA workflow package execution and management.
 * Features:
 * - Available workflow packages
 * - One-click package execution 
 * - Real-time progress tracking
 * - Execution history
 * - Package controls (pause, resume, cancel)
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  ActivityIndicator,
  Modal
} from 'react-native';
import { 
  WorkflowsService, 
  AURAService,
  WorkflowPackageResponse, 
  WorkflowExecutionResponse 
} from '../services/aura';

interface WorkflowsScreenProps {
  onNavigate?: (view: string) => void;
}

export default function WorkflowsScreen({ onNavigate }: WorkflowsScreenProps) {
  const [packages, setPackages] = useState<WorkflowPackageResponse[]>([]);
  const [executions, setExecutions] = useState<WorkflowExecutionResponse[]>([]);
  const [activeExecution, setActiveExecution] = useState<WorkflowExecutionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [executing, setExecuting] = useState<string | null>(null);
  const [showExecutionModal, setShowExecutionModal] = useState(false);

  // Load workflow packages and execution history
  const loadData = useCallback(async () => {
    try {
      const [packagesData, executionsData] = await Promise.all([
        WorkflowsService.getPackages(),
        WorkflowsService.getExecutionHistory(10)
      ]);
      
      setPackages(packagesData);
      setExecutions(executionsData);

      // Check for active execution
      const active = executionsData.find(exec => 
        exec.status === 'running' || exec.status === 'pending'
      );
      setActiveExecution(active || null);

    } catch (error) {
      console.error('Error loading workflows data:', error);
      Alert.alert('Error', 'Failed to load workflow data. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Refresh data
  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    loadData();
  }, [loadData]);

  // Execute workflow package
  const executePackage = async (packageTemplate: string, variables: Record<string, any>) => {
    setExecuting(packageTemplate);
    try {
      const execution = await WorkflowsService.executePackage({
        package_template: packageTemplate as any,
        variables,
        notify_on_completion: true
      });

      setActiveExecution(execution);
      setShowExecutionModal(true);
      await loadData(); // Refresh data

      Alert.alert(
        'Workflow Started',
        `${execution.package_name} is now running. You'll be notified when it completes.`,
        [{ text: 'View Progress', onPress: () => setShowExecutionModal(true) }]
      );

    } catch (error) {
      console.error('Error executing workflow:', error);
      Alert.alert(
        'Execution Failed',
        'Failed to start workflow. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setExecuting(null);
    }
  };

  // Control execution (pause, resume, cancel)
  const controlExecution = async (executionId: string, action: 'pause' | 'resume' | 'cancel') => {
    try {
      await WorkflowsService.controlExecution(executionId, { action });
      await loadData(); // Refresh data
      
      const actionText = action === 'pause' ? 'paused' : action === 'resume' ? 'resumed' : 'cancelled';
      Alert.alert('Success', `Workflow ${actionText} successfully.`);
    } catch (error) {
      console.error('Error controlling workflow:', error);
      Alert.alert('Error', `Failed to ${action} workflow. Please try again.`);
    }
  };

  // Quick execution handlers
  const handleNewListingPackage = (propertyId: number) => {
    Alert.prompt(
      'New Listing Package',
      'Enter Property ID:',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Execute',
          onPress: (text) => {
            const id = parseInt(text || '1', 10);
            executePackage('new_listing', { property_id: id, priority: 'high' });
          }
        }
      ],
      'plain-text',
      propertyId.toString()
    );
  };

  const handleLeadNurturingPackage = () => {
    Alert.prompt(
      'Lead Nurturing Package',
      'Enter Lead ID:',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Execute',
          onPress: (text) => {
            const id = parseInt(text || '1', 10);
            executePackage('lead_nurturing', { lead_id: id, nurturing_type: 'standard' });
          }
        }
      ],
      'plain-text',
      '1'
    );
  };

  const handleClientOnboardingPackage = () => {
    Alert.prompt(
      'Client Onboarding Package',
      'Enter Client ID:',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Execute',
          onPress: (text) => {
            const id = parseInt(text || '1', 10);
            executePackage('client_onboarding', { client_id: id, onboarding_type: 'full' });
          }
        }
      ],
      'plain-text',
      '1'
    );
  };

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading AURA Workflows...</Text>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>AURA Workflows</Text>
        <Text style={styles.subtitle}>One-click automation packages</Text>
      </View>

      {/* Active Execution */}
      {activeExecution && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Active Execution</Text>
          <View style={styles.executionCard}>
            <View style={styles.executionHeader}>
              <Text style={styles.executionTitle}>{activeExecution.package_name}</Text>
              <View style={[styles.statusBadge, { backgroundColor: getStatusColor(activeExecution.status) }]}>
                <Text style={styles.statusText}>{activeExecution.status.toUpperCase()}</Text>
              </View>
            </View>
            
            <View style={styles.progressSection}>
              <Text style={styles.progressLabel}>Progress: {Math.round(activeExecution.progress)}%</Text>
              <View style={styles.progressBar}>
                <View 
                  style={[styles.progressFill, { width: `${activeExecution.progress}%` }]} 
                />
              </View>
            </View>

            <View style={styles.executionActions}>
              <TouchableOpacity
                style={[styles.actionButton, styles.viewButton]}
                onPress={() => setShowExecutionModal(true)}
              >
                <Text style={styles.actionButtonText}>View Details</Text>
              </TouchableOpacity>
              
              {activeExecution.status === 'running' && (
                <TouchableOpacity
                  style={[styles.actionButton, styles.pauseButton]}
                  onPress={() => controlExecution(activeExecution.execution_id, 'pause')}
                >
                  <Text style={styles.actionButtonText}>Pause</Text>
                </TouchableOpacity>
              )}

              {activeExecution.status === 'paused' && (
                <TouchableOpacity
                  style={[styles.actionButton, styles.resumeButton]}
                  onPress={() => controlExecution(activeExecution.execution_id, 'resume')}
                >
                  <Text style={styles.actionButtonText}>Resume</Text>
                </TouchableOpacity>
              )}

              <TouchableOpacity
                style={[styles.actionButton, styles.cancelButton]}
                onPress={() => controlExecution(activeExecution.execution_id, 'cancel')}
              >
                <Text style={styles.actionButtonText}>Cancel</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Launch</Text>
        
        <TouchableOpacity
          style={[styles.packageCard, executing === 'new_listing' && styles.packageCardLoading]}
          onPress={() => handleNewListingPackage(1)}
          disabled={executing !== null}
        >
          <View style={styles.packageHeader}>
            <Text style={styles.packageTitle}>🏢 New Listing Package</Text>
            <Text style={styles.packageDuration}>45 min</Text>
          </View>
          <Text style={styles.packageDescription}>
            Complete property marketing automation: CMA, content, social media, and listing optimization
          </Text>
          {executing === 'new_listing' && (
            <ActivityIndicator size="small" color="#007AFF" style={styles.packageLoader} />
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.packageCard, executing === 'lead_nurturing' && styles.packageCardLoading]}
          onPress={handleLeadNurturingPackage}
          disabled={executing !== null}
        >
          <View style={styles.packageHeader}>
            <Text style={styles.packageTitle}>🎯 Lead Nurturing Package</Text>
            <Text style={styles.packageDuration}>30 min</Text>
          </View>
          <Text style={styles.packageDescription}>
            Automated lead scoring, insights, recommendations, and follow-up sequences
          </Text>
          {executing === 'lead_nurturing' && (
            <ActivityIndicator size="small" color="#007AFF" style={styles.packageLoader} />
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.packageCard, executing === 'client_onboarding' && styles.packageCardLoading]}
          onPress={handleClientOnboardingPackage}
          disabled={executing !== null}
        >
          <View style={styles.packageHeader}>
            <Text style={styles.packageTitle}>👋 Client Onboarding Package</Text>
            <Text style={styles.packageDuration}>20 min</Text>
          </View>
          <Text style={styles.packageDescription}>
            Welcome sequences, market briefing, service overview, and portal setup
          </Text>
          {executing === 'client_onboarding' && (
            <ActivityIndicator size="small" color="#007AFF" style={styles.packageLoader} />
          )}
        </TouchableOpacity>
      </View>

      {/* Recent Executions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Executions</Text>
        {executions.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No executions yet</Text>
            <Text style={styles.emptyStateSubtext}>Start your first AURA workflow above</Text>
          </View>
        ) : (
          executions.slice(0, 5).map((execution, index) => (
            <View key={execution.execution_id || index} style={styles.executionItem}>
              <View style={styles.executionItemHeader}>
                <Text style={styles.executionItemTitle}>{execution.package_name}</Text>
                <View style={[styles.statusBadge, styles.statusBadgeSmall, { backgroundColor: getStatusColor(execution.status) }]}>
                  <Text style={[styles.statusText, styles.statusTextSmall]}>{execution.status.toUpperCase()}</Text>
                </View>
              </View>
              <Text style={styles.executionItemTime}>
                {execution.started_at ? new Date(execution.started_at).toLocaleString() : 'Recently'}
              </Text>
              {execution.status === 'completed' && execution.completed_at && (
                <Text style={styles.executionItemDuration}>
                  Completed in {Math.round((new Date(execution.completed_at).getTime() - 
                    new Date(execution.started_at!).getTime()) / 60000)} minutes
                </Text>
              )}
            </View>
          ))
        )}
      </View>

      {/* Execution Details Modal */}
      <Modal
        visible={showExecutionModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowExecutionModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>
              {activeExecution?.package_name || 'Execution Details'}
            </Text>
            <TouchableOpacity
              style={styles.modalCloseButton}
              onPress={() => setShowExecutionModal(false)}
            >
              <Text style={styles.modalCloseText}>Done</Text>
            </TouchableOpacity>
          </View>

          {activeExecution && (
            <ScrollView style={styles.modalContent}>
              <View style={styles.modalSection}>
                <Text style={styles.modalSectionTitle}>Status</Text>
                <View style={styles.modalStatusRow}>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(activeExecution.status) }]}>
                    <Text style={styles.statusText}>{activeExecution.status.toUpperCase()}</Text>
                  </View>
                  <Text style={styles.modalProgressText}>{Math.round(activeExecution.progress)}% Complete</Text>
                </View>
              </View>

              <View style={styles.modalSection}>
                <Text style={styles.modalSectionTitle}>Progress</Text>
                <View style={styles.progressBar}>
                  <View 
                    style={[styles.progressFill, { width: `${activeExecution.progress}%` }]} 
                  />
                </View>
                <Text style={styles.modalProgressLabel}>
                  {activeExecution.estimated_completion && 
                    `Estimated completion: ${new Date(activeExecution.estimated_completion).toLocaleTimeString()}`
                  }
                </Text>
              </View>

              <View style={styles.modalSection}>
                <Text style={styles.modalSectionTitle}>Execution Steps</Text>
                {activeExecution.steps.map((step, index) => (
                  <View key={index} style={styles.stepItem}>
                    <View style={[styles.stepIndicator, { 
                      backgroundColor: index < activeExecution.progress / (100 / activeExecution.steps.length) ? '#4CAF50' : '#E0E0E0' 
                    }]} />
                    <Text style={styles.stepText}>
                      {step.step_name || `Step ${index + 1}`}
                    </Text>
                  </View>
                ))}
              </View>

              <View style={styles.modalSection}>
                <Text style={styles.modalSectionTitle}>Timeline</Text>
                <Text style={styles.modalTimelineText}>
                  Started: {activeExecution.started_at ? 
                    new Date(activeExecution.started_at).toLocaleString() : 'Recently'
                  }
                </Text>
                {activeExecution.completed_at && (
                  <Text style={styles.modalTimelineText}>
                    Completed: {new Date(activeExecution.completed_at).toLocaleString()}
                  </Text>
                )}
              </View>
            </ScrollView>
          )}
        </View>
      </Modal>
    </ScrollView>
  );
}

// Helper function to get status color
function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'completed':
      return '#4CAF50';
    case 'running':
    case 'pending':
      return '#2196F3';
    case 'paused':
      return '#FF9800';
    case 'cancelled':
    case 'failed':
      return '#F44336';
    default:
      return '#9E9E9E';
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  header: {
    padding: 20,
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  section: {
    margin: 16,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  packageCard: {
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  packageCardLoading: {
    opacity: 0.7,
  },
  packageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  packageTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  packageDuration: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  packageDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  packageLoader: {
    marginTop: 8,
    alignSelf: 'center',
  },
  executionCard: {
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  executionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  executionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusBadgeSmall: {
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFF',
  },
  statusTextSmall: {
    fontSize: 10,
  },
  progressSection: {
    marginBottom: 16,
  },
  progressLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 6,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
  },
  executionActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  viewButton: {
    backgroundColor: '#007AFF',
  },
  pauseButton: {
    backgroundColor: '#FF9800',
  },
  resumeButton: {
    backgroundColor: '#4CAF50',
  },
  cancelButton: {
    backgroundColor: '#F44336',
  },
  actionButtonText: {
    color: '#FFF',
    fontSize: 14,
    fontWeight: '500',
  },
  executionItem: {
    backgroundColor: '#FFF',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  executionItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  executionItemTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    flex: 1,
  },
  executionItemTime: {
    fontSize: 12,
    color: '#666',
  },
  executionItemDuration: {
    fontSize: 12,
    color: '#4CAF50',
    marginTop: 2,
  },
  emptyState: {
    alignItems: 'center',
    padding: 24,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 4,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#999',
  },
  // Modal styles
  modalContainer: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  modalCloseButton: {
    padding: 4,
  },
  modalCloseText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  modalContent: {
    flex: 1,
    padding: 16,
  },
  modalSection: {
    marginBottom: 24,
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  modalStatusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  modalProgressText: {
    fontSize: 14,
    color: '#666',
  },
  modalProgressLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 6,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  stepIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 12,
  },
  stepText: {
    fontSize: 14,
    color: '#333',
  },
  modalTimelineText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
});
