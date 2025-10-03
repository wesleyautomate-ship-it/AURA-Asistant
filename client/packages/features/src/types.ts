import React from 'react';

export type View =
  | 'dashboard'
  | 'tasks'
  | 'chat'
  | 'profile'
  | 'properties'
  | 'content'
  | 'analytics'
  | 'workflows'
  | 'transactions';

export interface ActionItem {
  id:
    | 'marketing'
    | 'analytics'
    | 'social'
    | 'strategy'
    | 'contacts'
    | 'transactions'
    | 'playwright'
    | 'packages'
    | 'workflows'
    | 'content'
    | 'properties';
  title: string;
  subtitle: string;
  color: string;
  icon: React.ReactNode;
}

export type ActionId = ActionItem['id'];

export type CommandRequest =
  | {
      kind: 'text';
      prompt: string;
      quickAction?: string | null;
    }
  | {
      kind: 'audio';
      transcript: string;
      mimeType: string;
      duration: number;
      audioBlob: Blob;
    };

export interface ChatMessage {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  suggestions?: string[];
  format?: 'plain' | 'markdown';
  actions?: { label: string; prompt: string }[];
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
  tags?: { text: string; color: string }[];
}

export type Priority = 'Low' | 'Medium' | 'High';

export interface Task {
  id: string | number;
  title: string;
  dueDate?: string;
  priority?: Priority;
  isCompleted?: boolean;
  status?: 'pending' | 'in_progress' | 'completed';
}

export type TransactionStatus =
  | 'draft'
  | 'in_progress'
  | 'pending_approval'
  | 'completed'
  | 'cancelled';

export type MilestoneType =
  | 'offer_submitted'
  | 'offer_accepted'
  | 'contract_signed'
  | 'inspection'
  | 'appraisal'
  | 'financing_approved'
  | 'closing'
  | 'possession';

export interface TransactionMilestone {
  id: string;
  type: MilestoneType;
  title: string;
  description: string;
  dueDate: string;
  completed: boolean;
  completedAt?: string;
  documents?: string[];
}

export interface TransactionDocument {
  id: string;
  name: string;
  type: string;
  url: string;
  uploadedAt: string;
  size: number;
}

export interface Transaction {
  id: string;
  propertyId: string;
  clientId: string;
  status: TransactionStatus;
  offerAmount: number;
  salePrice?: number;
  createdAt: string;
  updatedAt: string;
  milestones: TransactionMilestone[];
  documents: TransactionDocument[];
  notes: string;
  agentId: string;
  expectedClosingDate: string;
  actualClosingDate?: string;
}

export interface TransactionTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  milestoneTypes: MilestoneType[];
  isDefault: boolean;
  createdAt: string;
  updatedAt: string;
}

export type Milestone = TransactionMilestone;
export type Document = TransactionDocument;

export type AIProvider = 'openai' | 'gemini';

export interface AIContentRequest {
  prompt: string;
  contentType?: 'description' | 'social' | 'email' | 'brochure';
  tone?: 'professional' | 'casual' | 'luxury' | 'friendly';
}

export interface AIContentResponse {
  content: string;
  contentType: 'description' | 'social' | 'email' | 'brochure';
  tone?: 'professional' | 'casual' | 'luxury' | 'friendly';
  wordCount?: number;
  suggestions?: string[];
}
