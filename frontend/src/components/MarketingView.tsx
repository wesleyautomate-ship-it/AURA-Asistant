import React, { useState, useEffect, useRef } from 'react';

    import MarketingTemplates from './MarketingTemplates';
    import PostcardTemplates from './PostcardTemplates';
    import EmailCampaigns from './EmailCampaigns';
    import CampaignAnalytics from './CampaignAnalytics';
    import { usePropertyStore } from '../store/propertyStore';

    interface GeneratedContent {
        id: string;
        type: string;
        title: string;
        content: string;
        status: 'generated' | 'approved' | 'published';
        createdAt: string;
    }
// AURA-inspired property selection interfaces
interface Property {
    id: string;
    address: string;
    price: string;
    beds: number;
    baths: number;
    sqft: number;
    image: string;
    status: 'active' | 'sold' | 'pending';
}

interface WorkflowStep {
    id: string;
    title: string;
    description: string;
    status: 'pending' | 'active' | 'completed';
}

const MarketingView: React.FC<{ onBack: () => void; }> = ({ onBack }) => {
    const [inputMethod, setInputMethod] = useState<'voice' | 'text'>('voice');
    const [prompt, setPrompt] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0);
    const [generatedContent, setGeneratedContent] = useState<GeneratedContent[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [audioLevel, setAudioLevel] = useState(0);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const animationFrameRef = useRef<number | null>(null);
    
    // AURA-inspired state management
    const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
    const [currentStep, setCurrentStep] = useState(1);
    const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([
        { id: '1', title: 'Select Property', description: 'Choose or add a property for analysis', status: 'active' },
        { id: '2', title: 'Enter Instructions', description: 'Tell AI what content to create', status: 'pending' },
        { id: '3', title: 'AI Processing', description: 'Generating your content', status: 'pending' },
        { id: '4', title: 'Review Results', description: 'Approve and use your content', status: 'pending' }
    ]);
    
    // Beta-1 property store integration (auto-populate when available)
    const propertyStore = usePropertyStore();
    const [displayedProperties, setDisplayedProperties] = useState<Property[]>([]);
    const brandPurple = '#7c3aed';
    const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);

    useEffect(() => {
        try {
            // Attempt to fetch properties when component mounts
            // @ts-ignore Optional chaining for robustness
            if (propertyStore.fetch?.status === 'idle' || !propertyStore.fetch?.lastUpdated) {
                propertyStore.fetchProperties().catch(() => {});
            }
        } catch {}
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        const items: any[] = (propertyStore as any)?.items || [];
        if (Array.isArray(items) && items.length > 0) {
            const mapped: Property[] = items.map((p: any) => ({
                id: String(p.id),
                address: p.address || p.title || 'Property',
                price: typeof p.price === 'number' ? `$${p.price.toLocaleString()}` : (p.price || '$0'),
                beds: p.beds ?? 0,
                baths: p.baths ?? 0,
                sqft: p.sqft ?? 0,
                image: p.imageUrl || 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400&h=300&fit=crop',
                status: p.status || 'active',
            }));
            setDisplayedProperties(mapped);
        } else {
            setDisplayedProperties(sampleProperties);
        }
    }, [propertyStore]);

    // AURA-inspired sample properties
    const sampleProperties: Property[] = [
        {
            id: '1',
            address: 'Seven Palm, 2 Bedroom',
            price: '$3.4M',
            beds: 2,
            baths: 2,
            sqft: 1200,
            image: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&h=300&fit=crop',
            status: 'active'
        },
        {
            id: '2',
            address: '123 Ocean Drive, Penthouse',
            price: '$5.2M',
            beds: 3,
            baths: 3,
            sqft: 1800,
            image: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400&h=300&fit=crop',
            status: 'active'
        },
        {
            id: '3',
            address: '456 Main Street, Commercial',
            price: '$2.8M',
            beds: 0,
            baths: 2,
            sqft: 2500,
            image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&h=300&fit=crop',
            status: 'active'
        }
    ];

    // AURA-inspired sample prompts
    const samplePrompts = [
        "Create a CMA for this property with market analysis",
        "Generate a marketing plan and brochure for the owner",
        "Create social media posts and investor deck",
        "Make a newsletter about this property for my clients",
        "Analyze investment potential and create presentation"
    ];

    // Timer effect
    useEffect(() => {
        let interval: NodeJS.Timeout | null = null;
        if (isRecording) {
            interval = setInterval(() => {
                setElapsedTime(time => time + 1);
            }, 1000);
        } else if (interval) {
            clearInterval(interval);
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [isRecording]);

    // Format time as MM:SS
    const formatTime = (time: number) => {
        const minutes = Math.floor(time / 60).toString().padStart(2, '0');
        const seconds = (time % 60).toString().padStart(2, '0');
        return `${minutes}:${seconds}`;
    };

    // Reactive waveform based on actual audio levels
    const waveformHeights = Array.from({ length: 50 }, (_, index) => {
        if (!isRecording) return 4;
        // Create a more dynamic waveform based on audio level and position
        const baseHeight = 4;
        const maxHeight = 60;
        const audioInfluence = audioLevel * 0.8;
        const positionInfluence = Math.sin((index / 50) * Math.PI * 4) * 10;
        const randomInfluence = Math.random() * 15;
        return Math.max(baseHeight, Math.min(maxHeight, baseHeight + audioInfluence + positionInfluence + randomInfluence));
    });

    // Audio level monitoring
    const monitorAudioLevel = () => {
        if (analyserRef.current && isRecording) {
            const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
            analyserRef.current.getByteFrequencyData(dataArray);
            
            // Calculate average audio level
            const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
            setAudioLevel(average / 255); // Normalize to 0-1
            
            animationFrameRef.current = requestAnimationFrame(monitorAudioLevel);
        }
    };

    useEffect(() => {
        if (isRecording) {
            monitorAudioLevel();
        } else {
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }
            setAudioLevel(0);
        }
        
        return () => {
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }
        };
    }, [isRecording]);

    const handleVoiceRecording = async () => {
        if (isRecording) {
            // Stop recording
            setIsRecording(false);
            setElapsedTime(0);
            // In a real app, this would process the recorded audio
            setPrompt("Create a CMA for Seven Palm, 2 bed asking price 3.4 million");
        } else {
            // Start recording
            try {
                // Request microphone access
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                // Set up audio context for level monitoring
                audioContextRef.current = new AudioContext();
                const source = audioContextRef.current.createMediaStreamSource(stream);
                analyserRef.current = audioContextRef.current.createAnalyser();
                analyserRef.current.fftSize = 256;
                source.connect(analyserRef.current);
                
                setIsRecording(true);
                setElapsedTime(0);
        setError(null);
            } catch (error) {
                setError('Microphone access denied. Please allow microphone access to use voice input.');
            }
        }
    };

    const handlePromptSubmit = () => {
        if (!prompt.trim()) {
            setError('Please tell PropertyPro AI what you need.');
            return;
        }

        setIsProcessing(true);
        setError(null);
        
        // Advance to processing step
        setCurrentStep(3);
        setWorkflowSteps(prev => prev.map(step => 
            step.id === '2' 
                ? { ...step, status: 'completed' as const }
                : step.id === '3'
                ? { ...step, status: 'active' as const }
                : step
        ));

        // Simulate AI processing - backend will analyze the prompt and generate appropriate content
        setTimeout(() => {
            const newContent: GeneratedContent[] = [];
            
            // AI analyzes the prompt and determines what content to create
            if (prompt.toLowerCase().includes('cma')) {
                newContent.push({
                    id: '1',
                    type: 'CMA Report',
                    title: 'Comparative Market Analysis - Seven Palm',
                    content: `# Comparative Market Analysis - Seven Palm\n\n## Property Details\n- Address: Seven Palm\n- Bedrooms: 2\n- Asking Price: $3.4M\n\n## Market Analysis\nBased on recent sales in the area, this property is competitively priced. Similar 2-bedroom units in the building have sold for $3.2M-$3.6M in the past 6 months.\n\n## Recommended Strategy\n- List at $3.4M (current asking price is optimal)\n- Market to young professionals and investors\n- Highlight building amenities and location\n\n## Comparable Sales\n- Unit 12B: $3.2M (sold 3 months ago)\n- Unit 8A: $3.5M (sold 1 month ago)\n- Unit 15C: $3.6M (sold 2 months ago)`,
                    status: 'generated',
                    createdAt: new Date().toISOString()
                });
            }
            
            if (prompt.toLowerCase().includes('marketing plan') || prompt.toLowerCase().includes('brochure')) {
                newContent.push({
                    id: '2',
                    type: 'Marketing Plan',
                    title: 'Marketing Strategy - Seven Palm',
                    content: `# Marketing Plan - Seven Palm\n\n## Target Audience\n- Young professionals (25-35)\n- First-time luxury buyers\n- Real estate investors\n\n## Marketing Channels\n1. **Digital Marketing**\n   - Professional photography\n   - Virtual tour\n   - Social media campaigns\n\n2. **Traditional Marketing**\n   - Luxury property brochures\n   - Open house events\n   - Agent network promotion\n\n## Timeline\n- Week 1: Photography and staging\n- Week 2: Digital marketing launch\n- Week 3: Open house preparation\n- Week 4: First open house`,
                    status: 'generated',
                    createdAt: new Date().toISOString()
                });
            }
            
            if (prompt.toLowerCase().includes('brochure')) {
                newContent.push({
                    id: '3',
                    type: 'Property Brochure',
                    title: 'Seven Palm - Luxury Living',
                    content: `# Seven Palm - Luxury Living\n\n## Welcome to Seven Palm\nExperience the pinnacle of luxury living in this stunning 2-bedroom residence.\n\n## Key Features\n- 2 spacious bedrooms with city views\n- Modern open-concept living\n- Premium finishes throughout\n- Building amenities: gym, pool, concierge\n\n## Location Benefits\n- Prime downtown location\n- Walking distance to restaurants\n- Easy access to public transport\n- Close to business district\n\n## Investment Opportunity\n- Strong rental potential\n- Appreciating neighborhood\n- Low maintenance building\n\n**Asking Price: $3.4M**\n\n*Contact us for a private viewing*`,
                    status: 'generated',
                    createdAt: new Date().toISOString()
                });
            }
            
            setGeneratedContent(prev => [...newContent, ...prev]);
            setIsProcessing(false);
            setPrompt(''); // Clear the prompt after processing
            
            // Advance to results step
            setCurrentStep(4);
            setWorkflowSteps(prev => prev.map(step => 
                step.id === '3' 
                    ? { ...step, status: 'completed' as const }
                    : step.id === '4'
                    ? { ...step, status: 'active' as const }
                    : step
            ));
        }, 3000);
    };

    const handleSamplePrompt = (samplePrompt: string) => {
        setPrompt(samplePrompt);
    };

    // AURA-inspired handler functions
    const handlePropertySelect = (property: Property) => {
        setSelectedProperty(property);
        setCurrentStep(2);
        setWorkflowSteps(prev => prev.map(step => 
            step.id === '1' 
                ? { ...step, status: 'completed' as const }
                : step.id === '2'
                ? { ...step, status: 'active' as const }
                : step
        ));
    };

    const handleAddNewProperty = () => {
        // In a real app, this would open a property addition form
        const newProperty: Property = {
            id: Date.now().toString(),
            address: 'New Property Address',
            price: '$0',
            beds: 0,
            baths: 0,
            sqft: 0,
            image: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&h=300&fit=crop',
            status: 'active'
        };
        handlePropertySelect(newProperty);
    };

    const handleNextStep = () => {
        if (currentStep < 4) {
            setCurrentStep(currentStep + 1);
            setWorkflowSteps(prev => prev.map(step => 
                step.id === currentStep.toString()
                    ? { ...step, status: 'completed' as const }
                    : step.id === (currentStep + 1).toString()
                    ? { ...step, status: 'active' as const }
                    : step
            ));
        }
    };

    const handleApproveContent = (contentId: string) => {
        setGeneratedContent(prev => 
            prev.map(content => 
                content.id === contentId 
                    ? { ...content, status: 'approved' as const }
                    : content
            )
        );
    };

    const handleCopyContent = (content: string) => {
        navigator.clipboard.writeText(content);
        // Could add a toast notification here
    };

    const handleDeleteContent = (contentId: string) => {
        setGeneratedContent(prev => prev.filter(content => content.id !== contentId));
    };

    const getContentTypeColor = (type: string) => {
        switch (type.toLowerCase()) {
            case 'cma report': return 'bg-blue-100 text-blue-800 border-blue-200';
            case 'marketing plan': return 'bg-green-100 text-green-800 border-green-200';
            case 'property brochure': return 'bg-purple-100 text-purple-800 border-purple-200';
            case 'social media': return 'bg-pink-100 text-pink-800 border-pink-200';
            case 'newsletter': return 'bg-orange-100 text-orange-800 border-orange-200';
            default: return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };
    
    return (
        <div className="flex flex-col h-full bg-gradient-to-br from-gray-50 to-gray-100">
            {/* Header */}
            <header className="flex items-center justify-between p-6 border-b border-gray-200 bg-white/80 backdrop-blur-sm shadow-sm">
                <div className="flex items-center">
                    <button onClick={onBack} className="p-2 rounded-xl hover:bg-gray-100 transition-colors duration-200" aria-label="Go back">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                </button>
                    <div className="ml-4">
                        <h2 className="text-xl font-semibold text-gray-900">Marketing</h2>
                        <p className="text-sm text-gray-500">AI-powered content creation for real estate</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-gray-500 font-medium">AI Ready</span>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto p-6 md:p-8 pb-20">
                {/* AURA-inspired Workflow Steps */}
                <div className="max-w-6xl mx-auto mb-8">
                    <div className="flex items-center justify-between">
                        {workflowSteps.map((step, index) => (
                            <div key={step.id} className="flex items-center">
                                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300 ${
                                    step.status === 'completed' 
                                        ? 'bg-green-500 border-green-500 text-white' 
                                        : step.status === 'active'
                                        ? 'bg-blue-500 border-blue-500 text-white'
                                        : 'bg-white border-gray-300 text-gray-400'
                                }`}>
                                    {step.status === 'completed' ? (
                                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                    ) : (
                                        <span className="text-sm font-semibold">{index + 1}</span>
                                    )}
                                </div>
                                <div className="ml-3 hidden md:block">
                                    <p className={`text-sm font-medium ${
                                        step.status === 'active' ? 'text-blue-600' : 
                                        step.status === 'completed' ? 'text-green-600' : 'text-gray-400'
                                    }`}>
                                        {step.title}
                                    </p>
                                    <p className="text-xs text-gray-500">{step.description}</p>
                                </div>
                                {index < workflowSteps.length - 1 && (
                                    <div className={`hidden md:block w-16 h-0.5 mx-4 ${
                                        step.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'
                                    }`} />
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="max-w-6xl mx-auto">
                    {/* AURA-inspired Property Selection */}
                    {currentStep === 1 && (
                        <div className="mb-8">
                            <div className="text-center mb-8">
                                <h3 className="text-2xl font-bold text-gray-900 mb-2">Select a Property</h3>
                                <p className="text-gray-600">Choose a property to analyze or add a new one</p>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                                {sampleProperties.map((property) => (
                                    <div
                                        key={property.id}
                                        onClick={() => handlePropertySelect(property)}
                                        className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-lg shadow-gray-100 hover:shadow-xl hover:shadow-gray-200 transition-all duration-300 cursor-pointer transform hover:scale-[1.02]"
                                    >
                                        <div className="relative">
                                            <img
                                                src={property.image}
                                                alt={property.address}
                                                className="w-full h-48 object-cover"
                                            />
                                            <div className="absolute top-4 right-4">
                                                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                                    property.status === 'active' 
                                                        ? 'bg-green-100 text-green-800' 
                                                        : 'bg-gray-100 text-gray-800'
                                                }`}>
                                                    {property.status}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="p-6">
                                            <h4 className="text-lg font-semibold text-gray-900 mb-2">{property.address}</h4>
                                            <div className="flex items-center justify-between mb-3">
                                                <span className="text-2xl font-bold text-blue-600">{property.price}</span>
                                                <div className="flex items-center space-x-4 text-sm text-gray-600">
                                                    {property.beds > 0 && <span>{property.beds} bed</span>}
                                                    <span>{property.baths} bath</span>
                                                    <span>{property.sqft.toLocaleString()} sqft</span>
                                                </div>
                                            </div>
                                            <button className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-600 transition-colors">
                                                Select Property
                                            </button>
                                        </div>
                                    </div>
                                ))}
                                
                                {/* Add New Property Card */}
                                <div
                                    onClick={handleAddNewProperty}
                                    className="bg-white rounded-2xl border-2 border-dashed border-gray-300 overflow-hidden shadow-lg shadow-gray-100 hover:shadow-xl hover:shadow-gray-200 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] flex items-center justify-center min-h-[300px]"
                                >
                                    <div className="text-center p-6">
                                        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                            </svg>
                                        </div>
                                        <h4 className="text-lg font-semibold text-gray-900 mb-2">Add New Property</h4>
                                        <p className="text-gray-600 text-sm">Add a property that's not in your portfolio</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Instructions Input (Step 2) */}
                    {currentStep === 2 && (
                        <div className="mb-8">
                            <div className="text-center mb-8">
                                <h3 className="text-2xl font-bold text-gray-900 mb-2">Enter Instructions</h3>
                                <p className="text-gray-600">Tell AI what content to create for {selectedProperty?.address}</p>
                            </div>
                            
                            {/* Input Method Toggle */}
                    <div className="flex justify-center mb-8">
                        <div className="bg-white rounded-2xl border border-gray-200 p-1 flex shadow-lg shadow-gray-100">
                            <button
                                onClick={() => setInputMethod('voice')}
                                className={`px-8 py-4 rounded-xl text-sm font-semibold transition-all duration-200 ${
                                    inputMethod === 'voice' 
                                        ? 'bg-red-500 text-white shadow-lg shadow-red-200' 
                                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                                }`}
                            >
                                🎤 Voice Input
                            </button>
                            <button
                                onClick={() => setInputMethod('text')}
                                className={`px-8 py-4 rounded-xl text-sm font-semibold transition-all duration-200 ${
                                    inputMethod === 'text' 
                                        ? 'bg-blue-500 text-white shadow-lg shadow-blue-200' 
                                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                                }`}
                            >
                                ✏️ Text Input
                            </button>
                        </div>
                    </div>

                    {/* Voice Input - Modern Design */}
                    {inputMethod === 'voice' && (
                        <div className="bg-white rounded-3xl border border-gray-200 p-12 text-center shadow-xl shadow-gray-100">
                            {/* Timer and Waveform */}
                            <div className="mb-8">
                                <p className="text-5xl font-light text-gray-900 tracking-wider mb-6">
                                    {isRecording ? formatTime(elapsedTime) : '00:00'}
                                </p>
                                <div className="w-full h-20 flex items-center justify-center space-x-1.5">
                                    {waveformHeights.map((height, index) => (
                                        <div 
                                            key={index}
                                            className="w-1.5 rounded-full bg-gradient-to-t from-red-500 to-red-400 transition-all duration-150"
                                            style={{ height: `${height}px` }}
                                        ></div>
                                    ))}
                                </div>
                            </div>

                            {/* Voice Button */}
                            <div className="mb-6">
                                {!isRecording ? (
                                    <button 
                                        onClick={handleVoiceRecording}
                                        className="w-24 h-24 rounded-full bg-gradient-to-br from-red-500 to-red-600 text-white flex items-center justify-center shadow-2xl shadow-red-500/30 hover:shadow-red-500/40 transition-all duration-300 transform hover:scale-105 hover:from-red-600 hover:to-red-700"
                                        aria-label="Start recording"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93V17a1 1 0 102 0v-2.07A5.986 5.986 0 0113 11v-1a1 1 0 10-2 0v1a3.987 3.987 0 00-1.03.177A1 1 0 008 11v1a5.986 5.986 0 013 3.93z" clipRule="evenodd" />
                                        </svg>
                                    </button>
                                ) : (
                                    <button 
                                        onClick={handleVoiceRecording}
                                        className="w-24 h-24 rounded-full bg-gradient-to-br from-red-500 to-red-600 text-white flex items-center justify-center shadow-2xl shadow-red-500/30 hover:shadow-red-500/40 transition-all duration-300 transform hover:scale-105 hover:from-red-600 hover:to-red-700 animate-pulse"
                                        aria-label="Stop recording"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                        </svg>
                                    </button>
                                )}
                            </div>

                            <p className="text-base text-gray-600 mb-6 font-medium">
                                {isRecording ? 'Recording... Click to stop' : 'Tap the microphone to start recording your request'}
                            </p>

                            {/* Prompt Display */}
                            {prompt && (
                                <div className="bg-gray-50 rounded-lg p-4 text-left">
                                    <p className="text-sm text-gray-700">"{prompt}"</p>
                            </div>
                            )}
                        </div>
                    )}

                    {/* Text Input */}
                    {inputMethod === 'text' && (
                        <div className="bg-white rounded-3xl border border-gray-200 p-8 shadow-xl shadow-gray-100">
                            <textarea
                                value={prompt}
                                onChange={e => setPrompt(e.target.value)}
                                className="w-full p-6 border-0 resize-none focus:ring-0 text-lg bg-transparent placeholder-gray-400"
                                rows={5}
                                placeholder="Describe what you need... e.g., Create a CMA for Seven Palm, 2 bed asking price 3.4 million"
                            />
                        </div>
                    )}

                    {/* Processing Step (Step 3) */}
                    {currentStep === 3 && (
                        <div className="text-center py-12">
                            <div className="bg-white rounded-3xl border border-gray-200 p-12 shadow-xl shadow-gray-100">
                                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                                    <svg className="animate-spin h-10 w-10 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                </div>
                                <h3 className="text-2xl font-bold text-gray-900 mb-4">AI is Working</h3>
                                <p className="text-gray-600 mb-6">Analyzing {selectedProperty?.address} and generating your content...</p>
                                <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                                    <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
                                </div>
                                <p className="text-sm text-gray-500">This usually takes 2-3 minutes</p>
                            </div>
                        </div>
                    )}

                    {/* Submit Button - Only show in step 2 */}
                    {currentStep === 2 && (
                        <div className="mt-8">
                            <button 
                                onClick={handlePromptSubmit}
                                disabled={isProcessing || !prompt.trim()}
                                className="w-full flex items-center justify-center bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-5 px-8 rounded-2xl shadow-xl shadow-blue-500/25 hover:shadow-blue-500/35 transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-300 disabled:from-gray-400 disabled:to-gray-500 disabled:shadow-none text-lg transform hover:scale-[1.02]"
                            >
                                {isProcessing ? (
                                    <>
                                        <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        PropertyPro AI is working on it...
                                    </>
                                ) : (
                                    '✨ Generate Content with AI'
                                )}
                            </button>
                        </div>
                    )}

                    {error && <p className="text-sm text-red-600 bg-red-100 p-3 rounded-md mt-4">{error}</p>}
                        </div>
                    )}
                    
                    {/* Sample Prompts - Only show in step 2 */}
                    {currentStep === 2 && (
                    <div className="mb-8">
                        <div className="text-center mb-6">
                            <h4 className="text-lg font-semibold text-gray-900 mb-2">Need inspiration?</h4>
                            <p className="text-sm text-gray-500">Try these examples to get started</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {samplePrompts.map((sample, index) => (
                                <button
                                    key={index}
                                    onClick={() => handleSamplePrompt(sample)}
                                    className="text-left bg-white rounded-2xl border border-gray-200 p-6 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 text-sm text-gray-700 shadow-lg shadow-gray-100 hover:shadow-xl hover:shadow-gray-200 transform hover:scale-[1.02]"
                                >
                                    <div className="flex items-start space-x-3">
                                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                            <span className="text-blue-600 font-semibold text-xs">{index + 1}</span>
                                        </div>
                                        <p className="leading-relaxed">"{sample}"</p>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                    )}

                    {/* Generated Content - Actionable Results (Step 4) */}
                    {currentStep === 4 && generatedContent.length > 0 && (
                        <div>
                            <h3 className="text-lg font-semibold text-gray-800 mb-4">Generated Content</h3>
                            <div className="space-y-4">
                                {generatedContent.map((content) => (
                                    <div key={content.id} className="bg-white rounded-lg border shadow-sm overflow-hidden">
                                        {/* Content Header */}
                                        <div className="p-4 border-b bg-gray-50">
                                            <div className="flex justify-between items-start">
                                                <div className="flex-1">
                                                    <h4 className="font-semibold text-gray-800 mb-1">{content.title}</h4>
                                                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium border ${getContentTypeColor(content.type)}`}>
                                                        {content.type}
                                                    </span>
                                                </div>
                                                <div className="flex space-x-2">
                                                    <button 
                                                        onClick={() => handleApproveContent(content.id)}
                                                        className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                                                            content.status === 'approved' 
                                                                ? 'bg-green-100 text-green-800' 
                                                                : 'bg-gray-100 text-gray-700 hover:bg-green-100 hover:text-green-800'
                                                        }`}
                                                    >
                                                        {content.status === 'approved' ? '✅ Approved' : '✓ Approve'}
                                                    </button>
                                                    <button 
                                                        onClick={() => handleCopyContent(content.content)}
                                                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-md text-xs font-medium hover:bg-blue-200 transition-colors"
                                                    >
                                                        📋 Copy
                                                    </button>
                                                    <button 
                                                        onClick={() => handleDeleteContent(content.id)}
                                                        className="px-3 py-1 bg-red-100 text-red-800 rounded-md text-xs font-medium hover:bg-red-200 transition-colors"
                                                    >
                                                        🗑️ Delete
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        {/* Content Body */}
                                        <div className="p-4">
                                            <div className="prose prose-sm max-w-none">
                                                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans bg-gray-50 p-4 rounded-lg border">
                                                    {content.content}
                                                </pre>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default MarketingView;

