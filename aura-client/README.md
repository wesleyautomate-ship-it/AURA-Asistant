# AURA Client - AI-Powered Real Estate Assistant Frontend

> **React 19 + TypeScript** | Modern responsive web app with unified intelligence pipeline

## 🌟 **Current Status: v3.4 - Unified Intelligence Architecture**

✅ **Production Ready Features:**
- **CommandCenter**: AI-powered voice & text interface with mock transcription support
- **Unified Intelligence API**: Direct backend integration via `/api/v1/intelligence/*`
- **Real-time Progress Tracking**: SSE streaming with polling fallback
- **Intelligent Follow-ups**: AI-suggested workflow chains with visual relationship tracking
- **Content Management**: Multi-format content generation (CMA, Pitch Decks, Social Posts, Market Reports)
- **Mobile-First Design**: Responsive interface with bottom navigation and floating action button
- **Cross-Tab Session Management**: Unified session handling with mic lock coordination

🎭 **Development Features:**
- **Mock Transcription Mode**: 10+ realistic prompts for rapid development (`VITE_AURA_MOCK_MODE=true`)
- **Error Recovery**: Graceful fallbacks and retry mechanisms
- **TypeScript Safety**: Full type coverage for intelligence API and content schemas

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server (with mock mode)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Development server:** [http://localhost:3000](http://localhost:3000)  
**Backend integration:** [http://localhost:8000](http://localhost:8000)

## 📦 Tech Stack

### **Core Framework**
- **React 19** - Latest React with concurrent features and improved performance
- **TypeScript 5.2+** - Full type safety throughout the application
- **Vite 5.0+** - Lightning-fast development server and build tool

### **State Management & Data**
- **Zustand 5.0** - Lightweight, flexible state management with persistence
- **React Query 5.90** - Server state management, caching, and synchronization
- **Native Fetch API** - HTTP client with error handling and retry logic

### **UI & Styling**
- **TailwindCSS 4.1** - Utility-first CSS framework with custom design system
- **Framer Motion 12.23** - Production-ready animations and gestures
- **Lucide React 0.545** - Consistent icon library with 1000+ icons

### **Routing & Navigation**
- **React Router DOM 7.9** - Declarative routing with nested layouts
- **React Swipeable 7.0** - Touch gesture support for mobile interactions

## 📁 Project Architecture

```
src/
├── components/
│   ├── layout/         # Global layout components
│   │   ├── BottomNav.tsx   # Mobile navigation
│   │   └── GlobalHeader.tsx # Desktop header
│   ├── report/         # Report generation components
│   │   ├── ExportToolbar.tsx
│   │   ├── ReportSection.tsx
│   │   └── SkeletonLoader.tsx
│   └── ui/             # Core UI components
│       ├── CommandCenter.tsx      # 🧠 AI command interface
│       ├── CommandFab.tsx         # Floating action button
│       ├── BottomDock.tsx         # Mobile dock interface
│       ├── FollowUpCard.tsx       # AI follow-up suggestions
│       ├── ProgressTracker.tsx    # Real-time progress display
│       ├── RequestFeed.tsx        # Task request feed
│       └── ErrorDialog.tsx        # Error handling UI
│
├── pages/              # Application pages
│   ├── Dashboard.tsx       # Main dashboard
│   ├── Tasks.tsx           # Task management
│   ├── Analytics.tsx       # Analytics dashboard  
│   ├── CMAReport.tsx       # CMA report viewer
│   ├── DeckBuilder.tsx     # Pitch deck builder
│   └── ContentViewer.tsx   # Universal content viewer
│
├── services/           # API and business logic
│   ├── api/
│   │   └── intelligenceApi.ts  # 🧠 Unified intelligence API client
│   ├── intelligence/       # Intelligence services
│   │   ├── contentIntelligence.ts
│   │   └── memoryService.ts
│   ├── api.ts              # Legacy API (being phased out)
│   ├── followupAgent.ts    # AI follow-up generation
│   └── contextEnrichment.ts # Context enhancement
│
├── store/              # Global state management
│   └── commandStore.ts     # 🧠 Unified command & session store
│
├── types/              # TypeScript definitions
│   ├── intelligence.ts     # Intelligence API types
│   └── contentSchemas.ts   # Content structure schemas
│
├── mocks/              # Development mocks
│   └── transcriptionPrompts.ts # 🎭 Mock voice prompts
│
├── test/               # Integration tests
│   └── commandCenterIntegrationTest.ts
│
├── config/             # Application configuration
│   └── taskLifecycle.ts    # Task management rules
│
├── routes/             # Routing setup
│   └── index.tsx           # Route definitions
│
├── App.tsx             # 🏠 Root application component
├── main.tsx            # Application entry point
└── index.css           # Global styles & Tailwind imports
```

## 🎨 Design System

### Colors
- **Primary**: `#3B82F6` (Blue) - Trust, professionalism
- **Secondary**: `#10B981` (Green) - Growth, success
- **Accent**: `#F59E0B` (Orange) - Energy, action
- **Background**: `#F9FAFB` (Gray) - Clean, modern
- **Text**: `#111827` (Dark Gray) - Readability

### Spacing
- Grid system: 4px, 8px, 16px, 24px
- Card padding: 16px
- Border radius: 8px, 12px, 16px

### Typography
- Font family: Inter, system-ui, sans-serif
- Headers: Bold, clean sans-serif
- Body: Readable, medium weight

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Configuration

Create `.env.development` for local development:

```env
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Development Features
VITE_AURA_MOCK_MODE=true          # Enable mock transcription (10+ realistic prompts)
VITE_ENABLE_DEBUG_LOGS=true       # Enable detailed console logging
VITE_ENABLE_PERFORMANCE_MONITORING=true # Track performance metrics

# Feature Flags
VITE_ENABLE_FOLLOW_UP_SUGGESTIONS=true  # AI follow-up cards
VITE_ENABLE_PROGRESS_STREAMING=true     # Real-time progress updates
VITE_ENABLE_ERROR_RECOVERY=true         # Automatic error recovery
```

**Production Environment (`.env.production`):**
```env
VITE_API_BASE_URL=https://your-backend-domain.com
VITE_AURA_MOCK_MODE=false         # Always disable in production
VITE_ENABLE_DEBUG_LOGS=false      # Disable debug logs
```

## 🧠 **CommandCenter: AI Interface Core**

The CommandCenter is the heart of AURA's AI interaction system, providing both voice and text interfaces for content generation.

### **Features**
- **Dual Mode Interface**: Voice recording with real-time amplitude visualization + Text input
- **Mock Transcription Support**: 10+ realistic prompts for development (`VITE_AURA_MOCK_MODE=true`)
- **Real-time Progress Tracking**: SSE streaming + polling fallback
- **Intelligent Follow-ups**: AI-suggested next steps with workflow chains
- **Error Recovery**: Graceful fallbacks and retry mechanisms
- **Cross-tab Session Management**: Mic lock coordination and session persistence

### **Voice Mode Workflow**
```typescript
// 1. User clicks microphone button
setPhase('listening') 

// 2. Real-time audio visualization
getUserMedia() → analyser.getByteTimeDomainData() → setAmplitude()

// 3. Transcription (mock or real)
if (VITE_AURA_MOCK_MODE) {
  simulateMockTranscription() // 1-1.5s realistic delay
} else {
  intelligenceApi.transcribe(audioBlob) // Backend STT
}

// 4. Content generation
intelligenceApi.generateContent({
  user_input: transcript,
  content_type: 'CMA_REPORT' | 'PITCH_DECK' | 'SOCIAL_POST',
  priority: 'normal' | 'high'
})

// 5. Progress streaming
for await (const progress of intelligenceApi.streamTaskProgress(taskId)) {
  setPipelineProgress(progress.progress)
  setPipelineStep(progress.current_step)
}
```

### **Text Mode Workflow**
```typescript
// Direct text input → same intelligence pipeline
const handleTextSubmit = async (userInput: string) => {
  const request: ContentGenerationRequest = {
    user_input: userInput,
    content_type: selectedContentType,
    memory_enhanced: true,
    priority: 'normal'
  }
  
  const response = await intelligenceApi.generateContent(request)
  startProgressPolling(response.task_id)
}
```

## 🔗 **Intelligence API Integration**

AURA uses a unified intelligence API that replaces all previous mock orchestration with real backend calls.

### **Core API Client (`intelligenceApi.ts`)**
```typescript
class IntelligenceApiClient {
  // Content generation
  async generateContent(request: ContentGenerationRequest): Promise<ContentGenerationResponse>
  
  // Progress tracking
  async getTaskStatus(taskId: string): Promise<TaskStatusResponse>
  async *streamTaskProgress(taskId: string): AsyncGenerator<ProgressEventData>
  async *pollTaskProgress(taskId: string): AsyncGenerator<ProgressEventData>
  
  // Transcription with mock support
  async transcribe(audioBlob?: Blob): Promise<string>
  
  // Content management
  async getContent(contentId: string): Promise<ContentRetrievalResponse>
  async refineContent(contentId: string, request: RefinementRequest): Promise<RefinementResponse>
  
  // High-level workflows
  async generateContentWithProgress(request, onProgress): Promise<IntelligenceContent>
  async transcribeAndGenerate(audioFile, options): Promise<IntelligenceContent>
}
```

### **API Endpoints**
```
POST   /api/v1/intelligence/generate     # Start content generation
GET    /api/v1/intelligence/status/{id}  # Get task status
GET    /api/v1/intelligence/stream/{id}  # SSE progress stream
POST   /api/v1/intelligence/transcribe   # Audio transcription
GET    /api/v1/intelligence/content/{id} # Retrieve generated content
POST   /api/v1/intelligence/refine/{id}  # Refine existing content
GET    /api/v1/intelligence/health       # Health check
```

### **Content Types Supported**
- `CMA_REPORT` - Comparative Market Analysis
- `PITCH_DECK` - Property investment presentation
- `SOCIAL_POST` - Social media content
- `MARKET_REPORT` - Market analysis and trends
- `GENERIC` - General-purpose content

## 📝 Development Guidelines

### **Component Standards**
1. **Functional components only** with React hooks
2. **Full TypeScript coverage** - strict mode enabled
3. **Mobile-first responsive design** - test on 320px+ viewports
4. **Tailwind utilities preferred** - avoid custom CSS
5. **Extract business logic** into custom hooks
6. **Component size limit** - max 300 lines per component
7. **Error boundaries** - wrap async operations
8. **Accessibility** - ARIA labels, keyboard navigation

## 🧪 **Testing Strategy**

### **Mock Transcription Testing**

Perfect for rapid development and consistent testing:

```javascript
// Browser console testing
const testMockTranscription = async () => {
  console.log('Testing mock transcription...')
  
  // 1. Enable mock mode
  localStorage.setItem('VITE_AURA_MOCK_MODE', 'true')
  
  // 2. Simulate voice input
  const mockPrompt = await window.intelligenceApi.transcribe()
  console.log('Mock prompt:', mockPrompt)
  
  // 3. Test content generation
  const response = await window.intelligenceApi.generateContent({
    user_input: mockPrompt,
    content_type: 'CMA_REPORT'
  })
  console.log('Generation response:', response)
}

// Run the test
testMockTranscription()
```

### **Integration Testing**

**CommandCenter Workflow Test:**
```bash
# 1. Start backend (ensure dev auth bypass enabled)
cd ../backend && python -m app.main

# 2. Start frontend with mock mode
echo "VITE_AURA_MOCK_MODE=true" > .env.development
npm run dev

# 3. Manual test checklist:
# ✅ CommandCenter opens without errors
# ✅ Voice mode shows orange mock indicator
# ✅ Mock transcription provides realistic prompts
# ✅ Content generation starts successfully
# ✅ Progress tracking shows real backend status
# ✅ Follow-up suggestions appear after completion
```

**API Integration Test:**
```typescript
// Available in: src/test/commandCenterIntegrationTest.ts
import { testCommandCenterIntegration } from './test/commandCenterIntegrationTest'

// Run comprehensive test suite
await testCommandCenterIntegration({
  testMockTranscription: true,
  testRealBackend: false, // Set to true when backend ready
  testFollowupGeneration: true,
  testProgressTracking: true
})
```

### **Quality Assurance**

```bash
# TypeScript checking
npm run lint

# Build verification
npm run build

# Preview production build
npm run preview

# Manual testing matrix
# - Desktop Chrome/Firefox/Safari
# - Mobile Chrome/Safari (iOS/Android)
# - Tablet responsive breakpoints
# - Voice input with/without microphone access
# - Network offline/online scenarios
```

## 🚀 **Deployment**

### **Production Build**
```bash
# 1. Set production environment
cp .env.production .env

# 2. Install dependencies
npm ci --only=production

# 3. Build application
npm run build

# 4. Verify build
ls -la dist/
npm run preview
```

### **Static Hosting (Recommended)**
```bash
# Vercel deployment
npx vercel --prod

# Netlify deployment  
npx netlify deploy --prod --dir=dist

# AWS S3 + CloudFront
aws s3 sync dist/ s3://your-bucket-name --delete
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

### **Docker Deployment**
```dockerfile
# Dockerfile
FROM node:19-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
# Build and run
docker build -t aura-client .
docker run -p 3000:80 aura-client
```

## 🔧 **Troubleshooting**

### **Common Issues**

**❌ CommandCenter Black Screen:**
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev

# Check browser console for undefined variable errors
# Ensure no legacy sync-related code remains
```

**❌ Mock Transcription Not Working:**
```bash
# Verify environment variable
echo $VITE_AURA_MOCK_MODE  # Should be 'true'

# Check file exists
ls -la src/mocks/transcriptionPrompts.ts

# Verify imports in CommandCenter.tsx
grep -n "simulateMockTranscription" src/components/ui/CommandCenter.tsx
```

**❌ Backend API Connection Failed:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Verify CORS settings
curl -H "Origin: http://localhost:3000" \  
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/v1/intelligence/generate

# Check development authentication bypass
curl -X POST "http://localhost:8000/api/v1/intelligence/generate" \
     -H "Content-Type: application/json" \
     -d '{"user_input":"test"}'
```

**❌ Build Failures:**
```bash
# Clear everything and reinstall
rm -rf node_modules package-lock.json dist
npm install
npm run build

# Check TypeScript errors
npx tsc --noEmit

# Verify environment variables in build
cat .env.production
```

### **Performance Optimization**

```bash
# Bundle analysis
npm run build -- --analyze

# Lighthouse audit
npm run preview
# Then run Lighthouse on http://localhost:4173

# Memory profiling
# Open Chrome DevTools > Memory tab
# Take heap snapshots during heavy CommandCenter usage
```

## 📚 **Documentation**

### **Current Status Documents**
- `FINAL_FIXES_COMPLETE.md` - Latest CommandCenter fixes and migration status
- `MOCK_TRANSCRIPTION_INTEGRATION_COMPLETE.md` - Mock transcription implementation
- `INTELLIGENCE_IMPLEMENTATION_SUMMARY.md` - Intelligence API integration
- `COMMAND_CENTER_MIGRATION_COMPLETE.md` - v3.3 to v3.4 migration summary

### **Architecture Documents**
- `AURA_INTELLIGENCE_ARCHITECTURE_AUDIT_REPORT.md` - System architecture overview
- `V33-MIGRATION-COMPLETE.md` - Historical migration details
- `MOBILE_REDESIGN_SUMMARY.md` - Mobile-first design decisions

### **API Documentation**
- `src/services/api/intelligenceApi.ts` - Comprehensive API client with inline docs
- `src/types/intelligence.ts` - TypeScript type definitions and schemas
- Backend OpenAPI docs: `http://localhost:8000/docs` (when backend running)

## 🤝 **Contributing**

### **Development Workflow**

1. **Setup Development Environment**
   ```bash
   git clone <repository>
   cd aura-client
   npm install
   cp .env.development .env
   ```

2. **Follow Code Standards**
   - Use TypeScript for all new code
   - Follow mobile-first responsive design
   - Add comprehensive error handling
   - Write inline documentation for complex logic
   - Test on multiple devices/browsers

3. **Before Committing**
   ```bash
   npm run lint        # Fix TypeScript issues
   npm run build       # Verify production build
   npm run preview     # Test production bundle
   ```

4. **Testing Requirements**
   - Test CommandCenter voice & text modes
   - Verify mock transcription works
   - Test responsive design (320px - 1920px)
   - Check accessibility (keyboard navigation, screen readers)
   - Validate error handling and recovery

5. **Update Documentation**
   - Update this README.md if adding features
   - Add inline code documentation
   - Create/update status documents for major changes

### **Project Status Tracking**

The project uses detailed status documents to track implementation progress:
- ✅ **CommandCenter v3.4**: Fully migrated to unified intelligence API
- ✅ **Mock Transcription**: 10+ realistic prompts for development
- ✅ **Progress Tracking**: Real-time SSE streaming + polling fallback
- ✅ **Follow-up System**: AI-suggested workflow chains
- ✅ **Mobile Responsive**: Optimized for all screen sizes
- ✅ **TypeScript Coverage**: 100% type safety
- ✅ **Error Recovery**: Graceful fallbacks and retry mechanisms

**Next Priorities:**
- 🔄 Authentication integration (JWT token management)
- 🔄 Offline support and progressive web app features
- 🔄 Advanced content refinement and editing tools
- 🔄 Real-time collaboration features

## 📄 **License**

**Proprietary Software - AURA Real Estate Assistant**  
Copyright © 2024 RealtorProAI. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or modification is strictly prohibited.
