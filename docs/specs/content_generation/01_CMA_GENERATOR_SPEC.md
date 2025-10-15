# CMA Generator Specification v3.1

## Overview

The CMA (Competitive Market Analysis) Generator is an AI-powered content creation system that transforms voice or text commands into comprehensive, professionally formatted market analysis reports. This system integrates seamlessly with Aura's Command Center and follows the brand's visual templates.

## System Architecture

```
User Input → Intent Parser → Template Orchestrator → Workflow API → Content Generation → Report Viewer
     ↓              ↓               ↓                    ↓               ↓              ↓
  "Generate       CMA Intent    Content Type       Backend API     Structured      Full-page
   CMA for      Detected &    Mapping &         /api/v1/cma/      JSON with       Report with
   Dubai       Context        Enrichment         generate         Market Data     Export Options
   Marina"     Enhanced
```

## Input Processing Flow

### 1. User Input Examples

**Voice Commands:**
- "Generate a CMA for Downtown Dubai"  
- "Create a market analysis for Palm Jumeirah"
- "I need a competitive analysis for Business Bay"

**Text Commands:**
- "Generate CMA Downtown Dubai"
- "Create comprehensive market analysis for DIFC luxury properties"
- "Build CMA report Marina Walk 3-bedroom apartments"

### 2. Intent Detection & Classification

```typescript
interface CMAIntent {
  type: 'CMA';
  location: string;           // Required: "Downtown Dubai"
  property_type?: string;     // Optional: "luxury", "residential", "commercial"
  date_range?: string;        // Optional: "3_months", "6_months", "12_months"
  comparable_count?: number;  // Optional: 3-10, default 5
  confidence: number;         // 0.0-1.0
}
```

### 3. Context Enrichment Process

The system attempts to infer missing fields from:
- **Recent Tasks**: Previous CMA requests, location patterns
- **Context History**: Recent conversation mentions of areas/properties
- **Prompt Analysis**: Extract property types, timeframes from natural language
- **Smart Defaults**: Location fallbacks, standard analysis periods

## Data Flow Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   User Input    │───▶│  Intent Parser   │───▶│ Template Orchestr.  │
│ "CMA for Dubai" │    │ + Context Enrich │    │   Content Mapping   │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                                           │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Error Recovery│◄───│   Workflow API   │◄───│   Payload Building  │
│  + Streaming AI │    │  /cma/generate   │    │ + Field Validation  │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Report Viewer  │◄───│  Generated CMA   │◄───│   AI Processing     │
│  + Export Opts  │    │ Structured JSON  │    │  Market Analysis    │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Generated Content Structure

### CMA Report Schema

```typescript
interface CMAReport {
  executive_summary: string;
  market_overview: {
    average_price_psf: number;
    total_listings: number;
    avg_days_on_market: number;
    price_trend: 'upward' | 'downward' | 'stable';
    median_price: number;
    price_change_yoy: number;
  };
  comparables: Array<{
    address: string;
    price: number;
    size: number;
    price_psf: number;
    bedrooms?: number;
    bathrooms?: number;
    building_type?: string;
    days_on_market?: number;
  }>;
  insights: string[];
  recommendations: string;
  neighborhood_stats?: {
    population: number;
    avg_income: number;
    employment_rate: number;
    development_projects: number;
  };
}
```

### Example Output

```json
{
  "executive_summary": "Comprehensive market analysis for Downtown Dubai showing strong investment potential with 12% YoY growth and robust demand in the luxury segment.",
  "market_overview": {
    "average_price_psf": 1250,
    "total_listings": 156,
    "avg_days_on_market": 28,
    "price_trend": "upward",
    "median_price": 2500000,
    "price_change_yoy": 12.5
  },
  "comparables": [
    {
      "address": "Downtown Dubai Tower A",
      "price": 2500000,
      "size": 2000,
      "price_psf": 1250,
      "bedrooms": 3,
      "bathrooms": 3,
      "days_on_market": 25
    }
  ],
  "insights": [
    "Market showing strong upward momentum",
    "High demand in luxury segment",
    "Limited supply driving premium pricing"
  ],
  "recommendations": "Excellent time for investment with strong rental yields expected. Market fundamentals support continued appreciation."
}
```

## Frontend Integration

### Component Hierarchy

```
CMAReport Page (Full Viewer)
├── Header (Export, Share, Print)
├── Report Content
│   ├── Executive Summary Section
│   ├── Market Overview Cards
│   ├── Comparables Table
│   ├── Insights List
│   └── Recommendations Section
└── Footer (Branding, Data Sources)

ReportPreviewCard (Command Center)
├── Report Header + Status
├── Content Preview (Summary)
└── Action Buttons (View, Export, Share)
```

### Navigation Flow

