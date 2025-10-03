import React, { useMemo, useState } from 'react';
import { useClientStore, selectClients } from '../store';
import LeadScoring from './LeadScoring';

interface Contact {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: 'hot' | 'warm' | 'cold' | 'client';
  lastContact: string;
  nextFollowUp: string;
  leadScore: number;
  notes: string;
  tags: string[];
}

interface FollowUpTask {
  id: string;
  contactId: string;
  contactName: string;
  type: 'call' | 'email' | 'text' | 'meeting';
  dueDate: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'completed' | 'overdue';
  description: string;
}

const ContactManagementView: React.FC<{ onBack: () => void; }> = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState<'contacts' | 'followups' | 'analytics'>('contacts');
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [showAddContact, setShowAddContact] = useState(false);

  // Integrate with clientStore
  const storeClients = useClientStore(selectClients);
  const contacts: Contact[] = useMemo(() => storeClients.map(c => ({
    id: String(c.id),
    name: c.name,
    email: c.email || '',
    phone: c.phone || '',
    status: (c.status === 'converted' ? 'client' : (['hot','warm','cold'].includes(c.status as any) ? c.status as any : 'warm')),
    lastContact: c.lastContactedAt || '',
    nextFollowUp: '',
    leadScore: c.leadScore || 0,
    notes: c.notes || '',
    tags: []
  })), [storeClients]);

  // Fallback demo data if store is empty (keeps existing UX during initial load)
  const [demoContacts] = useState<Contact[]>([
    {
      id: '1',
      name: 'Sarah Johnson',
      email: 'sarah.johnson@email.com',
      phone: '(555) 123-4567',
      status: 'hot',
      lastContact: '2024-01-15',
      nextFollowUp: '2024-01-18',
      leadScore: 85,
      notes: 'Looking for 3BR condo in downtown. Budget $800K-1.2M. Very interested in Spanish River property.',
      tags: ['First-time buyer', 'Downtown', 'High budget']
    },
    {
      id: '2',
      name: 'Michael Chen',
      email: 'm.chen@email.com',
      phone: '(555) 987-6543',
      status: 'warm',
      lastContact: '2024-01-10',
      nextFollowUp: '2024-01-20',
      leadScore: 65,
      notes: 'Investment property buyer. Interested in rental properties with good ROI.',
      tags: ['Investor', 'Rental properties', 'ROI focused']
    },
    {
      id: '3',
      name: 'Emily Rodriguez',
      email: 'emily.r@email.com',
      phone: '(555) 456-7890',
      status: 'client',
      lastContact: '2024-01-12',
      nextFollowUp: '2024-01-25',
      leadScore: 95,
      notes: 'Recent client who bought through us. Referral potential. Very satisfied.',
      tags: ['Past client', 'Referral source', 'Satisfied customer']
    }
  ]);

  // Mock data for follow-up tasks
  const [followUpTasks] = useState<FollowUpTask[]>([
    {
      id: '1',
      contactId: '1',
      contactName: 'Sarah Johnson',
      type: 'call',
      dueDate: '2024-01-18',
      priority: 'high',
      status: 'pending',
      description: 'Follow up on Spanish River property showing'
    },
    {
      id: '2',
      contactId: '2',
      contactName: 'Michael Chen',
      type: 'email',
      dueDate: '2024-01-20',
      priority: 'medium',
      status: 'pending',
      description: 'Send investment property analysis report'
    },
    {
      id: '3',
      contactId: '3',
      contactName: 'Emily Rodriguez',
      type: 'text',
      dueDate: '2024-01-25',
      priority: 'low',
      status: 'pending',
      description: 'Check-in and ask for referrals'
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'hot': return 'bg-red-100 text-red-800';
      case 'warm': return 'bg-yellow-100 text-yellow-800';
      case 'cold': return 'bg-blue-100 text-blue-800';
      case 'client': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getLeadScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <header className="flex items-center p-4 border-b bg-white">
        <button onClick={onBack} className="p-2 rounded-full hover:bg-gray-100" aria-label="Go back">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 className="text-lg font-bold text-gray-800 ml-4">Contact Management</h2>
        <div className="ml-auto">
          <button 
            onClick={() => setShowAddContact(true)}
            className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700"
          >
            + Add Contact
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-20">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white p-1 rounded-lg border mb-6">
          <button
            onClick={() => setActiveTab('contacts')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'contacts' 
                ? 'bg-emerald-100 text-emerald-800 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Contacts
          </button>
          <button
            onClick={() => setActiveTab('followups')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'followups' 
                ? 'bg-emerald-100 text-emerald-800 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Follow-ups
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'analytics' 
                ? 'bg-emerald-100 text-emerald-800 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Analytics
          </button>
        </div>

        {/* Contacts Tab */}
        {activeTab === 'contacts' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-800">All Contacts</h3>
              <div className="flex space-x-2">
                <select className="text-sm border border-gray-300 rounded-md px-3 py-1">
                  <option>All Status</option>
                  <option>Hot Leads</option>
                  <option>Warm Leads</option>
                  <option>Cold Leads</option>
                  <option>Clients</option>
                </select>
                <input 
                  type="text" 
                  placeholder="Search contacts..." 
                  className="text-sm border border-gray-300 rounded-md px-3 py-1 w-48"
                />
              </div>
            </div>

            <div className="grid gap-4">
              {(contacts.length ? contacts : demoContacts).map((contact) => (
                <div key={contact.id} className="bg-white rounded-lg border p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-semibold text-gray-800">{contact.name}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(contact.status)}`}>
                          {contact.status.toUpperCase()}
                        </span>
                        <div className="w-40">
                          <LeadScoring score={contact.leadScore} />
                        </div>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>{contact.email}</p>
                        <p>{contact.phone}</p>
                        <p>Last contact: {contact.lastContact}</p>
                        <p>Next follow-up: {contact.nextFollowUp}</p>
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-gray-700">{contact.notes}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {contact.tags.map((tag, index) => (
                            <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Follow-ups Tab */}
        {activeTab === 'followups' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-800">Follow-up Tasks</h3>
              <button className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700">
                + Schedule Follow-up
              </button>
            </div>

            <div className="grid gap-4">
              {followUpTasks.map((task) => (
                <div key={task.id} className="bg-white rounded-lg border p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-semibold text-gray-800">{task.contactName}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                          {task.priority.toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500 capitalize">{task.type}</span>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{task.description}</p>
                      <p className="text-sm text-gray-500">Due: {task.dueDate}</p>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button className="bg-emerald-600 text-white px-3 py-1 rounded text-sm hover:bg-emerald-700">
                        Complete
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-800">Client Retention Analytics</h3>
            
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg border p-4 text-center">
                <div className="text-2xl font-bold text-emerald-600">85%</div>
                <div className="text-sm text-gray-600">Retention Rate</div>
              </div>
              <div className="bg-white rounded-lg border p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">12</div>
                <div className="text-sm text-gray-600">Active Follow-ups</div>
              </div>
              <div className="bg-white rounded-lg border p-4 text-center">
                <div className="text-2xl font-bold text-yellow-600">3.2</div>
                <div className="text-sm text-gray-600">Avg. Response Time (days)</div>
              </div>
              <div className="bg-white rounded-lg border p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">24</div>
                <div className="text-sm text-gray-600">Total Contacts</div>
              </div>
            </div>

            {/* Lead Score Distribution */}
            <div className="bg-white rounded-lg border p-4">
              <h4 className="font-semibold text-gray-800 mb-4">Lead Score Distribution</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Hot Leads (80-100)</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-red-500 h-2 rounded-full" style={{width: '25%'}}></div>
                    </div>
                    <span className="text-sm font-medium">6</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Warm Leads (60-79)</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-500 h-2 rounded-full" style={{width: '50%'}}></div>
                    </div>
                    <span className="text-sm font-medium">12</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Cold Leads (0-59)</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{width: '25%'}}></div>
                    </div>
                    <span className="text-sm font-medium">6</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Follow-up Performance */}
            <div className="bg-white rounded-lg border p-4">
              <h4 className="font-semibold text-gray-800 mb-4">Follow-up Performance</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">On-time Follow-ups</span>
                  <span className="text-sm font-medium text-green-600">78%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Response Rate</span>
                  <span className="text-sm font-medium text-blue-600">65%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Conversion Rate</span>
                  <span className="text-sm font-medium text-purple-600">23%</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default ContactManagementView;
