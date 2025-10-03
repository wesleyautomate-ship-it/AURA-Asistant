import { Transaction, TransactionMilestone, MilestoneType } from '@/types';

export type TimelineSeed = {
  contractSignedDate: string; // ISO date
  inspectionOffsetDays?: number;
  appraisalOffsetDays?: number;
  financingApprovalOffsetDays?: number;
  closingOffsetDays?: number;
  possessionOffsetDays?: number;
};

const addDays = (isoDate: string, days: number) => {
  const d = new Date(isoDate);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
};

export const defaultOffsets = {
  inspectionOffsetDays: 10,
  appraisalOffsetDays: 15,
  financingApprovalOffsetDays: 30,
  closingOffsetDays: 45,
  possessionOffsetDays: 46,
};

export function generateMilestonesFromContract(seed: TimelineSeed): TransactionMilestone[] {
  const s = { ...defaultOffsets, ...seed };

  const milestones: { type: MilestoneType; title: string; description: string; dueDate: string }[] = [
    { type: 'contract_signed', title: 'Contract Signed', description: 'Purchase agreement fully executed', dueDate: s.contractSignedDate },
    { type: 'inspection', title: 'Inspection', description: 'Buyer home inspection period', dueDate: addDays(s.contractSignedDate, s.inspectionOffsetDays) },
    { type: 'appraisal', title: 'Appraisal', description: 'Lender appraisal scheduled/completed', dueDate: addDays(s.contractSignedDate, s.appraisalOffsetDays) },
    { type: 'financing_approved', title: 'Financing Approved', description: 'Final loan/finance approval', dueDate: addDays(s.contractSignedDate, s.financingApprovalOffsetDays) },
    { type: 'closing', title: 'Closing', description: 'Final closing and key handover', dueDate: addDays(s.contractSignedDate, s.closingOffsetDays) },
    { type: 'possession', title: 'Possession', description: 'Buyer takes possession', dueDate: addDays(s.contractSignedDate, s.possessionOffsetDays) },
  ];

  return milestones.map((m, i) => ({
    id: `auto-${i + 1}`,
    ...m,
    completed: false,
  }));
}

export function computeProgress(tx: Transaction): number {
  if (!tx.milestones || tx.milestones.length === 0) return 0;
  const done = tx.milestones.filter(m => m.completed).length;
  return Math.round((done / tx.milestones.length) * 100);
}
