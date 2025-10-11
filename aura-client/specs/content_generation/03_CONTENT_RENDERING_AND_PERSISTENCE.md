# Content Rendering and Persistence Architecture v3.1

## Overview

This document describes the content rendering and persistence system that provides interactive, persistent viewing of AI-generated content (CMA reports, pitch decks, social posts, etc.) in the Aura frontend.

## Architecture Components

### 1. Content Storage (commandStore.ts)

The `commandStore` has been extended with a `generatedContent` collection that persists content data locally.

#### Data Structures

```typescript
export interface GeneratedContent {
  id: string;
  taskId: string;
  type: ContentType;
  title: string;
  data: CMAData | PitchDeckData | Record<string, any>;
  generatedAt: string;
  updatedAt?: string;
}

export interface CMAData {
  property: {
    address: string;
    sqft?: number;
    bedrooms?: number;
    bathrooms?: number;
    yearBuilt?: number;
    lotSize?: string;
    type?: string;
  };
  marketAnalysis: {
    avgPrice: number;
    medianPrice: number;
    pricePerSqft: number;
    marketTrend: 'up' | 'down' | 'stable';
    daysOnMarket: number;
    inventory: number;
  };
  comparables: Array<{
    address: string;
    price: number;
    sqft: number;
    bedrooms: number;
    bathrooms: number;
    soldDate: string;
    distance: number;
    pricePerSqft: number;
    adjustedPrice?: number;
    adjustments?: Record<string, number>;
  }>;
  valuation: {
    estimatedValue: number;
    confidenceRange: { min: number; max: number };
    methodology: string[];
  };
  insights: string[];
  disclaimers: string[];
  generatedAt: string;
  reportId: string;
}

export interface PitchDeckData {
  id: string;
  title: string;
  property: {
    address: string;
    type: 'residential' | 'commercial' | 'mixed';
    sqft?: number;
    lotSize?: string;
    yearBuilt?: number;
  };
  slides: Array<{
    id: string;
    type: 'title' | 'property-overview' | 'market-analysis' | 'financial-projections' | 'investment-highlights' | 'neighborhood' | 'conclusion' | 'custom';
    title: string;
    content: {
      text?: string;
      bullets?: string[];
      data?: Record<string, any>;
      charts?: Array<{
        type: 'bar' | 'line' | 'pie' | 'area';
        title: string;
        data: any[];
      }>;
      images?: Array<{
        url: string;
        alt: string;
        caption?: string;
      }>;
    };
    notes?: string;
  }>;
  theme: {
    primaryColor: string;
    accentColor: string;
    fontFamily: string;
  };
  generatedAt: string;
}
```

#### Store Methods

- `saveGeneratedContent(content)` - Saves content and persists to localStorage
- `getGeneratedContent(taskId)` - Retrieves content by task ID
- `removeGeneratedContent(taskId)` - Removes content from store
- `updateGeneratedContent(taskId, updates)` - Updates existing content
- `listContentByType(type)` - Lists all content of specific type

### 2. Content Generation Flow

#### Template Orchestrator Integration

The `templateOrchestrator` generates structured content that matches the store schemas:

```typescript
// CMA Report Generation
case 'CMA_REPORT':
  return {
    structured: {
      property: { ... },
      marketAnalysis: { ... },
      comparables: [ ... ],
      valuation: { ... },
      insights: [ ... ],
      disclaimers: [ ... ]
    }
  };
```

#### Persistence Integration

Content is automatically saved to the store when generation completes in the Command Center:

```typescript
// Handle content generation results
if (result.contentGeneration?.success && result.contentGeneration.content) {
  const { saveGeneratedContent } = useCommandStore.getState();
  
  const storeContent = {
    taskId: requestId,
    type: result.contentGeneration.content.type,
    title: result.contentGeneration.content.title,
    data: result.contentGeneration.content.content.structured
  };
  
  const savedId = saveGeneratedContent(storeContent);
}
```

### 3. Content Viewers

#### CMAReport.tsx

