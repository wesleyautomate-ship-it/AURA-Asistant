import React from 'react';
import { TransactionMilestone } from '@propertypro/features/types';

export type TransactionTimelineProps = {
  milestones: TransactionMilestone[];
  onMilestoneClick?: (milestone: TransactionMilestone) => void;
};

const iconFor = (type: TransactionMilestone['type']) => {
  switch (type) {
    case 'offer_submitted':
      return 'OS';
    case 'offer_accepted':
      return 'OA';
    case 'contract_signed':
      return 'CS';
    case 'inspection':
      return 'IN';
    case 'appraisal':
      return 'AP';
    case 'financing_approved':
      return 'FA';
    case 'closing':
      return 'CL';
    case 'possession':
      return 'PO';
    default:
      return '--';
  }
};

const TransactionTimeline: React.FC<TransactionTimelineProps> = ({ milestones, onMilestoneClick }) => {
  const sorted = [...milestones].sort((a, b) => a.dueDate.localeCompare(b.dueDate));

  return (
    <ol className="relative border-s border-gray-200">
      {sorted.map((milestone) => (
        <li key={milestone.id} className="mb-6 ms-6">
          <span
            className={`absolute -start-3 flex h-6 w-6 items-center justify-center rounded-full ring-4 ring-white ${
              milestone.completed ? 'bg-orange-600 text-white' : 'bg-white border border-gray-300'
            }`}
          >
            <span className="text-xs font-semibold" aria-hidden>
              {iconFor(milestone.type)}
            </span>
          </span>
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-gray-900">{milestone.title}</h3>
            <span className="text-xs text-gray-500">{new Date(milestone.dueDate).toLocaleDateString()}</span>
          </div>
          <p className="text-sm text-gray-600 mt-1">{milestone.description}</p>
          {milestone.completed && milestone.completedAt && (
            <div className="mt-1 text-xs text-emerald-700">
              Completed on {new Date(milestone.completedAt).toLocaleDateString()}
            </div>
          )}
          {!!milestone.documents?.length && (
            <div className="mt-2 text-xs text-gray-500">
              {milestone.documents.length} document{milestone.documents.length > 1 ? 's' : ''} attached
            </div>
          )}
          {onMilestoneClick && (
            <button className="mt-2 text-sm text-orange-700 hover:underline" onClick={() => onMilestoneClick(milestone)}>
              View actions
            </button>
          )}
        </li>
      ))}
    </ol>
  );
};

export default TransactionTimeline;
