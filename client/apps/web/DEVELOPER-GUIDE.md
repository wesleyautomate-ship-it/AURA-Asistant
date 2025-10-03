# Developer Guide - Unified Frontend

## 🚀 **Getting Started**

### **Quick Setup**
```bash
# Clone and navigate
cd frontend/

# Install dependencies
npm install

# Start development
npm run dev
# → Opens http://localhost:3000
```

---

## 📁 **Project Structure**

```
frontend/src/
├── components/      # UI Components
│   ├── Button.tsx           # Web version (Tailwind CSS)
│   ├── Button.mobile.tsx    # Mobile version (React Native)
│   └── ...
├── screens/         # Full-screen views (mobile-first)
│   ├── DashboardScreen.tsx
│   ├── ChatScreen.tsx
│   └── ...
├── services/        # API & Business Logic
│   ├── api.ts              # HTTP client
│   ├── audioService.ts     # Audio handling
│   └── ...
├── store/          # Global State (Zustand)
├── theme/          # Design System
├── assets/         # Static files
└── mock-data/      # Development data
```

---

## 🧩 **Component Development**

### **Creating Platform-Specific Components**

**Web Component (`Button.tsx`)**
```tsx
import React from 'react';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary';
}

export default function Button({ title, onPress, variant = 'primary' }: ButtonProps) {
  return (
    <button
      onClick={onPress}
      className={`px-4 py-2 rounded-lg font-semibold ${
        variant === 'primary' 
          ? 'bg-blue-500 text-white hover:bg-blue-600' 
          : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
      }`}
    >
      {title}
    </button>
  );
}
```

**Mobile Component (`Button.mobile.tsx`)**
```tsx
import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary';
}

export default function Button({ title, onPress, variant = 'primary' }: ButtonProps) {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={[styles.button, variant === 'primary' ? styles.primary : styles.secondary]}
    >
      <Text style={[styles.text, variant === 'primary' ? styles.primaryText : styles.secondaryText]}>
        {title}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  primary: {
    backgroundColor: '#3B82F6',
  },
  secondary: {
    backgroundColor: '#E5E7EB',
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
  },
  primaryText: {
    color: '#FFFFFF',
  },
  secondaryText: {
    color: '#374151',
  },
});
```

---

## 📦 **Import System**

### **Path Aliases**
```typescript
// ✅ Use path aliases
import Button from '@components/Button';          // Auto-resolves platform
import DashboardScreen from '@screens/Dashboard'; // Mobile screens
import apiService from '@services/api';           // Shared services
import { colors } from '@theme/colors';           // Design tokens

// ❌ Avoid relative imports
import Button from '../../../components/Button';
```

### **Platform Resolution**
Vite automatically resolves components in this order:
1. `.web.tsx` (web-specific)
2. `.mobile.tsx` (mobile-specific) 
3. `.tsx` (universal)

---

## 🎨 **Styling Guide**

### **Web Components - Tailwind CSS**
```tsx
// Use Tailwind utility classes
<div className="bg-white shadow-lg rounded-xl p-6 hover:shadow-xl transition-shadow">
  <h2 className="text-xl font-bold text-gray-900 mb-4">Title</h2>
  <p className="text-gray-600 leading-relaxed">Content</p>
</div>
```

### **Mobile Components - StyleSheet**
```tsx
import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    borderRadius: 12,
    padding: 24,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 16,
  },
  text: {
    fontSize: 16,
    color: '#6B7280',
    lineHeight: 24,
  },
});
```

---

## 🔌 **Services & API**

### **API Service Pattern**
```typescript
// services/api.ts
class ApiService {
  private baseURL = process.env.VITE_API_URL || 'http://localhost:8000';

  async getProperties() {
    const response = await fetch(`${this.baseURL}/api/properties`);
    return response.json();
  }

  async createProperty(data: PropertyData) {
    const response = await fetch(`${this.baseURL}/api/properties`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }
}

export const apiService = new ApiService();
```

### **Using Services in Components**
```tsx
import { useEffect, useState } from 'react';
import { apiService } from '@services/api';

export default function PropertyList() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiService.getProperties()
      .then(setProperties)
      .finally(() => setLoading(false));
  }, []);

  // ... render logic
}
```

---

## 🏪 **State Management**

### **Zustand Store Example**
```typescript
// store/propertyStore.ts
import { create } from 'zustand';

interface PropertyState {
  properties: Property[];
  selectedProperty: Property | null;
  setProperties: (properties: Property[]) => void;
  selectProperty: (id: string) => void;
}

export const usePropertyStore = create<PropertyState>((set, get) => ({
  properties: [],
  selectedProperty: null,
  
  setProperties: (properties) => set({ properties }),
  
  selectProperty: (id) => {
    const property = get().properties.find(p => p.id === id);
    set({ selectedProperty: property || null });
  },
}));
```

### **Using Store in Components**
```tsx
import { usePropertyStore } from '@store/propertyStore';

export default function PropertyCard({ property }: { property: Property }) {
  const selectProperty = usePropertyStore(state => state.selectProperty);
  
  return (
    <div onClick={() => selectProperty(property.id)}>
      <h3>{property.title}</h3>
      <p>{property.price}</p>
    </div>
  );
}
```

---

## 🔧 **Development Workflow**

### **Available Scripts**
```bash
npm run dev          # Development server with HMR
npm run build        # Production build
npm run preview      # Preview production build
npm run test:e2e     # Run Playwright tests
```

### **Type Checking**
```bash
npx tsc --noEmit                # Full type check
npx tsc --noEmit --skipLibCheck # Skip library checks
```

### **Platform Testing**
- **Web**: Development server runs web components automatically
- **Mobile**: Components with `.mobile.tsx` variants are resolved
- **Universal**: Components without platform-specific variants work on both

---

## 🐛 **Common Issues**

### **Import Errors**
```typescript
// ❌ Wrong - direct react-native import
import { View } from 'react-native';

// ✅ Correct - let Vite resolve via alias
import { View } from 'react-native';  // Works via vite.config.ts alias
```

### **TypeScript Errors**
```bash
# If you see react-native type errors:
npm install --save-dev @types/react-native

# If path aliases don't work:
# Check tsconfig.json paths configuration
```

### **Build Errors**
```typescript
// ❌ Platform-specific code in universal components
Platform.OS === 'web' // Don't do this in .tsx files

// ✅ Use platform-specific files instead
// Button.tsx (web) and Button.mobile.tsx (mobile)
```

---

## 📋 **Best Practices**

### **Component Organization**
- Use platform-specific files for different styling approaches
- Keep business logic in shared services
- Use TypeScript interfaces for props consistency

### **Naming Conventions**
- Components: `PascalCase.tsx` / `PascalCase.mobile.tsx`
- Services: `camelCase.ts`
- Stores: `camelCaseStore.ts`
- Types: `PascalCase` interfaces

### **Performance**
- Use React.memo for expensive components
- Implement proper loading states
- Optimize images in assets/

---

## 🔗 **Useful Links**

- [React Native Web Docs](https://necolas.github.io/react-native-web/)
- [Vite Configuration](https://vitejs.dev/config/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand State Management](https://github.com/pmndrs/zustand)

---

**Happy Coding! 🚀**