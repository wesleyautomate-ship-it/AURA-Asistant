import React, { useState, useEffect, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  FlatList,
  Modal,
  ScrollView,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

import { TransactionTemplate, MilestoneType } from '@propertypro/features/types';

export type TransactionTemplatesProps = {
  visible: boolean;
  selectedMilestone?: MilestoneType;
  onSelectTemplate?: (template: TransactionTemplate) => void;
  onClose?: () => void;
};

const defaultTemplates: TransactionTemplate[] = [
  {
    id: 'temp-1',
    name: 'Offer Submitted',
    subject: 'Offer Submitted - {{propertyTitle}}',
    body:
      'Dear {{clientName}},\n\nWe have submitted your offer for {{propertyTitle}} in the amount of AED {{offerAmount}}. I will notify you as soon as we receive a response.\n\nBest regards,\n{{agentName}}',
    milestoneTypes: ['offer_submitted'],
    isDefault: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'temp-2',
    name: 'Inspection Scheduled',
    subject: 'Inspection Scheduled - {{propertyTitle}}',
    body:
      'Hi {{clientName}},\n\nYour inspection for {{propertyTitle}} is scheduled for {{inspectionDate}} at {{inspectionTime}}. Let me know if you would like to attend.\n\nThanks,\n{{agentName}}',
    milestoneTypes: ['inspection'],
    isDefault: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'temp-3',
    name: 'Closing Instructions',
    subject: 'Closing Instructions - {{propertyTitle}}',
    body:
      'Dear {{clientName}},\n\nWe are approaching the closing date for {{propertyTitle}}. Date: {{closingDate}}, Time: {{closingTime}}, Location: {{closingLocation}}. Please review the attached checklist.\n\nRegards,\n{{agentName}}',
    milestoneTypes: ['closing'],
    isDefault: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const milestoneOptions: MilestoneType[] = [
  'offer_submitted',
  'offer_accepted',
  'contract_signed',
  'inspection',
  'appraisal',
  'financing_approved',
  'closing',
  'possession',
];

const formatMilestone = (milestone: MilestoneType) =>
  milestone
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

const TransactionTemplates: React.FC<TransactionTemplatesProps> = ({
  visible,
  selectedMilestone,
  onSelectTemplate,
  onClose,
}) => {
  const [templates, setTemplates] = useState<TransactionTemplate[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [newTemplate, setNewTemplate] = useState<Partial<TransactionTemplate>>({
    name: '',
    subject: '',
    body: '',
    milestoneTypes: selectedMilestone ? [selectedMilestone] : [],
  });

  useEffect(() => {
    setTemplates(defaultTemplates);
  }, []);

  useEffect(() => {
    if (selectedMilestone) {
      setNewTemplate((prev) => ({ ...prev, milestoneTypes: [selectedMilestone] }));
    }
  }, [selectedMilestone]);

  const filteredTemplates = useMemo(() => {
    return templates.filter((template) => {
      const matchesSearch =
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.subject.toLowerCase().includes(searchQuery.toLowerCase());

      if (selectedMilestone) {
        return matchesSearch && template.milestoneTypes.includes(selectedMilestone);
      }

      return matchesSearch;
    });
  }, [templates, searchQuery, selectedMilestone]);

  const handleCreateTemplate = () => {
    if (!newTemplate.name || !newTemplate.subject || !newTemplate.body) {
      alert('Please fill in all fields');
      return;
    }

    const template: TransactionTemplate = {
      id: `temp-${Date.now()}`,
      name: newTemplate.name,
      subject: newTemplate.subject,
      body: newTemplate.body,
      milestoneTypes: newTemplate.milestoneTypes || [],
      isDefault: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    } as TransactionTemplate;

    setTemplates([...templates, template]);
    setNewTemplate({
      name: '',
      subject: '',
      body: '',
      milestoneTypes: selectedMilestone ? [selectedMilestone] : [],
    });
    setIsCreating(false);
  };

  const renderTemplateItem = ({ item }: { item: TransactionTemplate }) => (
    <TouchableOpacity style={styles.templateItem} onPress={() => onSelectTemplate?.(item)}>
      <View style={styles.templateHeader}>
        <Text style={styles.templateName}>{item.name}</Text>
        {item.isDefault && (
          <View style={styles.defaultBadge}>
            <Text style={styles.defaultBadgeText}>Default</Text>
          </View>
        )}
      </View>
      <Text style={styles.templateSubject} numberOfLines={1}>
        {item.subject}
      </Text>
      <Text style={styles.templateSnippet} numberOfLines={2}>
        {item.body.split('\n')[0]}
      </Text>
      <View style={styles.templateFooter}>
        <View style={styles.milestoneTags}>
          {item.milestoneTypes.map((type) => (
            <View key={type} style={styles.milestoneTag}>
              <Text style={styles.milestoneTagText}>{formatMilestone(type)}</Text>
            </View>
          ))}
        </View>
        <MaterialIcons name="chevron-right" size={20} color="#9ca3af" />
      </View>
    </TouchableOpacity>
  );

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <MaterialIcons name="close" size={24} color="#6b7280" />
          </TouchableOpacity>
          <Text style={styles.title}>Communication Templates</Text>
          <TouchableOpacity style={styles.createButton} onPress={() => setIsCreating(true)}>
            <MaterialIcons name="add" size={20} color="#fff" />
          </TouchableOpacity>
        </View>

        {!isCreating ? (
          <>
            <View style={styles.searchContainer}>
              <MaterialIcons name="search" size={20} color="#9ca3af" style={styles.searchIcon} />
              <TextInput
                style={styles.searchInput}
                placeholder="Search templates..."
                value={searchQuery}
                onChangeText={setSearchQuery}
                placeholderTextColor="#9ca3af"
              />
            </View>

            <FlatList
              data={filteredTemplates}
              renderItem={renderTemplateItem}
              keyExtractor={(item) => item.id}
              contentContainerStyle={styles.templatesList}
              ListEmptyComponent={
                <View style={styles.emptyState}>
                  <MaterialIcons name="description" size={48} color="#d1d5db" />
                  <Text style={styles.emptyStateText}>No templates found</Text>
                  <Text style={styles.emptyStateSubtext}>
                    {selectedMilestone
                      ? `No templates for ${formatMilestone(selectedMilestone)}`
                      : 'Create a new template to get started'}
                  </Text>
                </View>
              }
            />
          </>
        ) : (
          <ScrollView style={styles.formContainer}>
            <Text style={styles.formTitle}>New Template</Text>

            <View style={styles.formGroup}>
              <Text style={styles.label}>Template Name</Text>
              <TextInput
                style={styles.input}
                placeholder="e.g., Offer Submitted"
                value={newTemplate.name}
                onChangeText={(text) => setNewTemplate({ ...newTemplate, name: text })}
              />
            </View>

            <View style={styles.formGroup}>
              <Text style={styles.label}>Email Subject</Text>
              <TextInput
                style={styles.input}
                placeholder="e.g., Offer Submitted - {{propertyTitle}}"
                value={newTemplate.subject}
                onChangeText={(text) => setNewTemplate({ ...newTemplate, subject: text })}
              />
            </View>

            <View style={styles.formGroup}>
              <Text style={styles.label}>Email Body</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                placeholder="Write your email template here..."
                value={newTemplate.body}
                onChangeText={(text) => setNewTemplate({ ...newTemplate, body: text })}
                multiline
                numberOfLines={8}
              />
              <Text style={styles.variablesHint}>
                Use {{variable}} syntax for dynamic content (e.g., {{clientName}}, {{propertyTitle}})
              </Text>
            </View>

            <View style={styles.formGroup}>
              <Text style={styles.label}>Applicable Milestones</Text>
              <View style={styles.milestoneOptions}>
                {milestoneOptions.map((milestone) => {
                  const selected = newTemplate.milestoneTypes?.includes(milestone);
                  return (
                    <TouchableOpacity
                      key={milestone}
                      style={[styles.milestoneOption, selected && styles.milestoneOptionSelected]}
                      onPress={() => {
                        const types = new Set(newTemplate.milestoneTypes || []);
                        if (selected) {
                          types.delete(milestone);
                        } else {
                          types.add(milestone);
                        }
                        setNewTemplate({ ...newTemplate, milestoneTypes: Array.from(types) });
                      }}
                    >
                      <Text
                        style={[styles.milestoneOptionText, selected && styles.milestoneOptionTextSelected]}
                      >
                        {formatMilestone(milestone)}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>

            <View style={styles.formActions}>
              <TouchableOpacity style={[styles.button, styles.cancelButton]} onPress={() => setIsCreating(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.button, styles.saveButton]} onPress={handleCreateTemplate}>
                <Text style={styles.saveButtonText}>Save Template</Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        )}
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  closeButton: {
    padding: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  createButton: {
    backgroundColor: '#ea580c',
    borderRadius: 20,
    padding: 6,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: 16,
    borderRadius: 12,
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 12,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 40,
    color: '#111827',
  },
  templatesList: {
    paddingHorizontal: 16,
    paddingBottom: 24,
  },
  templateItem: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#f3f4f6',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  templateHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  templateName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  defaultBadge: {
    backgroundColor: '#dcfce7',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  defaultBadgeText: {
    fontSize: 10,
    color: '#166534',
    fontWeight: '600',
  },
  templateSubject: {
    fontSize: 14,
    color: '#4b5563',
    marginBottom: 4,
  },
  templateSnippet: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 8,
  },
  templateFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  milestoneTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    flex: 1,
  },
  milestoneTag: {
    backgroundColor: '#f3f4f6',
    borderRadius: 4,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginRight: 6,
    marginBottom: 4,
  },
  milestoneTagText: {
    fontSize: 10,
    color: '#4b5563',
    fontWeight: '500',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500',
    marginTop: 16,
    marginBottom: 4,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#9ca3af',
    textAlign: 'center',
  },
  formContainer: {
    flex: 1,
    padding: 16,
  },
  formTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 24,
  },
  formGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#111827',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  textArea: {
    minHeight: 120,
  },
  variablesHint: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
    fontStyle: 'italic',
  },
  milestoneOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  milestoneOption: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#f3f4f6',
    marginRight: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  milestoneOptionSelected: {
    backgroundColor: '#ffedd5',
    borderColor: '#ea580c',
  },
  milestoneOptionText: {
    fontSize: 12,
    color: '#4b5563',
    fontWeight: '500',
  },
  milestoneOptionTextSelected: {
    color: '#9a3412',
  },
  formActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 24,
  },
  button: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 6,
    marginLeft: 12,
    minWidth: 100,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#f3f4f6',
  },
  saveButton: {
    backgroundColor: '#ea580c',
  },
  cancelButtonText: {
    color: '#4b5563',
    fontWeight: '500',
  },
  saveButtonText: {
    color: '#fff',
    fontWeight: '500',
  },
});

export default TransactionTemplates;
