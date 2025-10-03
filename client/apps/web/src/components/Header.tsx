import React from 'react';

const Header: React.FC = () => {
    return (
        <header className="px-4 md:px-6 pt-8 md:pt-12 pb-4">
            <div className="flex justify-between items-center">
                    {/* App Logo */}
                    <div className="flex items-baseline space-x-1">
                        <h1 className="text-2xl font-bold text-gray-900 tracking-tighter">PropertyPro AI</h1>
                    </div>

                <div className="flex items-center space-x-4">
                     {/* Notification Bell */}
                    <button className="relative p-2 rounded-full text-gray-500 hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V5a1 1 0 00-2 0v.083A6 6 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                        <span className="absolute top-2 right-2 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
                    </button>
                    {/* User Avatar */}
                    <img
                        className="h-10 w-10 rounded-full object-cover"
                        src="https://images.unsplash.com/photo-1557862921-37829c790f19?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                        alt="User profile"
                    />
                </div>
            </div>
        </header>
    );
};

export default Header;
