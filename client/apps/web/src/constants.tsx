import React from 'react';
import { ActionItem, Request, Task } from './types';

const MarketingIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.136a1.76 1.76 0 011.171-2.287l5.42-1.935a1.76 1.76 0 012.287 1.171l.636 1.791M11 5.882L15 4.5l4.5 1.5-1.5 4.5-1.5-1-1.5 1-1.5-1-1.5 1-1.5-1z" /></svg>;
const AnalyticsIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>;
const SocialIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-amber-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>;
const StrategyIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-teal-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>;
const ContactManagementIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-emerald-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>;
const TransactionsIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-fuchsia-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" /></svg>;
const PlaywrightIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-orange-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" /></svg>;
const PackagesIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-teal-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M3 7l9-4 9 4-9 4-9-4zm0 6l9 4 9-4M3 7v6m18-6v6" /></svg>;

export const ACTION_ITEMS: ActionItem[] = [
    { id: 'marketing', title: 'Marketing', subtitle: 'Reach the Right Audience', color: 'bg-red-100', icon: <MarketingIcon /> },
    { id: 'analytics', title: 'Data & Analytics', subtitle: 'Make Informed Decisions', color: 'bg-indigo-100', icon: <AnalyticsIcon /> },
    { id: 'social', title: 'Social Media', subtitle: 'Amplify Your Presence', color: 'bg-amber-100', icon: <SocialIcon /> },
    { id: 'strategy', title: 'Strategy', subtitle: 'Plan for Success', color: 'bg-teal-100', icon: <StrategyIcon /> },
    { id: 'packages', title: 'Packages', subtitle: 'Automate Multi-Step Work', color: 'bg-teal-100', icon: <PackagesIcon /> },
    { id: 'contacts', title: 'Contact Management', subtitle: 'Optimize Client Retention', color: 'bg-emerald-100', icon: <ContactManagementIcon /> },
    { id: 'transactions', title: 'Transactions', subtitle: 'Manage workflow', color: 'bg-fuchsia-100', icon: <TransactionsIcon /> },
    { id: 'playwright', title: 'UI/UX Testing', subtitle: 'Test & Validate Interface', color: 'bg-orange-100', icon: <PlaywrightIcon /> },
];

export const MOCK_REQUESTS: Request[] = [
    {
        id: 1,
        category: 'Marketing',
        title: 'Generate Listing Campaign for 1801 Spanish River Road',
        description: "Generate a compelling listing description, social media posts (Instagram, Facebook), and an email blast announcement. Price: $11,995,000.",
        eta: '~10 min',
        status: 'Processing',
        progress: 75,
        assignees: [{id: 'ai'}],
        image: 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=400&q=80',
    },
    {
        id: 2,
        category: 'Data Analysis',
        title: 'Prep for Listing Appointment at 548 West 22nd St.',
        description: "Compile a full CMA with two pricing strategies (aggressive, standard) and generate a listing presentation draft.",
        eta: '~15 min',
        status: 'Queued',
        progress: 10,
        assignees: [{id: 'ai'}],
        image: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=400&q=80',
        tags: [{ text: 'Hot Prospect', color: 'bg-orange-100 text-orange-800' }]
    }
];

export const MOCK_TASKS: Task[] = [
    {
        id: 1,
        title: 'Follow up with the Smiths about 123 Main St.',
        dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Due in 2 days
        priority: 'High',
        isCompleted: false,
    },
    {
        id: 2,
        title: 'Prepare CMA for 548 West 22nd St.',
        dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Due in 3 days
        priority: 'Medium',
        isCompleted: false,
    },
    {
        id: 3,
        title: 'Schedule staging photos for Spanish River property',
        dueDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Due yesterday
        priority: 'Medium',
        isCompleted: true,
    },
    {
        id: 4,
        title: 'Update client database with new leads',
        dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Due in 1 week
        priority: 'Low',
        isCompleted: false,
    },
];

// Transactions mock data (used by TransactionsView)
export { MOCK_TRANSACTIONS } from '@propertypro/features';
