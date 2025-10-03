import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { Milestone, MilestoneType } from '@propertypro/features/types';

export type TransactionTimelineProps = {
  milestones: Milestone[];
  onMilestonePress?: (milestone: Milestone) => void;
};

const milestoneIcons: Record<MilestoneType, keyof typeof MaterialIcons.glyphMap> = {
  offer_submitted: 'gavel',
  offer_accepted: 'thumb-up',
  contract_signed: 'assignment',
  inspection: 'home-repair-service',
  appraisal: 'assessment',
  financing_approved: 'account-balance',
  closing: 'gavel',
  possession: 'keyboard-return',
};

const milestoneTitles: Record<MilestoneType, string> = {
  offer_submitted: 'Offer Submitted',
  offer_accepted: 'Offer Accepted',
  contract_signed: 'Contract Signed',
  inspection: 'Inspection',
  appraisal: 'Appraisal',
  financing_approved: 'Financing Approved',
  closing: 'Closing',
  possession: 'Possession',
};

const TransactionTimeline: React.FC<TransactionTimelineProps> = ({ milestones, onMilestonePress }) => {
  const sortedMilestones = [...milestones].sort(
    (a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
  );

  return (
    <View style={styles.container}>
      {sortedMilestones.map((milestone, index) => (
        <TouchableOpacity
          key={milestone.id}
          style={styles.milestoneItem}
          onPress={() => onMilestonePress?.(milestone)}
          activeOpacity={0.7}
        >
          <View style={styles.milestoneLeft}>
            <View
              style={[
                styles.milestoneIconContainer,
                milestone.completed ? styles.completedIcon : styles.pendingIcon,
              ]}
            >
              <MaterialIcons
                name={milestoneIcons[milestone.type]}
                size={20}
                color={milestone.completed ? '#fff' : '#ea580c'}
              />
            </View>
            {index < sortedMilestones.length - 1 && <View style={styles.connectorLine} />}
          </View>
          <View style={styles.milestoneContent}>
            <View style={styles.milestoneHeader}>
              <Text style={styles.milestoneTitle}>
                {milestone.title || milestoneTitles[milestone.type]}
              </Text>
              <Text style={styles.milestoneDate}>
                {new Date(milestone.dueDate).toLocaleDateString()}
              </Text>
            </View>
            <Text style={styles.milestoneDescription} numberOfLines={2}>
              {milestone.description}
            </Text>
            {milestone.completed && milestone.completedAt && (
              <View style={styles.completedBadge}>
                <MaterialIcons name="check" size={12} color="#fff" />
                <Text style={styles.completedText}>
                  Completed on {new Date(milestone.completedAt).toLocaleDateString()}
                </Text>
              </View>
            )}
            {milestone.documents && milestone.documents.length > 0 && (
              <View style={styles.documentsContainer}>
                <MaterialIcons name="attachment" size={14} color="#6b7280" />
                <Text style={styles.documentsText}>
                  {milestone.documents.length} document{milestone.documents.length > 1 ? 's' : ''}
                </Text>
              </View>
            )}
          </View>
        </TouchableOpacity>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  milestoneItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  milestoneLeft: {
    width: 40,
    alignItems: 'center',
    marginRight: 12,
  },
  milestoneIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    position: 'relative',
  },
  completedIcon: {
    backgroundColor: '#ea580c',
    borderColor: '#ea580c',
  },
  pendingIcon: {
    backgroundColor: 'transparent',
    borderColor: '#d1d5db',
  },
  connectorLine: {
    position: 'absolute',
    width: 2,
    backgroundColor: '#d1d5db',
    top: 48,
    bottom: -16,
    left: '50%',
    marginLeft: -1,
  },
  milestoneContent: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 1,
  },
  milestoneHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  milestoneTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    flex: 1,
    marginRight: 8,
  },
  milestoneDate: {
    fontSize: 12,
    color: '#6b7280',
  },
  milestoneDescription: {
    fontSize: 13,
    color: '#4b5563',
    marginBottom: 8,
  },
  completedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ecfdf5',
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 4,
    alignSelf: 'flex-start',
    marginTop: 4,
  },
  completedText: {
    fontSize: 11,
    color: '#065f46',
    marginLeft: 4,
    fontWeight: '500',
  },
  documentsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  documentsText: {
    fontSize: 12,
    color: '#6b7280',
    marginLeft: 4,
  },
});

export default TransactionTimeline;
