import React from 'react';
import { TransactionMilestone } from '@/types';

type Props = {
  milestones: TransactionMilestone[];
  onToggleComplete?: (id: string, completed: boolean) => void;
};

const MilestoneTracker: React.FC<Props> = ({ milestones, onToggleComplete }) => {
  const sorted = [...milestones].sort((a,b)=>a.dueDate.localeCompare(b.dueDate));

  return (
    <div className="overflow-x-auto border rounded">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 text-gray-600">
          <tr>
            <th className="px-3 py-2 text-left">Done</th>
            <th className="px-3 py-2 text-left">Milestone</th>
            <th className="px-3 py-2 text-left">Due</th>
            <th className="px-3 py-2 text-left">Completed</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map(m => (
            <tr key={m.id} className="border-t">
              <td className="px-3 py-2 align-top">
                <input
                  type="checkbox"
                  checked={m.completed}
                  onChange={(e)=>onToggleComplete?.(m.id, e.target.checked)}
                />
              </td>
              <td className="px-3 py-2">
                <div className="font-medium text-gray-900">{m.title}</div>
                <div className="text-gray-500">{m.description}</div>
              </td>
              <td className="px-3 py-2 text-gray-700">{new Date(m.dueDate).toLocaleDateString()}</td>
              <td className="px-3 py-2 text-gray-700">{m.completedAt ? new Date(m.completedAt).toLocaleDateString() : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MilestoneTracker;
