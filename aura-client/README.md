# Aura Client - Frontend Application

> Modern React 19 frontend for the Aura Real Estate Assistant

## 🎯 **NEW in v2.9.4: Intelligent Follow-up & Linked Task Automation**

✨ **Aura now proactively suggests contextual next steps!** 
- Automatic follow-up generation after task completion
- Smart workflow chains (CMA → Social Posts → Marketing Campaigns)
- One-click accept/dismiss with seamless execution
- Visual task relationship tracking
- AI-powered confidence scoring

**Example Workflows:**
- Complete CMA → Suggests social media promotion
- Finish market report → Suggests property-specific analysis  
- Create social post → Suggests email marketing campaign

## 🚀 Quick Start

```bash
# Install dependencies (if not already done)
npm install --no-workspaces

# Start development server
npm run dev --no-workspaces

# Build for production
npm run build --no-workspaces

# Preview production build
npm run preview --no-workspaces
```

The app will be available at [http://localhost:3000](http://localhost:3000)

## 📦 Tech Stack

- **React 19** - Latest React with concurrent features
- **Vite** - Fast build tool and dev server
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Lucide Icons** - Beautiful icon library
- **Framer Motion** - Animation library
- **Axios** - HTTP client

## 📁 Project Structure

```
src/
├── components/     # Reusable UI components
│   ├── common/     # Base components (Button, Input, etc.)
│   ├── forms/      # Form-specific components
│   ├── layout/     # Layout components
│   ├── voice/      # Voice interface components
│   └── ai/         # AI interaction components
├── pages/          # Page-level components
├── layout/         # Layout wrappers
├── store/          # Zustand state stores
├── services/       # API services
├── hooks/          # Custom React hooks
├── routes/         # Routing configuration
├── App.tsx         # Main application component
├── main.tsx        # Entry point
└── index.css       # Global styles
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

### Environment Setup

Create a `.env.local` file for local development:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📝 Component Guidelines

1. **Use functional components** with hooks
2. **TypeScript for all new code** - strict mode enabled
3. **Follow mobile-first** responsive design
4. **Use Tailwind utilities** - avoid custom CSS when possible
5. **Extract reusable logic** into custom hooks
6. **Keep components small** and focused

## 🧪 Testing

### Follow-up System Testing

**Browser Console Testing:**
```javascript
// Load test script in browser console
const script = document.createElement('script');
script.src = '/test-followup.js';
document.head.appendChild(script);

// Run integration test
testAuraFollowUp();
```

**Manual Testing:**
1. Complete any task (CMA, Market Report, Social Post)
2. Wait for follow-up suggestion card to appear
3. Test accept/dismiss functionality
4. Verify linked task creation

**Unit Tests:**
```bash
# Run tests (when implemented)
npm run test

# TypeScript checking
npm run lint
```

## 📚 Documentation

- Main docs: `/docs/frontend-architecture.md`
- Build notes: `/docs/build-journal/BUILD_NOTES.md`
- Status: `/docs/build-journal/STATUS.md`
- Design rules: `/.claude/claude.md`

## 🤝 Contributing

1. Check the build journal for current status
2. Follow the design system guidelines
3. Update CHANGELOG.md with your changes
4. Test on mobile, tablet, and desktop

## 📄 License

Proprietary - Aura Real Estate Assistant
