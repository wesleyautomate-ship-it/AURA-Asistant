import React from 'react';

export type View = 'dashboard' | 'tasks' | 'chat' | 'profile' | 'properties';

export interface ActionItem {
    id: 'marketing' | 'analytics' | 'social' | 'strategy' | 'contacts' | 'transactions' | 'playwright' | 'packages';
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
    id: number;
    title: string;
    dueDate: string;
    priority: Priority;
    isCompleted: boolean;
}

// Transaction system types
export type TransactionStatus = 'draft' | 'in_progress' | 'pending_approval' | 'completed' | 'cancelled';

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
    dueDate: string; // ISO date
    completed: boolean;
    completedAt?: string; // ISO datetime
    documents?: string[]; // document ids
}

export interface TransactionDocument {
    id: string;
    name: string;
    type: string; // mime or category
    url: string;
    uploadedAt: string; // ISO datetime
    size: number; // bytes
}

export interface Transaction {
    id: string;
    propertyId: string;
    clientId: string;
    status: TransactionStatus;
    offerAmount: number;
    salePrice?: number;
    createdAt: string; // ISO datetime
    updatedAt: string; // ISO datetime
    milestones: TransactionMilestone[];
    documents: TransactionDocument[];
    notes: string;
    agentId: string;
    expectedClosingDate: string; // ISO date
    actualClosingDate?: string; // ISO date
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