1. **Command Center** → User says "Generate CMA for Dubai Marina"
2. **Processing** → Template Orchestrator validates and enriches request
3. **Generation** → AI creates comprehensive CMA report
4. **Preview** → ReportPreviewCard appears in Command Center
5. **Full View** → Click "View Full Report" → Navigate to CMAReport page
6. **Export** → PDF/HTML/JSON export options available

## API Integration Points

### Backend Endpoints

| Endpoint | Method | Purpose |
|----------|---------|---------|
| `/api/v1/cma/generate` | POST | Create CMA content |
| `/api/v1/content/export/{id}` | POST | Export to PDF/HTML |
| `/api/v1/tasks/{id}/status` | GET | Check generation status |

### Request Payload

```typescript
interface CMAGenerationRequest {
  location: string;
  property_type: string;
  date_range: string;
  comparable_count: number;
  analysis_type: 'comprehensive' | 'basic';
  include_insights: boolean;
  include_recommendations: boolean;
  output_format: 'structured_json';
}
```

### Response Format

```typescript
interface CMAGenerationResponse {
  success: boolean;
  task_id: string;
  message: string;
  data: {
    content_id: string;
    report_data: CMAReport;
    export_url: string;
    estimated_completion?: string;
  };
  enrichment?: {
    status: 'valid' | 'enriched' | 'fallback';
    inferredFields: string[];
    debugLog: string[];
  };
}
```

## Visual Design Guidelines

### Brand Consistency

- **Color Scheme**: Clean, professional blues and grays
- **Typography**: Sans-serif headers, readable body text
- **Layout**: Newsletter-style with clear section hierarchy
- **White Space**: Generous margins and padding
- **Data Visualization**: Simple, clean charts and tables

### Template Structure

1. **Header Section**: Gradient background with location and date
2. **Executive Summary**: Highlighted in blue accent box
3. **Market Overview**: 4-column metrics grid
4. **Comparables**: Professional table with alternating row colors
5. **Insights**: Numbered list with orange accent indicators
6. **Recommendations**: Green accent box with action-oriented text
7. **Footer**: Subtle branding and data attribution

## Error Handling & Fallback

### Validation Failures

```
Input: "Generate CMA" (missing location)
│
├── Context Enrichment Attempt
│   ├── Check recent tasks for location mentions
│   ├── Analyze conversation history
│   └── Apply smart defaults if available
│
├── If Enrichment Succeeds → Proceed with generation
│
└── If Enrichment Fails → Graceful fallback
    └── Return to streaming conversation:
        "I need more information to generate your CMA report. 
         Which location would you like me to analyze?"
```

### Generation Failures

- **API Timeouts**: Show progress indicator, retry automatically
- **Data Issues**: Fall back to mock data with clear labeling
- **Network Problems**: Queue for retry when connection restored

## Quality Assurance Scenarios

### Test Cases

| Scenario | Input | Expected Output |
|----------|--------|-----------------|
| **Happy Path** | "Generate CMA for Downtown Dubai" | Complete CMA report with market data |
| **Missing Location** | "Generate CMA report" | Contextual prompt for location |
| **Vague Input** | "Create analysis for luxury properties" | Context enrichment → specific CMA |
| **Network Failure** | Valid request but API down | Graceful error → conversation fallback |
| **Export Test** | Generated CMA → "Export PDF" | PDF download with professional formatting |

### Validation Criteria

- ✅ Report contains all required sections
- ✅ Data is realistic and formatted correctly  
- ✅ Visual design matches brand templates
- ✅ Export functions work for PDF/HTML
- ✅ Error messages are user-friendly
- ✅ Performance: Generation completes within 10 seconds

## Future Enhancements

### v3.2 Planned Features

- **Interactive Charts**: Clickable price trend visualizations
- **Comparative Analysis**: Side-by-side area comparisons
- **Historical Data**: Multi-year trend analysis
- **Custom Templates**: User-customizable report formats
- **Email Integration**: Direct sharing to clients
- **API Caching**: Faster subsequent reports for same area

## Integration Mapping

### Command Center Workflow

```
User Voice Input
        ↓
Intent Detection (CMA recognized)
        ↓
Template Orchestrator Route
        ↓
Context Enrichment & Validation
        ↓
Backend CMA Generation API
        ↓
Structured Content Response
        ↓
ReportPreviewCard in Command Center
        ↓
Full CMAReport Page on "View"
```

### File Dependencies

- **Frontend**: `templateOrchestrator.ts`, `CMAReport.tsx`, `ReportPreviewCard.tsx`
- **Services**: `workflowApi.ts`, `contextEnrichment.ts`, `orchestrator.ts`
- **Store**: `commandStore.ts` (RequestType: 'CMA_REPORT')
- **Backend**: `/api/v1/cma/generate` endpoint, CMA models