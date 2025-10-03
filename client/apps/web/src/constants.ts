import { ActionId, Task } from './types';

export const ACTION_ITEMS: { id: ActionId; title: string; icon?: string }[] = [
  { id: 'marketing', title: 'Marketing' },
  { id: 'social', title: 'Social Media' },
  { id: 'contacts', title: 'Contacts' },
  { id: 'playwright', title: 'Playwright' },
  { id: 'properties', title: 'Properties' },
  { id: 'content', title: 'Content' },
  { id: 'analytics', title: 'Analytics' },
];

export const MOCK_TASKS: Task[] = [
  { id: 't-1', title: 'Follow up with Ali Khan', status: 'pending', dueDate: '2025-09-22' },
  { id: 't-2', title: 'Create CMA for Marina apt', status: 'in_progress', dueDate: '2025-09-24' },
  { id: 't-3', title: 'Schedule viewing - Palm villa', status: 'pending', dueDate: '2025-09-23' },
];

export const MOCK_PROPERTIES = [
  {
    id: 'p-1',
    title: '2BR Marina View Apartment',
    price: 'AED 1,850,000',
    area: 'Dubai Marina',
    sizeSqft: 1120,
    beds: 2,
    baths: 2,
    image: undefined as string | undefined,
  },
  {
    id: 'p-2',
    title: 'Palm Jumeirah Garden Villa',
    price: 'AED 12,400,000',
    area: 'Palm Jumeirah',
    sizeSqft: 5200,
    beds: 5,
    baths: 6,
    image: undefined as string | undefined,
  },
  {
    id: 'p-3',
    title: 'Downtown Burj View 1BR',
    price: 'AED 1,450,000',
    area: 'Downtown Dubai',
    sizeSqft: 780,
    beds: 1,
    baths: 1,
    image: undefined as string | undefined,
  },
];
