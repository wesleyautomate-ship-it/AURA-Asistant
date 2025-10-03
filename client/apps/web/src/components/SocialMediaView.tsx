import React, { useState, useMemo } from 'react';
import SocialTemplates, { type SocialTemplate } from './SocialTemplates';
import PostScheduler from './PostScheduler';
import PlatformConnections from './PlatformConnections';
import SocialCampaigns from './SocialCampaigns';
import { socialMediaApi } from '../services/socialMediaApi';
import { usePropertyStore } from '../store/propertyStore';

// Array of social media categories for the UI
const socialCategories = [
    { id: 'just-listed', title: 'Just Listed', icon: '🏠' },
    { id: 'open-house', title: 'Open House', icon: '🚪' },
    { id: 'just-sold', title: 'Just Sold', icon: 'SOLD' },
    { id: 'feature-post', title: 'Feature Post', icon: '✨' },
    { id: 'presenting', title: 'Presenting', icon: '🤝' },
    { id: 'no-contract', title: 'No Contract', icon: '✍️' },
];

// Pre-defined heights for a simulated audio waveform visual
const waveformHeights = [10, 20, 35, 50, 30, 15, 40, 45, 55, 60, 50, 40, 30, 20, 15, 25, 35, 45, 50, 40, 30, 20, 10, 15, 25, 35, 40, 30, 20, 10];

// Define the structure for a generated social media post
interface GeneratedPost {
    image: string;
    caption: string;
}

