# Pitch Deck Generator Specification v3.1

## Overview

The Investor Pitch Deck Generator transforms natural language commands into professionally structured, slide-based presentations for real estate investment opportunities. The system creates multi-slide decks with consistent visual hierarchy, following investor presentation best practices.

## System Architecture

```
User Input → Intent Parser → Template Orchestrator → Workflow API → Slide Generation → Deck Builder
     ↓              ↓               ↓                    ↓               ↓              ↓
"Create pitch    Pitch Deck    Content Type        Backend API     Structured      Interactive
 deck for        Intent &      Mapping &          /api/v1/decks/   Slide Data     Deck Editor +
 Palm            Context       Enrichment         generate                        Presentation
 Jumeirah"       Enhanced
```

## Input Processing Flow

### 1. User Input Examples

**Voice Commands:**
- "Create an investor pitch deck for Palm Jumeirah"
- "Generate presentation for luxury villa project in DIFC"
- "Build investment deck for Marina Walk development"

**Text Commands:**
- "Generate pitch deck Downtown Dubai luxury project"
- "Create investor presentation Business Bay commercial"
- "Build investment deck 5M AED villa development"

**Context-Aware Recognition:**
- Keywords: "pitch", "deck", "presentation", "investor", "investment"
- Intent markers: "create", "generate", "build", "make"
- Investment context: amounts, ROI, timeline mentions

### 2. Intent Detection & Classification

```typescript
interface PitchDeckIntent {
  type: 'PITCH_DECK';
  location: string;              // Required: "Palm Jumeirah"
  property_type?: string;        // Optional: "luxury", "commercial", "villa"
  investment_amount?: number;    // Optional: parsed from "5M AED"
  target_audience?: string;      // Optional: "investors", "partners"
  timeline?: string;            // Optional: "12_months", "24_months"
  confidence: number;           // 0.0-1.0
}
```

### 3. Context Enrichment Process

The system infers missing fields from:
- **Recent Property Tasks**: CMA reports, market analyses for same location
- **Investment Context**: Previous pitch decks, mentioned budgets/timelines
- **Market Intelligence**: Property type classifications, standard investment ranges
- **Presentation Patterns**: Common slide structures for property type/location

## Data Flow Diagram

```
┌──────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   User Command   │───▶│  Intent Parser   │───▶│ Template Orchestr.  │
│"Pitch deck Palm" │    │ + Context Enrich │    │  Slide Mapping      │
└──────────────────┘    └──────────────────┘    └─────────────────────┘
                                                            │
┌──────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Error Recovery  │◄───│   Workflow API   │◄───│  Payload Building   │
│ + Streaming AI   │    │ /decks/generate  │    │ + Field Validation  │
└──────────────────┘    └──────────────────┘    └─────────────────────┘
                                 │
┌──────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Deck Builder   │◄───│  Generated Deck  │◄───│   AI Processing     │
│ Grid/Single View │    │ Multi-slide JSON │    │ Investment Analysis │
└──────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Generated Content Structure

### Pitch Deck Schema

```typescript
interface PitchDeck {
  slides: Array<{
    id?: number;
    title: string;
    subtitle?: string;
    content: string[];
    type: 'title' | 'content' | 'data' | 'closing';
    layout?: 'center' | 'left' | 'split';
  }>;
  metadata: {
    title: string;
    location: string;
    investment_amount?: number;
    target_audience: string;
    created_date: string;
    estimated_duration: string; // "8-10 minutes"
  };
}
```

### Standard Slide Structure

```typescript
interface StandardPitchSlides {
  1: TitleSlide;           // Investment opportunity overview
  2: OpportunitySlide;     // Market problem/opportunity
  3: LocationSlide;        // Location advantages & analysis
  4: ProjectSlide;         // Property details & specifications
  5: MarketSlide;          // Market analysis & trends
  6: FinancialSlide;       // Investment highlights & ROI
  7: TimelineSlide;        // Development/investment timeline
  8: NextStepsSlide;       // Call to action & contact
}
```

### Example Output

```json
{
  "slides": [
    {
      "id": 1,
      "title": "Investment Opportunity",
      "subtitle": "Palm Jumeirah Premium Development",
      "content": [
        "Prime waterfront location with panoramic views",
        "High-end finishes and world-class amenities", 
        "Strong rental demand and capital appreciation potential"
      ],
      "type": "title",
      "layout": "center"
    },
    {
      "id": 2,
      "title": "Market Opportunity",
      "subtitle": "Growing Demand in Premium Segment",
      "content": [
        "15% YoY price appreciation in luxury properties",
        "85% occupancy rates in premium developments",
        "Limited new supply pipeline in Palm Jumeirah",
        "Government initiatives boosting foreign investment"
      ],
      "type": "content",
      "layout": "left"
    },
    {
      "id": 3,
      "title": "Financial Highlights",
      "subtitle": "Strong Investment Returns",
      "content": [
        "7.5% projected rental yield",
        "AED 5.2M total investment",
        "12% IRR over 5-year hold period",
        "30% equity appreciation potential"
      ],
      "type": "data",
      "layout": "split"
    }
  ],
  "metadata": {
    "title": "Palm Jumeirah Investment Opportunity",
    "location": "Palm Jumeirah",
    "investment_amount": 5200000,
    "target_audience": "investors",
    "created_date": "2024-10-09",
    "estimated_duration": "8-10 minutes"
  }
}
```

## Frontend Integration

### Component Hierarchy

```
DeckBuilder Page (Full Editor)
├── Header (Present, Share, Export)
├── View Mode Toggle (Grid/Single/Presentation)
├── Slide Content
│   ├── Grid View (Slide Thumbnails)
│   ├── Single View (Current Slide + Navigation)
│   └── Presentation Mode (Fullscreen)
├── Slide Navigation
└── Deck Overview Panel

