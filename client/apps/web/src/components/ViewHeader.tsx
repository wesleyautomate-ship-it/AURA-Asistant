import React from 'react';

interface ViewHeaderProps {
    title: string;
    actions?: React.ReactNode;
}

const ViewHeader: React.FC<ViewHeaderProps> = ({ title, actions }) => {
    return (
        <header className="px-4 md:px-6 pt-8 md:pt-12 pb-4 border-b border-gray-200 bg-white">
            <div className="flex items-center justify-between">
                <h1 className="text-xl font-bold text-gray-900">{title}</h1>
                <div className="flex items-center space-x-4">
                    {actions}
                    <button>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </button>
                    <button>
                         <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                        </svg>
                    </button>
                </div>
            </div>
        </header>
    );
};

export default ViewHeader;