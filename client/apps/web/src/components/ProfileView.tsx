import React from 'react';
import ViewHeader from './ViewHeader';

const ProfileView: React.FC = () => {
    return (
        <div className="flex flex-col h-full bg-gray-50">
            <ViewHeader title="Profile" />
             <main className="flex-1 flex flex-col items-center justify-center text-center p-8">
                <div className="p-6 bg-gray-100 rounded-full mb-6">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-800">Coming Soon!</h3>
                <p className="text-gray-500 mt-2 max-w-xs">
                    The Profile section is under construction. You'll soon be able to manage your account settings and preferences here.
                </p>
            </main>
        </div>
    );
};

export default ProfileView;