SlideCard Component (Individual Slides)
├── Slide Type Styling (Title/Content/Data/Closing)
├── Content Rendering (Title + Subtitle + Bullet Points)
├── Navigation Controls (Previous/Next)
└── Visual Indicators (Slide Number, Progress)
```

### Navigation Flow

1. **Command Center** → User says "Create pitch deck for Palm Jumeirah"
2. **Processing** → Template Orchestrator detects pitch deck intent
3. **Generation** → AI creates structured slide content
4. **Preview** → ReportPreviewCard shows deck summary
5. **Full View** → Click "View" → Navigate to DeckBuilder page
6. **Present** → Full-screen presentation mode with keyboard navigation

## Slide Types & Layouts

### 1. Title Slide
```typescript
{
  type: 'title',
  layout: 'center',
  styling: {
    background: 'gradient-blue-purple',
    text: 'white',
    icon: 'large-centered'
  }
}
```

### 2. Content Slide
```typescript
{
  type: 'content', 
  layout: 'left',
  styling: {
    background: 'white',
    text: 'gray-900',
    bullets: 'blue-accent-icons'
  }
}
```

### 3. Data Slide
```typescript
{
  type: 'data',
  layout: 'split',
  styling: {
    background: 'gradient-green-blue',
    cards: 'white-with-shadows',
    metrics: 'large-emphasized'
  }
}
```

### 4. Closing Slide
```typescript
{
  type: 'closing',
  layout: 'center', 
  styling: {
    background: 'gradient-purple-blue',
    text: 'white',
    cta: 'prominent-arrows'
  }
}
```

## API Integration Points

### Backend Endpoints

| Endpoint | Method | Purpose |
|----------|---------|---------|
| `/api/v1/decks/generate` | POST | Create pitch deck content |
| `/api/v1/content/export/{id}` | POST | Export to PDF/PPTX |
| `/api/v1/decks/{id}/slides` | GET | Retrieve individual slides |

### Request Payload

```typescript
interface DeckGenerationRequest {
  location: string;
  property_type: string;
  investment_amount?: number;
  target_audience: string;
  timeline: string;
  deck_type: 'investor_presentation';
  include_financials: boolean;
  include_market_analysis: boolean;
  slide_count: number;
  output_format: 'structured_slides';
}
```

### Response Format

```typescript
interface DeckGenerationResponse {
  success: boolean;
  task_id: string;
  message: string;
  data: {
    content_id: string;
    deck_data: PitchDeck;
    export_url: string;
    slide_count: number;
  };
  enrichment?: {
    status: 'valid' | 'enriched' | 'fallback';
    inferredFields: string[];
    debugLog: string[];
  };
}
```

## Visual Design Guidelines

### Slide Design Principles

- **Professional Aesthetic**: Clean, modern, investor-focused
- **Consistent Branding**: Company colors and fonts throughout
- **Visual Hierarchy**: Clear title → subtitle → content flow
- **Data Emphasis**: Large metrics, clear charts, highlighted ROI
- **Whitespace**: Generous margins, uncluttered layouts

### Color Scheme by Slide Type

| Slide Type | Background | Text | Accents |
|------------|------------|------|---------|
| **Title** | Blue-Purple Gradient | White | Blue-100 |
| **Content** | White | Gray-900 | Blue-600 |
| **Data** | Green-Blue Gradient | Gray-900 | Green-600 |
| **Closing** | Purple-Blue Gradient | White | Purple-100 |

### Typography & Layout

- **Headers**: Large, bold sans-serif (32-48px)
- **Subheaders**: Medium weight, readable (20-24px)  
- **Body**: Clean, scannable bullet points (16-18px)
- **Metrics**: Emphasized, large numbers (28-36px)

## Error Handling & Fallback

### Validation Failures

```
Input: "Create pitch deck" (missing location)
│
├── Context Enrichment Attempt
│   ├── Check recent property tasks for location
│   ├── Infer from conversation history
│   └── Prompt for clarification if needed
│
├── If Enrichment Succeeds → Generate deck with inferred data
│
└── If Enrichment Fails → Contextual fallback
    └── "I'd be happy to create an investor pitch deck for you! 
         Which property or location should I focus on?"