Full-page CMA report viewer with:
- TaskId-based routing (`/cma/:taskId`)
- Data loading from commandStore
- Professional report layout with sections:
  - Executive Summary
  - Market Overview with key metrics
  - Comparable Properties table
  - Key Market Insights
  - Recommendations
- Export functionality (PDF, HTML)
- Share capabilities
- Error handling and loading states

#### DeckBuilder.tsx

Interactive pitch deck viewer with:
- TaskId-based routing (`/deck/:taskId`)
- Data loading from commandStore
- Multiple view modes:
  - Grid view (all slides overview)
  - Single slide view with navigation
  - Full-screen presentation mode
- Slide navigation with keyboard controls
- Export functionality (PDF, HTML)
- Share capabilities

### 4. Content Preview Integration

#### Requests Page Enhancement

The Requests page now shows:
- Content availability badges for completed tasks
- Content preview cards with:
  - Content type icons
  - Brief descriptions
  - "View Content" buttons
- Direct routing to appropriate viewers
- Support for opening content in new tabs

```typescript
const getContentPreview = (taskId: string, type: RequestType) => {
  const content = getGeneratedContent(taskId);
  if (!content) return null;

  switch (type) {
    case 'CMA_REPORT':
      const cmaData = content.data as CMAData;
      return {
        title: 'CMA Report',
        description: `Analysis for ${cmaData?.property?.address} with ${cmaData?.comparables?.length || 0} comparables`,
        badge: 'CMA'
      };
    // ... other types
  }
};
```

### 5. Routing Configuration

New routes added for content viewers:

```typescript
<Route path="/cma/:id" element={<CMAReport />} />
<Route path="/deck/:id" element={<DeckBuilder />} />
```

## Data Flow

### Content Generation to Persistence

1. **User Input** → Command Center receives voice/text command
2. **Intent Detection** → Orchestrator routes to Template Orchestrator
3. **Content Generation** → Template Orchestrator generates structured content
4. **Persistence** → Command Center saves content to store using task ID
5. **UI Update** → Requests page shows content available badge

### Content Viewing

1. **User Navigation** → User clicks "View Content" or navigates to `/cma/:taskId`
2. **Data Loading** → Viewer component loads content from store by task ID
3. **Rendering** → Full content rendered with proper UI components
4. **Interaction** → User can export, share, navigate through content

## Error Handling

### Content Loading
- Graceful fallback when content not found
- Clear error messages with navigation options
- Loading states during data retrieval

### Data Validation
- Type checking for content data structures
- Fallback values for missing fields
- Backward compatibility with legacy data

## Performance Considerations

### Storage
- Content persisted in localStorage for offline access
- Automatic cleanup of old content (configurable)
- Compression for large datasets

### Rendering
- Lazy loading of content sections
- Virtualization for large data sets (comparables, slides)
- Optimized re-rendering with React optimization patterns

## Future Enhancements

### Version 4.0 Roadmap
1. **Content Versioning** - Track content changes and history
2. **Collaborative Editing** - Allow content modification and annotation
3. **Advanced Export** - More export formats and customization
4. **Content Analytics** - Track content usage and engagement
5. **Real-time Updates** - Live content updates from backend
6. **Content Templates** - Customizable content generation templates

### Scalability
- Move from localStorage to IndexedDB for larger datasets
- Implement content synchronization with backend
- Add content caching strategies
- Support for offline content creation

## Integration Points

### Backend APIs
- Content generation endpoints return structured JSON matching schemas
- Export endpoints handle PDF/HTML generation
- Content persistence APIs for multi-device sync

### UI Components
- Reusable content preview cards
- Shared export/share functionality
- Consistent loading and error states

## Testing Strategy

### Unit Tests
- Store methods functionality
- Data transformation logic
- Component rendering with mock data

### Integration Tests
- End-to-end content generation flow
- Cross-component navigation
- Export functionality

### Performance Tests
- Large dataset rendering
- Memory usage optimization
- Storage performance

---

*This document describes the v3.1 implementation of content rendering and persistence. For implementation details, see the respective component files and store methods.*