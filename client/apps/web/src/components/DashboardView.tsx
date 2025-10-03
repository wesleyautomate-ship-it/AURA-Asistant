import React from 'react';
import Header from './Header';
import ActionCenter from './ActionCenter';
import RequestCard from './RequestCard';
import { MOCK_REQUESTS } from '../constants';
import { ActionId, Request } from '../types';

interface DashboardViewProps {
    onActionClick: (id: ActionId) => void;
    onRequestClick: (request: Request) => void;
}

const DashboardView: React.FC<DashboardViewProps> = ({ onActionClick, onRequestClick }) => {
    return (
        <div className="flex flex-col h-full bg-gray-50 overflow-y-auto">
            <Header />
            <main className="flex-grow px-4 md:px-6 pb-28">
                <div className="mb-8">
                    <ActionCenter onActionClick={onActionClick} />
                </div>
                
                <div className="mb-8">
                    <div className="flex justify-between items-center mb-3">
                        <div className="flex items-center space-x-2">
                           <h2 className="text-sm font-semibold text-gray-500">AI WORKSPACE</h2>
                           <span className="flex items-center justify-center bg-gray-800 text-white text-xs font-bold w-5 h-5 rounded-full">{MOCK_REQUESTS.length}</span>
                        </div>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>

                    <div className="space-y-3">
                        {MOCK_REQUESTS.map(request => (
                           <RequestCard key={request.id} request={request} onClick={onRequestClick} />
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default DashboardView;