import React, { useCallback, useEffect, useMemo } from 'react';
import BottomNav from '@components/BottomNav';
import CommandCenter from '@components/CommandCenter';
import DashboardView from '@components/DashboardView.mobile';
import PropertiesScreen from '@screens/PropertiesScreen';
import TasksView from '@components/TasksView';
import ChatView from '@components/ChatView';
import ProfileView from '@components/ProfileView';
import FeatureView from '@components/FeatureView';
import MarketingView from '@components/MarketingView';
import SocialMediaView from '@components/SocialMediaView';
import ContactManagementView from '@components/ContactManagementView';
import PlaywrightTestView from '@components/PlaywrightTestView';
import TransactionsView from '@components/TransactionsView';
import StrategyView from '@components/StrategyView';
import PackagesView from '@components/PackagesView';
import RequestsView from '@components/RequestsView';
import LoginView from '@components/LoginView';

import { View, ActionId, CommandRequest } from '@/types';
import { ACTION_ITEMS } from '@/constants.tsx';
import {
    useUIStore,
    selectCommandCenterOpen,
    selectCommandMode,
    selectCommandStatus,
    selectCommandText,
    selectCommandTranscript,
    selectCommandError,
    useUserStore,
    selectAuthToken,
    usePropertyStore,
    selectPropertyFetchStatus,
    useClientStore,
    selectClientFetchStatus,
} from '@/store';

// Development mock user for bypassing authentication
const DEV_MOCK_USER = {
    id: 'dev-user-001',
    name: 'Development User',
    email: 'dev@local',
    role: 'admin',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
};

