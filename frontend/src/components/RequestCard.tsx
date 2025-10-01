import React from 'react';
import { Request } from '../types';

interface RequestCardProps {
    request: Request;
    onClick?: (request: Request) => void;
}

const CategoryTag: React.FC<{ category: string }> = ({ category }) => {
    const colors: { [key: string]: string } = {
        'Marketing': 'bg-rose-100 text-rose-800',
        'Data Analysis': 'bg-indigo-100 text-indigo-800',
        'Sync': 'bg-blue-100 text-blue-800',
        'Campaign': 'bg-amber-100 text-amber-800',
    };
    return (
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${colors[category] || 'bg-gray-100 text-gray-800'}`}>
            {category}
        </span>
    );
};

const AIAvatar: React.FC = () => {
    return (
        <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center text-white ring-2 ring-white">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2z" /></svg>
            </div>
            <span className="text-xs font-semibold text-gray-500">PropertyPro AI</span>
        </div>
    );
};

const ProgressBar: React.FC<{ progress: number }> = ({ progress }) => (
    <div className="w-full bg-gray-200 rounded-full h-1.5" aria-label={`Progress: ${progress}%`}>
        <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: `${progress}%` }}></div>
    </div>
);

const RequestCard: React.FC<RequestCardProps> = ({ request, onClick }) => {
    const cardContent = (
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-lg focus-within:shadow-lg focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 transition-all duration-300 flex space-x-4 w-full">
            {request.image && (
                <div className="w-24 h-24 flex-shrink-0">
                    <img src={request.image} alt={request.title} className="w-full h-full object-cover rounded-lg" />
                </div>
            )}
            <div className="flex-grow flex flex-col justify-between min-w-0">
                <div>
                    <div className="flex items-center justify-between mb-1">
                        <CategoryTag category={request.category} />
                        <span className="text-xs font-medium text-gray-500">{request.eta}</span>
                    </div>
                    <h3 className="text-sm font-bold text-gray-800 leading-tight mb-2 truncate">{request.title}</h3>
                </div>
                <div className="mt-auto">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-gray-600">{request.status}</span>
                        <span className="text-xs font-semibold text-blue-600">{request.progress}%</span>
                    </div>
                    <ProgressBar progress={request.progress} />
                    <div className="flex items-center justify-between mt-3">
                        <AIAvatar />
                         <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" /></svg>
                    </div>
                </div>
            </div>
        </div>
    );

    if (onClick) {
        return (
            <button 
                onClick={() => onClick(request)} 
                className="w-full text-left rounded-xl focus:outline-none"
                aria-label={`View details for ${request.title}`}
            >
                {cardContent}
            </button>
        );
    }

    return <div className="w-full">{cardContent}</div>;
};

export default RequestCard;
