import React from 'react';

interface FeatureViewProps {
    title: string;
    onBack: () => void;
}

const FeatureView: React.FC<FeatureViewProps> = ({ title, onBack }) => {
    return (
        <div className="flex flex-col h-full bg-gray-50">
            <header className="flex items-center p-4 border-b bg-white">
                <button onClick={onBack} className="p-2 rounded-full hover:bg-gray-100">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                </button>
                <h2 className="text-lg font-bold text-gray-800 ml-4">{title}</h2>
            </header>
            <main className="flex-1 flex flex-col items-center justify-center text-center p-8">
                <div className="p-6 bg-gray-100 rounded-full mb-6">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-800">Coming Soon!</h3>
                <p className="text-gray-500 mt-2 max-w-xs">
                    The "{title}" feature is currently under development. Check back later for exciting new functionality!
                </p>
                <button 
                    onClick={onBack}
                    className="mt-8 bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-blue-700 transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300">
                    Back to Dashboard
                </button>
            </main>
        </div>
    );
};

export default FeatureView;