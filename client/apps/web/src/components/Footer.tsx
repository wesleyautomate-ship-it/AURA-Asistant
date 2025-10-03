
import React from 'react';

const Footer: React.FC = () => {
    return (
        <footer className="p-6 border-t border-gray-200 mt-auto">
            <div className="flex flex-col items-center">
                <button className="w-full bg-blue-600 text-white font-bold py-4 px-6 rounded-xl shadow-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300">
                    Get Started
                </button>
                <p className="mt-3 text-sm text-gray-500">You have <span className="font-semibold text-gray-700">3 things</span> waiting</p>
            </div>
        </footer>
    );
};

export default Footer;
