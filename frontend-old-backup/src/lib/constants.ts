import type { ActionItem, Request, Task } from './types';

export const ACTION_ITEMS: ActionItem[] = [
  {
    id: 'marketing',
    title: 'Marketing',
    subtitle: 'Reach the right audience',
    accentColor: '#2563EB',
  },
  {
    id: 'analytics',
    title: 'Analytics',
    subtitle: 'Track performance',
    accentColor: '#7C3AED',
  },
  {
    id: 'social',
    title: 'Social Media',
    subtitle: 'Amplify your presence',
    accentColor: '#059669',
  },
  {
    id: 'strategy',
    title: 'Strategy',
    subtitle: 'Plan for success',
    accentColor: '#F59E0B',
  },
  {
    id: 'contacts',
    title: 'Contacts',
    subtitle: 'Delight your clients',
    accentColor: '#10B981',
  },
  {
    id: 'transactions',
    title: 'Transactions',
    subtitle: 'Manage workflow',
    accentColor: '#1D4ED8',
  },
  {
    id: 'playwright',
    title: 'UI Testing',
    subtitle: 'Validate experiences',
    accentColor: '#DC2626',
  },
];

export const MOCK_REQUESTS: Request[] = [
  {
    id: 1,
    category: 'Marketing',
    title: 'Generate listing campaign for 1801 Spanish River Road',
    description:
      'Create a listing description, social media posts, and email blast for the Spanish River property. Price: $11,995,000.',
    eta: '~10 min',
    status: 'Processing',
    progress: 75,
    assignees: [{ id: 'ai' }],
    image: 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=400&q=80',
    tags: [{ text: 'Luxury', tone: 'info' }],
  },
  {
    id: 2,
    category: 'Data Analysis',
    title: 'Prep CMA for 548 West 22nd St.',
    description: 'Compile pricing strategies and listing presentation draft for the upcoming appointment.',
    eta: '~15 min',
    status: 'Queued',
    progress: 10,
    assignees: [{ id: 'ai' }],
    image: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=400&q=80',
    tags: [{ text: 'Hot Prospect', tone: 'warning' }],
  },
];

export const MOCK_TASKS: Task[] = [
  {
    id: 1,
    title: 'Follow up with the Smiths about 123 Main St.',
    dueDate: '2025-09-26',
    priority: 'High',
    isCompleted: false,
  },
  {
    id: 2,
    title: 'Prepare CMA for 548 West 22nd St.',
    dueDate: '2025-09-27',
    priority: 'Medium',
    isCompleted: false,
  },
  {
    id: 3,
    title: 'Schedule staging photos for Spanish River property',
    dueDate: '2025-09-21',
    priority: 'Medium',
    isCompleted: true,
  },
  {
    id: 4,
    title: 'Update client database with new leads',
    dueDate: '2025-10-01',
    priority: 'Low',
    isCompleted: false,
  },
];
