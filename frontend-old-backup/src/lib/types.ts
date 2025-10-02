import type { ReactNode } from 'react';

export type View = 'dashboard' | 'tasks' | 'chat' | 'profile';

export type ActionId =
  | 'marketing'
  | 'analytics'
  | 'social'
  | 'strategy'
  | 'contacts'
  | 'transactions'
  | 'playwright';

export interface ActionItem {
  id: ActionId;
  title: string;
  subtitle: string;
  accentColor?: string;
  icon?: ReactNode;
}

export interface Request {
  id: number;
  category: 'Marketing' | 'Sync' | 'Campaign' | 'Data Analysis';
  title: string;
  description: string;
  eta: string;
  status: 'Queued' | 'Processing' | 'Ready for Review';
  progress: number;
  assignees: { id: string; avatarUrl?: string }[];
  image?: string;
  tags?: RequestTag[];
}

export interface RequestTag {
  text: string;
  tone?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}

export type Priority = 'Low' | 'Medium' | 'High';

export interface Task {
  id: number;
  title: string;
  dueDate: string;
  priority: Priority;
  isCompleted: boolean;
}
