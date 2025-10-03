import React from 'react';
import ViewHeader from './ViewHeader';
import RequestCard from './RequestCard';
import { MOCK_REQUESTS } from '../constants';

const RequestsView: React.FC = () => {
    return (
        <div className="flex flex-col h-full bg-gray-50">
            <ViewHeader title="All Requests" />
             <main className="flex-1 overflow-y-auto px-6 pt-4 pb-28">
                <div className="space-y-4">
                    {MOCK_REQUESTS.map(request => (
                        <RequestCard key={request.id} request={request} />
                    ))}
                     {[...MOCK_REQUESTS].reverse().map(request => (
                        <RequestCard key={request.id + 10} request={{...request, id: request.id + 10}} />
                    ))}
                </div>
            </main>
        </div>
    );
};

export default RequestsView;