const App: React.FC = () => {
    const [currentView, setCurrentView] = React.useState<View>('dashboard');
    const [selectedAction, setSelectedAction] = React.useState<ActionId | null>(null);

    const authToken = useUserStore(selectAuthToken);
    const login = useUserStore((state) => state.login);

    const propertyFetchStatus = usePropertyStore(selectPropertyFetchStatus);
    const clientFetchStatus = useClientStore(selectClientFetchStatus);
    const fetchProperties = usePropertyStore((state) => state.fetchProperties);
    const fetchClients = useClientStore((state) => state.fetchClients);

    const commandCenterOpen = useUIStore(selectCommandCenterOpen);
    const commandMode = useUIStore(selectCommandMode);
    const commandStatus = useUIStore(selectCommandStatus);
    const commandText = useUIStore(selectCommandText);
    const commandTranscript = useUIStore(selectCommandTranscript);
    const commandError = useUIStore(selectCommandError);

    const openCommandCenter = useUIStore((state) => state.openCommandCenter);
    const closeCommandCenter = useUIStore((state) => state.closeCommandCenter);
    const setCommandMode = useUIStore((state) => state.setCommandMode);
    const setCommandStatus = useUIStore((state) => state.setCommandStatus);
    const setCommandText = useUIStore((state) => state.setCommandText);
    const setCommandTranscript = useUIStore((state) => state.setCommandTranscript);
    const setCommandError = useUIStore((state) => state.setCommandError);
    const resetCommandState = useUIStore((state) => state.resetCommandState);

    const isAuthenticated = Boolean(authToken);

    // Development authentication bypass
    useEffect(() => {
        if (import.meta.env?.DEV && !authToken) {
            // Auto-authenticate with mock user in development
            login({
                user: DEV_MOCK_USER,
                accessToken: 'dev-mock-token',
                refreshToken: 'dev-mock-refresh-token',
                expiresAt: Date.now() + 24 * 60 * 60 * 1000, // 24 hours
            });
            
            // Clear any stale tokens from previous sessions
            localStorage.removeItem('token');
        }
    }, [login, authToken]);

    useEffect(() => {
        if (!isAuthenticated) {
            return;
        }
        if (propertyFetchStatus === 'idle') {
            fetchProperties().catch(() => {});
        }
        if (clientFetchStatus === 'idle') {
            fetchClients().catch(() => {});
        }
    }, [isAuthenticated, propertyFetchStatus, clientFetchStatus, fetchProperties, fetchClients]);

    const handleActionClick = useCallback((id: ActionId) => {
        setSelectedAction(id);
    }, []);

    const handleBackFromFeature = useCallback(() => {
        setSelectedAction(null);
    }, []);

    const handleCommandSubmit = useCallback(
        async (request: CommandRequest) => {
            setCommandStatus('processing');
            
            try {
                // Import the store dynamically to avoid circular dependency issues
                const { useAIRequestStore } = await import('@/store');
                const createFromCommand = useAIRequestStore.getState().createFromCommand;
                
                // Extract content based on request type
                const content = request.kind === 'text' 
                    ? request.prompt 
                    : request.transcript;
                
                // Determine team/category from content or use default
                let team = 'marketing'; // default
                const contentLower = content.toLowerCase();
                
                if (contentLower.includes('analytic') || contentLower.includes('data') || contentLower.includes('report')) {
                    team = 'analytics';
                } else if (contentLower.includes('social') || contentLower.includes('post') || contentLower.includes('instagram') || contentLower.includes('facebook')) {
                    team = 'social';
                } else if (contentLower.includes('strategy') || contentLower.includes('plan')) {
                    team = 'strategy';
                } else if (contentLower.includes('transaction') || contentLower.includes('contract') || contentLower.includes('closing')) {
                    team = 'transactions';
                }
                
                // Create the AI request
                const aiRequest = await createFromCommand(content, team, 5);
                
                useUIStore.getState().pushSnackbar({
                    id: `command-success-${aiRequest.id}`,
                    message: `AI request created: ${aiRequest.title.slice(0, 50)}${aiRequest.title.length > 50 ? '...' : ''}`,
                    type: 'success',
                });
                
                resetCommandState();
            } catch (error) {
                console.error('Command submission failed', error);
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                setCommandError(errorMessage);
                setCommandStatus('reviewing');
                
                useUIStore.getState().pushSnackbar({
                    id: `command-error-${Date.now()}`,
                    message: `Failed to create AI request: ${errorMessage}`,
                    type: 'error',
                });
            }
        },
        [resetCommandState, setCommandError, setCommandStatus]
    );

    const commandContext = useMemo(
        () => ({
            commandMode,
            commandStatus,
            commandText,
            commandTranscript,
            commandError,
        }),
        [commandMode, commandStatus, commandText, commandTranscript, commandError]
    );

    // DEVELOPMENT: Skip authentication completely for now
    // TODO: Re-enable authentication once backend is working
    // if (!isAuthenticated && !import.meta.env?.DEV) {
    //     return <LoginView />;
    // }

    const renderView = () => {
        switch (currentView) {
            case 'dashboard':
                return <DashboardView onActionClick={handleActionClick} onRequestClick={() => {}} />;
            case 'tasks':
                return <TasksView />;
            case 'chat':
                return <ChatView />;
            case 'profile':
                return <ProfileView />;
            case 'properties':
                return <PropertiesScreen />;
            case 'requests':
                return <RequestsView />;
            default:
                return <DashboardView onActionClick={handleActionClick} onRequestClick={() => {}} />;
        }
    };

    const selectedActionData = selectedAction ? ACTION_ITEMS.find(item => item.id === selectedAction) : null;

    const renderFeatureView = () => {
        if (!selectedAction) return null;

        switch (selectedAction) {
            case 'marketing':
                return <MarketingView onBack={handleBackFromFeature} />;
            case 'social':
                return <SocialMediaView onBack={handleBackFromFeature} />;
            case 'strategy':
                return <StrategyView onBack={handleBackFromFeature} />;
            case 'packages':
                return <PackagesView onBack={handleBackFromFeature} />;
            case 'contacts':
                return <ContactManagementView onBack={handleBackFromFeature} />;
            case 'transactions':
                return <TransactionsView onBack={handleBackFromFeature} />;
            case 'playwright':
                return <PlaywrightTestView onBack={handleBackFromFeature} />;
            default:
                if (selectedActionData) {
                    return <FeatureView title={selectedActionData.title} onBack={handleBackFromFeature} />;
                }
                return null;
        }
    };

    return (
        <div className="min-h-screen font-sans md:flex md:items-center md:justify-center md:p-4">
            <div className="w-full h-screen bg-white flex flex-col relative md:max-w-4xl md:h-[calc(100vh-2rem)] md:rounded-[48px] md:shadow-2xl overflow-hidden">
                {selectedAction ? (
                    renderFeatureView()
                ) : (
                    <>
                        <div className="flex-grow overflow-hidden">
                            {renderView()}
                        </div>
                        <BottomNav
                            activeView={currentView}
                            onNavigate={setCurrentView}
                            onOpenCommandCenter={() => openCommandCenter()}
                            commandMode={commandMode}
                            commandStatus={commandStatus}
                            isCommandCenterOpen={commandCenterOpen}
                        />
                        {commandCenterOpen && (
                            <CommandCenter
                                onClose={() => closeCommandCenter()}
                                onModeChange={setCommandMode}
                                onStatusChange={setCommandStatus}
                                onTextChange={setCommandText}
                                onTranscriptChange={setCommandTranscript}
                                onSubmit={handleCommandSubmit}
                                context={commandContext}
                            />
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default App;
