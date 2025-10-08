# Aura Real Estate Assistant - Frontend Architecture

This document outlines the frontend architecture for the React 19 rebuild of the Aura Real Estate Assistant.

## Component Hierarchy

### Application Structure
```
src/
├── components/           # Reusable UI components
│   ├── common/          # Base components (Button, Input, Card, etc.)
│   ├── forms/           # Form-specific components
│   ├── layout/          # Layout components (Header, Sidebar, etc.)
│   ├── voice/           # Voice interface components
│   └── ai/              # AI interaction components
├── views/               # Page-level components
│   ├── Dashboard/       # Main dashboard view
│   ├── Marketing/       # Marketing automation view  
│   ├── Properties/      # Property management view
│   ├── Clients/         # Client management view
│   ├── Auth/           # Authentication views
│   └── Settings/       # Settings and configuration
├── hooks/              # Custom React hooks
│   ├── useVoice.ts     # Voice recording and processing
│   ├── useAI.ts        # AI service integration
│   ├── useAuth.ts      # Authentication state
│   └── useWebSocket.ts # Real-time communication
├── services/           # API and business logic
│   ├── api.ts          # API client configuration
│   ├── auth.service.ts # Authentication services
│   ├── ai.service.ts   # AI service integration
│   └── voice.service.ts # Voice processing services
├── store/              # State management (Zustand)
│   ├── auth.store.ts   # Authentication state
│   ├── ai.store.ts     # AI conversation state
│   ├── voice.store.ts  # Voice interface state
│   └── app.store.ts    # Global application state
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── styles/             # Global styles and themes
```

### Key Components

#### Voice Interface Components
```typescript
// Primary voice interaction component
<VoiceCommand>
  <MicrophoneButton size="20x20" />
  <WaveformVisualizer bars={50} />
  <Timer format="MM:SS" />
  <AudioLevelIndicator />
</VoiceCommand>

// Voice status and feedback
<VoiceStatus>
  <ListeningIndicator />
  <ProcessingSpinner />
  <ErrorMessage />
</VoiceStatus>
```

#### AI Response Components  
```typescript
// AI conversation interface
<AIChat>
  <MessageList>
    <UserMessage />
    <AIMessage streaming={true} />
  </MessageList>
  <InputArea>
    <VoiceCommand />
    <TextFallback />
  </InputArea>
</AIChat>

// AI-generated content display
<AIContentCard>
  <ContentPreview />
  <ActionButtons>
    <ApproveButton />
    <CopyButton />
    <DeleteButton />
  </ActionButtons>
</AIContentCard>
```

#### Layout Components
```typescript
// Main application layout
<AppLayout>
  <Header>
    <Logo />
    <UserMenu />
    <NotificationCenter />
  </Header>
  <BottomNavigation /> // Primary mobile navigation
  <MainContent>
    {children}
  </MainContent>
</AppLayout>

// Dashboard action grid
<ActionGrid cols={2} rows={3}>
  <ActionCard title="Marketing" icon="megaphone" />
  <ActionCard title="Properties" icon="home" />
  <ActionCard title="Clients" icon="users" />
  <ActionCard title="Analytics" icon="chart" />
  <ActionCard title="Voice Chat" icon="microphone" />
  <ActionCard title="Settings" icon="cog" />
</ActionGrid>
```

## Data Flow & State Management

### State Architecture (Zustand)

```typescript
// Authentication Store
interface AuthStore {
  user: User | null
  isAuthenticated: boolean
  token: string | null
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

// AI Conversation Store  
interface AIStore {
  conversations: Conversation[]
  currentConversation: string | null
  isProcessing: boolean
  streamingResponse: string
  sendMessage: (message: string) => Promise<void>
  clearConversation: () => void
}

// Voice Interface Store
interface VoiceStore {
  isRecording: boolean
  audioLevel: number
  recordingTime: number
  transcript: string
  startRecording: () => void
  stopRecording: () => void
  clearTranscript: () => void
}
```

### Data Flow Patterns

#### Voice → AI → Action Flow
```
1. User activates voice interface
   ↓
2. Audio captured and transcribed (Web Speech API)
   ↓
3. Transcript sent to AI service
   ↓
4. AI processes request and streams response
   ↓
5. Response displayed in real-time
   ↓
6. Action buttons presented for user confirmation
   ↓
7. User approves/modifies/rejects AI output
```

#### Real-time Updates Flow
```
1. WebSocket connection established on app load
   ↓
2. Backend sends updates (AI processing status, notifications)
   ↓
3. Frontend receives and updates relevant stores
   ↓
4. Components react to store changes
   ↓
5. UI updates reflect current state
```

## Routing Map