```

### Generation Failures

- **Slide Content Issues**: Fall back to template-based content
- **Image/Chart Problems**: Use placeholder graphics with data
- **Export Failures**: Provide HTML preview with retry option

## Interactive Features

### Presentation Mode

- **Keyboard Navigation**: Arrow keys, spacebar, escape
- **Full-Screen Display**: Optimized for projectors/large screens
- **Slide Transitions**: Smooth animations between slides
- **Progress Indicators**: Slide counter and progress dots

### Edit Capabilities

- **Content Editing**: Click-to-edit titles and bullet points (future)
- **Slide Reordering**: Drag-and-drop slide sequence (future)
- **Template Switching**: Apply different visual themes (future)

## Quality Assurance Scenarios

### Test Cases

| Scenario | Input | Expected Output |
|----------|--------|-----------------|
| **Complete Request** | "Create investor pitch deck for Marina Walk luxury villa project" | 8-slide professional deck with financial projections |
| **Missing Investment Amount** | "Generate pitch deck for DIFC office building" | Context enrichment → standard commercial investment deck |
| **Vague Property Type** | "Build presentation for premium Dubai project" | Smart defaults → luxury residential assumptions |
| **Export Test** | Generated deck → "Export PDF" | Professional PDF with slide formatting preserved |
| **Presentation Mode** | Deck view → "Present" → Arrow key navigation | Full-screen slides with smooth transitions |

### Validation Criteria

- ✅ All slides follow consistent visual template
- ✅ Content is relevant to property type and location
- ✅ Financial data is realistic and properly formatted
- ✅ Presentation mode functions smoothly
- ✅ Export maintains professional formatting
- ✅ Loading states and error handling work correctly

## Future Enhancements

### v3.2 Planned Features

- **Interactive Charts**: Clickable financial projections
- **Video Integration**: Property tour embeds in slides
- **Real-time Collaboration**: Multi-user editing capabilities
- **Custom Branding**: User uploadable logos and color schemes
- **Analytics Integration**: Track presentation engagement
- **Client Portal**: Shareable links with access controls

## Integration Mapping

### Command Center Workflow

```
User Voice Input
        ↓
Intent Detection (Pitch deck keywords)
        ↓  
Template Orchestrator Route
        ↓
Context Enrichment (Location, investment details)
        ↓
Backend Deck Generation API
        ↓
Structured Slide Response
        ↓
ReportPreviewCard in Command Center
        ↓
DeckBuilder Page on "View"
        ↓
Presentation Mode on "Present"
```

### File Dependencies

- **Frontend**: `templateOrchestrator.ts`, `DeckBuilder.tsx`, `SlideCard.tsx`, `ReportPreviewCard.tsx`
- **Services**: `workflowApi.ts`, `contextEnrichment.ts`, `orchestrator.ts`
- **Store**: `commandStore.ts` (RequestType: 'PITCH_DECK')
- **Backend**: `/api/v1/decks/generate` endpoint, Deck models

## Technical Implementation Notes

### Slide Rendering

- **Aspect Ratio**: 16:9 standard presentation format
- **Responsive Design**: Adapts to different screen sizes
- **Animation**: Framer Motion for smooth slide transitions
- **Typography**: Consistent with brand guidelines

### Data Structure

- **Modular Slides**: Each slide is independent, reorderable
- **Type Safety**: TypeScript interfaces for all slide content
- **Validation**: Required fields checked before rendering
- **Fallbacks**: Default content for missing data points

### Performance Optimization

- **Lazy Loading**: Slides loaded on demand in grid view
- **Image Optimization**: Compressed assets for faster loading
- **Caching**: Generated content cached for quick access
- **Background Processing**: Non-blocking slide generation