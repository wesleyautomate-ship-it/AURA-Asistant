import React, { useCallback, useMemo } from 'react';
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

import { View, ActionId, Task, CommandRequest } from '@/types';
import { ACTION_ITEMS, MOCK_TASKS } from '@/constants.tsx';
import {
    useUIStore,
    selectCommandCenterOpen,
    selectCommandMode,
    selectCommandStatus,
    selectCommandText,
    selectCommandTranscript,
    selectCommandError,
    selectSnackbars,
} from '@/store';

const App: React.FC = () => {
    const [currentView, setCurrentView] = React.useState<View>('dashboard');
    const [selectedAction, setSelectedAction] = React.useState<ActionId | null>(null);
    const [tasks, setTasks] = React.useState<Task[]>(MOCK_TASKS);

    const commandCenterOpen = useUIStore(selectCommandCenterOpen);
    const commandMode = useUIStore(selectCommandMode);
    const commandStatus = useUIStore(selectCommandStatus);
    const commandText = useUIStore(selectCommandText);
    const commandTranscript = useUIStore(selectCommandTranscript);
    const commandError = useUIStore(selectCommandError);
    const snackbars = useUIStore(selectSnackbars);

    const openCommandCenter = useUIStore((state) => state.openCommandCenter);
    const closeCommandCenter = useUIStore((state) => state.closeCommandCenter);
    const setCommandMode = useUIStore((state) => state.setCommandMode);
    const setCommandStatus = useUIStore((state) => state.setCommandStatus);
    const setCommandText = useUIStore((state) => state.setCommandText);
    const setCommandTranscript = useUIStore((state) => state.setCommandTranscript);
    const setCommandError = useUIStore((state) => state.setCommandError);
    const resetCommandState = useUIStore((state) => state.resetCommandState);

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
                // TODO: Integrate with workflow engine / AI coordinator
                // For now, simulate async handling and enqueue a snackbar
                await new Promise((resolve) => setTimeout(resolve, 1200));
                useUIStore.getState().pushSnackbar({
                    id: `command-${Date.now()}`,
                    message:
                        request.kind === 'text'
                            ? `Command received: ${request.prompt.slice(0, 72)}${
                                  request.prompt.length > 72 ? '…' : ''
                              }`
                            : `Voice command processed (${Math.round(request.duration / 1000)}s)` ,
                });
                resetCommandState();
            } catch (error) {
                console.error('Command submission failed', error);
                setCommandError(error instanceof Error ? error.message : 'Unknown error');
                setCommandStatus('reviewing');
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

    const renderView = () => {
        switch (currentView) {
            case 'dashboard':
                return <DashboardView onActionClick={handleActionClick} onRequestClick={() => {}} />;
            case 'tasks':
                return <TasksView tasks={tasks} setTasks={setTasks} />;
            case 'chat':
                return <ChatView />;
            case 'profile':
                return <ProfileView />;
            case 'properties':
                return <PropertiesScreen />;
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