const SocialMediaView: React.FC<{ onBack: () => void; }> = ({ onBack }) => {
    // State management for the component
    const [selectedCategory, setSelectedCategory] = useState<string>('just-listed');
    const [instructions, setInstructions] = useState('A modern 2-story house in the suburbs with a pool.');
    const [activeTab, setActiveTab] = useState<'audio' | 'text'>('text');
    const [isLoading, setIsLoading] = useState(false);
    const [generatedPost, setGeneratedPost] = useState<GeneratedPost | null>(null);
    const brandPurple = '#7c3aed';
    const [selectedTemplate, setSelectedTemplate] = useState<SocialTemplate | null>(null);

    // Auto-populate from property store (Beta-1)
    const propertyStore = usePropertyStore();
    const property = useMemo(() => {
        const items: any[] = (propertyStore as any)?.items || [];
        return Array.isArray(items) && items.length > 0 ? items[0] : null;
    }, [propertyStore]);

    const defaultCaption = useMemo(() => {
        const addr = property?.address || 'a great property';
        switch (selectedCategory) {
            case 'just-listed':
                return `Just Listed! ${addr} ${property?.beds ? `· ${property.beds} bed` : ''} ${property?.baths ? `· ${property.baths} bath` : ''} ${property?.sqft ? `· ${property.sqft.toLocaleString()} sqft` : ''}`.trim();
            case 'open-house':
                return `Open House at ${addr} — Join us this weekend!`;
            case 'just-sold':
                return `Just Sold! ${addr} — Congratulations to our clients!`;
            default:
                return instructions;
        }
    }, [selectedCategory, property, instructions]);

    const defaultImageUrl = useMemo(() => {
        return property?.imageUrl || 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=1200&q=80';
    }, [property]);

    const handlePostNow = async (payload: { caption: string; imageUrl?: string; platforms: ('facebook' | 'instagram' | 'linkedin')[] }) => {
        await socialMediaApi.postNow(payload);
        // Optionally show a toast in future
    };

    const handleSchedule = async (payload: { caption: string; imageUrl?: string; platforms: ('facebook' | 'instagram' | 'linkedin')[]; scheduledAt: string }) => {
        await socialMediaApi.schedule(payload);
    };

    // Simulate generating a social media post
    const handleGenerate = () => {
        setIsLoading(true);
        setGeneratedPost(null);
        // Simulate a network request
        setTimeout(() => {
            setGeneratedPost({
                image: 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=870&q=80',
                caption: `Just Listed! ✨ A stunning modern 2-story house in the suburbs complete with a beautiful pool. Perfect for summer entertaining! This is a UI/UX demonstration of AI-generated content. #realestate #justlisted #dreamhome #suburbs #poolhouse`,
            });
            setIsLoading(false);
        }, 2000);
    };

    return (
        <div className="flex flex-col h-full bg-gray-50">
            {/* Header */}
            <header className="flex items-center p-4 border-b bg-white flex-shrink-0">
                <button onClick={onBack} className="p-2 rounded-full hover:bg-gray-100" aria-label="Go back">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                </button>
                <h2 className="text-lg font-bold text-gray-800 ml-4">AI Social Media Assistant</h2>
            </header>

            {/* Main Content Area */}
            <main className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 pb-20">
                {/* Step 1: Category Selection */}
                <div>
                    <h3 className="text-base font-semibold text-gray-800 mb-3">1. Select a Category</h3>
                    <div className="flex space-x-2 overflow-x-auto pb-2 -mx-4 px-4">
                        {socialCategories.map(cat => (
                            <button
                                key={cat.id}
                                onClick={() => setSelectedCategory(cat.id)}
                                className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition-colors border ${selectedCategory === cat.id ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 hover:bg-gray-100 border-gray-300'}`}
                            >
                                <span className="mr-2">{cat.icon}</span>
                                {cat.title}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Templates & Connections */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <SocialTemplates brandColor={brandPurple} onSelect={setSelectedTemplate} />
                    <PlatformConnections />
                </div>

                {/* Step 2: Provide Instructions */}
                <div>
                    <h3 className="text-base font-semibold text-gray-800 mb-3">2. Provide Instructions</h3>
                    <div className="bg-white p-1 rounded-lg border flex mb-2">
                        <button onClick={() => setActiveTab('audio')} className={`w-1/2 py-2 rounded-md text-sm font-medium flex items-center justify-center space-x-2 transition-colors ${activeTab === 'audio' ? 'bg-gray-100 shadow-sm text-gray-800' : 'text-gray-500'}`}>
                           <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93V17a1 1 0 102 0v-2.07A5.986 5.986 0 0113 11v-1a1 1 0 10-2 0v1a3.987 3.987 0 00-1.03.177A1 1 0 008 11v1a5.986 5.986 0 013 3.93z" /></svg>
                           <span>Audio</span>
                        </button>
                        <button onClick={() => setActiveTab('text')} className={`w-1/2 py-2 rounded-md text-sm font-medium flex items-center justify-center space-x-2 transition-colors ${activeTab === 'text' ? 'bg-gray-100 shadow-sm text-gray-800' : 'text-gray-500'}`}>
                           <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2h12v1H4V6zm0 3h12v1H4V9zm0 3h12v1H4v-1z" clipRule="evenodd" /></svg>
                           <span>Text</span>
                        </button>
                    </div>

                    {activeTab === 'audio' ? (
                        <div className="bg-white p-4 rounded-lg border text-center">
                            <p className="text-sm text-gray-500 mb-4">Recording UI (simulation)</p>
                            <div className="flex justify-center items-center space-x-4">
                                <button className="w-16 h-16 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 shadow-lg"><svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93V17a1 1 0 102 0v-2.07A5.986 5.986 0 0113 11v-1a1 1 0 10-2 0v1a3.987 3.987 0 00-1.03.177A1 1 0 008 11v1a5.986 5.986 0 013 3.93z" clipRule="evenodd" /></svg></button>
                            </div>
                        </div>
                    ) : (
                        <textarea
                            value={instructions}
                            onChange={e => setInstructions(e.target.value)}
                            rows={4}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 bg-white"
                            placeholder="e.g., A modern 2-story house in the suburbs with a pool."
                        />
                    )}
                </div>

                {/* Step 3: Generate Button */}
                <button
                    onClick={handleGenerate}
                    disabled={isLoading || !instructions.trim()}
                    className="w-full flex items-center justify-center bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-blue-700 transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300 disabled:bg-blue-300 disabled:cursor-not-allowed"
                >
                    {isLoading ? (
                        <>
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Generating Post...
                        </>
                    ) : (
                        '✨ Generate Post with AI'
                    )}
                </button>

                {/* Scheduling & Campaign Coordination */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <PostScheduler
                        defaultCaption={defaultCaption}
                        defaultImageUrl={defaultImageUrl}
                        onPostNow={handlePostNow}
                        onSchedule={handleSchedule}
                    />
                    <SocialCampaigns
                        selectedTemplate={selectedTemplate}
                        property={property ? { title: property.title, address: property.address, price: property.price, beds: property.beds, baths: property.baths, sqft: property.sqft, imageUrl: property.imageUrl } : null}
                    />
                </div>

                {/* Step 4: Display Result */}
                {generatedPost && (
                    <div>
                        <h3 className="text-base font-semibold text-gray-800 mb-3">4. Generated Post</h3>
                        <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
                            <div className="p-3 flex items-center space-x-3 border-b">
                                <img src="https://images.unsplash.com/photo-1557862921-37829c790f19?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" alt="User avatar" className="w-10 h-10 rounded-full" />
                                <div>
                                    <p className="font-semibold text-sm">Ryan's Realty</p>
                                    <p className="text-xs text-gray-500">Beverly Hills, CA</p>
                                </div>
                            </div>
                            <img src={generatedPost.image} alt="Generated property" className="w-full h-auto" />
                            <div className="p-4">
                                <p className="text-sm text-gray-800 whitespace-pre-wrap">{generatedPost.caption}</p>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default SocialMediaView;