### Route Structure
```typescript
const routes = [
  // Public routes
  { path: "/login", component: LoginView },
  { path: "/register", component: RegisterView },
  
  // Protected routes (require authentication)
  { 
    path: "/", 
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: "/marketing",
    component: MarketingView,
    meta: { requiresAuth: true }
  },
  {
    path: "/properties",
    component: PropertiesView,
    meta: { requiresAuth: true }
  },
  {
    path: "/clients",
    component: ClientsView,
    meta: { requiresAuth: true }
  },
  {
    path: "/chat",
    component: AIChatView,
    meta: { requiresAuth: true }
  },
  {
    path: "/settings",
    component: SettingsView,
    meta: { requiresAuth: true }
  }
]
```

### Navigation Patterns

#### Primary Navigation (Bottom Navigation Bar)
- Dashboard (home icon)
- Marketing (megaphone icon)
- Properties (home icon)
- Clients (users icon) 
- Chat (message icon)

#### Secondary Navigation (Contextual)
- Back buttons with left arrow
- Action-specific navigation within workflows
- Breadcrumbs for deep navigation paths

## Pending Integrations

### Backend API Integration
- **Status:** Architecture defined, implementation pending
- **Endpoints:** 
  - `/api/v1/auth/*` - Authentication
  - `/api/v1/properties/*` - Property management
  - `/api/v1/clients/*` - Client management  
  - `/api/chat/*` - AI chat functionality
  - `/api/v1/marketing/*` - Marketing automation
- **Authentication:** JWT tokens with automatic refresh
- **Error Handling:** Centralized error handling with user-friendly messages

### Voice Services Integration
- **Status:** Architecture defined, implementation pending
- **Primary:** Web Speech API for voice recognition
- **Fallback:** Text input with visual voice activation
- **Processing:** Real-time transcript display with confidence indicators
- **Browser Support:** Chrome (primary), Firefox, Safari (limited), Edge

### AI Services Integration  
- **Status:** Backend ready, frontend integration pending
- **Features:**
  - Real-time streaming responses
  - Context-aware conversations
  - Multi-turn dialogue support
  - Content generation workflows
- **WebSocket:** Real-time AI response streaming
- **Caching:** Response caching for improved performance

### Real Estate Specific Integrations
- **Status:** Planned for Phase 3
- **MLS Integration:** Property data feeds
- **Document Generation:** Automated listing descriptions, marketing materials
- **CRM Integration:** Client management and nurturing workflows
- **Analytics:** Performance tracking and reporting

### Third-Party Services
- **Status:** Planning phase
- **Planned Integrations:**
  - Email marketing platforms
  - Social media scheduling
  - Document storage (cloud providers)
  - Payment processing (for premium features)
  - Analytics and tracking

## Performance Considerations

### React 19 Optimizations
- **Concurrent Rendering:** For smooth AI response streaming
- **Suspense:** For code splitting and lazy loading
- **Server Components:** For SEO-critical pages (if SSR needed)
- **Automatic Batching:** Improved state update performance

### Voice Interface Performance
- **Audio Processing:** Efficient audio level monitoring
- **Transcript Streaming:** Real-time display without blocking UI
- **Fallback Performance:** Instant text input when voice fails

### State Management Performance
- **Selective Subscriptions:** Components only subscribe to needed state
- **Optimistic Updates:** Immediate UI feedback with rollback capability
- **Caching Strategy:** Intelligent caching of AI responses and user data

## Accessibility Considerations

### Voice Interface Accessibility
- **Visual Indicators:** Clear visual feedback for voice states
- **Keyboard Navigation:** Full voice interface accessible via keyboard
- **Screen Reader Support:** Proper ARIA labels and announcements
- **Fallback Methods:** Always provide text alternatives

### General Accessibility
- **Color Contrast:** WCAG AA compliant color schemes
- **Focus Management:** Clear focus indicators and logical tab order
- **Semantic HTML:** Proper heading structure and landmarks
- **Responsive Design:** Accessible across all device sizes

## Testing Strategy

### Component Testing
- **Unit Tests:** Individual component functionality
- **Integration Tests:** Component interaction testing  
- **Visual Regression:** Screenshot comparison testing
- **Accessibility Tests:** Automated a11y testing

### Voice Interface Testing
- **Mock Audio:** Simulated voice input for consistent testing
- **Cross-Browser:** Voice API compatibility testing
- **Fallback Testing:** Text input fallback scenarios
- **Performance Testing:** Audio processing performance

### AI Integration Testing  
- **Mock Responses:** Predictable AI responses for testing
- **Streaming Tests:** Real-time response display testing
- **Error Scenarios:** Network failures and API errors
- **State Synchronization:** Frontend-backend state consistency

This architecture provides a solid foundation for the React 19 rebuild while maintaining flexibility for future enhancements and integrations.