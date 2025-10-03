import React from 'react';
import { TransactionTemplate, MilestoneType } from '@propertypro/features/types';

export type TransactionTemplatesProps = {
  visible: boolean;
  onClose: () => void;
  selectedMilestone?: MilestoneType;
  onSelectTemplate?: (template: TransactionTemplate) => void;
};

const defaults: TransactionTemplate[] = [
  {
    id: 'temp-1',
    name: 'Offer Submitted',
    subject: 'Offer Submitted - {{propertyTitle}}',
    body:
      'Dear {{clientName}},\n\nWe have submitted your offer for {{propertyTitle}} at AED {{offerAmount}}. I will update you as soon as we receive a response.\n\nBest,\n{{agentName}}',
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
      'Hi {{clientName}},\n\nYour inspection for {{propertyTitle}} is scheduled for {{inspectionDate}} at {{inspectionTime}}. I will share the report when ready.\n\nThanks,\n{{agentName}}',
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
      'Dear {{clientName}},\n\nWe are approaching closing for {{propertyTitle}}. Date: {{closingDate}}, Time: {{closingTime}}, Location: {{closingLocation}}. See attached checklist.\n\nRegards,\n{{agentName}}',
    milestoneTypes: ['closing'],
    isDefault: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const TransactionTemplates: React.FC<TransactionTemplatesProps> = ({
  visible,
  onClose,
  selectedMilestone,
  onSelectTemplate,
}) => {
  const list = React.useMemo(() => {
    if (!selectedMilestone) return defaults;
    return defaults.filter((template) => template.milestoneTypes.includes(selectedMilestone));
  }, [selectedMilestone]);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center bg-black/40">
      <div className="bg-white w-full md:max-w-xl md:rounded-xl md:shadow-xl max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Communication Templates</h2>
          <button onClick={onClose} className="text-gray-600 hover:text-gray-900" aria-label="Close template dialog">
            X
          </button>
        </div>

        <div className="p-3 space-y-2 overflow-y-auto" style={{ maxHeight: '70vh' }}>
          {!list.length ? (
            <div className="p-6 text-center text-gray-500">No templates for this milestone</div>
          ) : (
            list.map((template) => (
              <button
                key={template.id}
                onClick={() => onSelectTemplate?.(template)}
                className="w-full text-left p-3 border rounded hover:bg-amber-50"
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium">{template.name}</div>
                  {template.isDefault && (
                    <span className="text-xs rounded px-2 py-0.5 bg-emerald-100 text-emerald-800">Default</span>
                  )}
                </div>
                <div className="text-sm text-gray-600">{template.subject}</div>
                <div className="text-xs text-gray-500 line-clamp-2 whitespace-pre-wrap">{template.body}</div>
              </button>
            ))
          )}
        </div>

        <div className="p-3 border-t flex justify-end">
          <button onClick={onClose} className="px-3 py-1.5 rounded bg-orange-600 text-white text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default TransactionTemplates;
