<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Laura AI - Real Estate Assistant (Frontend)

> **Unified React + React Native Web Frontend**

This is the unified frontend for Laura AI Real Estate Assistant, combining web and mobile components in a single codebase using **React Native Web**.

Laura AI is an intelligent real estate assistant that helps agents with content generation, lead management, and workflow automation.

## 🏗️ Architecture

### **Unified Structure**
```
frontend/
├── src/
│   ├── components/          # Web components + .mobile.tsx variants
│   ├── screens/            # Mobile-first screens
│   ├── services/           # API & business logic (web + mobile)
│   ├── store/              # State management
│   ├── theme/              # Design tokens & styling
│   ├── assets/             # Images, fonts, etc.
│   └── mock-data/          # Development data
├── legacy/                 # Backup files from migration
└── tests/                  # E2E and component tests
```

### **Technology Stack**
- **React 18** - Web framework
- **React Native Web** - Cross-platform component system
- **TypeScript** - Type safety
- **Vite** - Fast build tool & dev server
- **Tailwind CSS** - Styling (web components)
- **StyleSheet** - React Native styling (mobile components)

## 🚀 Quick Start

**Prerequisites:** Node.js 18+

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Environment Setup:**
   - Copy `.env.example` to `.env.local`
   - Set your `GEMINI_API_KEY` in `.env.local`

3. **Start development server:**
   ```bash
   npm run dev
   ```
   
4. **Open in browser:**
   - Local: http://localhost:3000
   - Network: Will be displayed in terminal

## 📱 Component System

### **Platform-Specific Components**
The app uses a **platform-aware component system**:

- **Web components:** `Component.tsx` (Tailwind CSS + HTML)
- **Mobile components:** `Component.mobile.tsx` (React Native components)
- **Vite automatically resolves:** `.mobile.tsx` → `.tsx` based on platform

### **Import Aliases**
```typescript
import Button from '@components/Button';           // Auto-resolves platform
import DashboardScreen from '@screens/Dashboard';   // Mobile screens
import apiService from '@services/api';             // Shared services
import { theme } from '@theme';                      // Design tokens
```

## 🛠️ Development

### **Available Scripts**
```bash
npm run dev          # Start development server
npm run build        # Production build
npm run preview      # Preview production build
npm run test:e2e     # Run Playwright tests
```

### **Code Quality**
```bash
npx tsc --noEmit     # TypeScript type checking
npx tsc --noEmit --skipLibCheck  # Skip lib checking
```

## 🎨 Styling

### **Web Components (Tailwind)**
```tsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  Web styling with Tailwind
</div>
```

### **Mobile Components (StyleSheet)**
```tsx
import { View, Text, StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: { backgroundColor: '#3B82F6', padding: 16 }
});

<View style={styles.container}>
  <Text>Mobile styling with StyleSheet</Text>
</View>
```

## 📦 Project Structure Details

### **Key Directories**
- **`src/components/`** - Reusable UI components (web + mobile variants)
- **`src/screens/`** - Full-screen views (mobile-first approach)
- **`src/services/`** - API clients, business logic, utilities
- **`src/store/`** - Global state management (Zustand/Redux)
- **`src/theme/`** - Design system, colors, typography

### **Configuration Files**
- **`vite.config.ts`** - Vite bundler config + React Native Web alias
- **`tsconfig.json`** - TypeScript config + path aliases
- **`tailwind.config.js`** - Tailwind CSS configuration
- **`playwright.config.ts`** - E2E testing configuration

## 🔄 Migration Notes

This frontend was created by merging:
- **Web components** (originally in `frontend/`)
- **Mobile screens** (originally in `mobile/`)
- **Mockup components** (originally in `frontend mockup/`)

**Legacy files** are preserved in `frontend/legacy/` for reference.

## 🐛 Known Issues

- Some TypeScript type mismatches between web/mobile codebases (non-breaking)
- Expo dependencies in mobile code (unused in web build)

## 📚 Learn More

- [React Native Web Documentation](https://necolas.github.io/react-native-web/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
