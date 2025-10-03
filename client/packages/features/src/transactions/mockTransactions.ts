export const MOCK_TRANSACTIONS = [
  {
    id: 'tx-1',
    propertyId: 'p-1',
    clientId: 'client-1',
    status: 'in_progress',
    offerAmount: 1800000,
    salePrice: 1850000,
    createdAt: '2025-09-01T10:00:00Z',
    updatedAt: '2025-09-15T14:30:00Z',
    expectedClosingDate: '2025-10-15',
    notes: 'Client is a first-time homebuyer. Pre-approved for 80% financing.',
    agentId: 'agent-1',
    milestones: [
      { id: 'm-1', type: 'offer_submitted', title: 'Offer Submitted', description: 'Initial offer submitted to seller', dueDate: '2025-09-01', completed: true, completedAt: '2025-09-01T15:30:00Z' },
      { id: 'm-2', type: 'offer_accepted', title: 'Offer Accepted', description: 'Seller accepted the offer with counter', dueDate: '2025-09-05', completed: true, completedAt: '2025-09-04T11:20:00Z' },
      { id: 'm-3', type: 'contract_signed', title: 'Contract Signed', description: 'Both parties signed the purchase agreement', dueDate: '2025-09-10', completed: true, completedAt: '2025-09-09T16:45:00Z' },
      { id: 'm-4', type: 'inspection', title: 'Property Inspection', description: 'Schedule and complete property inspection', dueDate: '2025-09-20', completed: false },
      { id: 'm-5', type: 'appraisal', title: 'Appraisal', description: 'Lender appraisal scheduled', dueDate: '2025-09-25', completed: false },
      { id: 'm-6', type: 'financing_approved', title: 'Financing Approved', description: 'Final mortgage approval from bank', dueDate: '2025-10-05', completed: false },
      { id: 'm-7', type: 'closing', title: 'Closing', description: 'Final closing and key handover', dueDate: '2025-10-15', completed: false },
      { id: 'm-8', type: 'possession', title: 'Possession', description: 'Client takes possession of property', dueDate: '2025-10-16', completed: false }
    ],
    documents: [
      { id: 'doc-1', name: 'Purchase Agreement.pdf', type: 'contract', url: '#', uploadedAt: '2025-09-10T14:30:00Z', size: 245678 },
      { id: 'doc-2', name: 'Disclosure Form.pdf', type: 'disclosure', url: '#', uploadedAt: '2025-09-11T10:15:00Z', size: 187654 }
    ]
  },
  {
    id: 'tx-2',
    propertyId: 'p-2',
    clientId: 'client-2',
    status: 'pending_approval',
    offerAmount: 12000000,
    createdAt: '2025-09-10T09:30:00Z',
    updatedAt: '2025-09-12T16:45:00Z',
    expectedClosingDate: '2025-11-30',
    notes: 'Luxury property with custom upgrades. Client is an investor from overseas.',
    agentId: 'agent-1',
    milestones: [
      { id: 'm-21', type: 'offer_submitted', title: 'Offer Submitted', description: 'Initial offer submitted to seller', dueDate: '2025-09-12', completed: true, completedAt: '2025-09-12T11:20:00Z' },
      { id: 'm-22', type: 'offer_accepted', title: 'Offer Accepted', description: 'Waiting for seller response', dueDate: '2025-09-17', completed: false }
    ],
    documents: []
  }
];
