# Track 3: Orchestrator Integration & Validation Flow
## Complete Implementation Guide

**Phase:** Track 3 - Intent Normalization, Validation & Content Pipeline  
**Status:** ✅ Foundation Complete | 🚀 Ready for Integration  
**Date:** 2025-10-10  
**Version:** 3.2

---

## 🎯 Overview

Track 3 connects voice/text input → validated structured content → persisted with new schema → routes to viewer. It implements intelligent fallback strategies to ensure **zero 422 errors reach users**.

### Completed Components

1. ✅ **Intent Normalizer** (`intentNormalizer.ts`) - Maps intents to content types
2. 🔄 **Validation Service** (needs creation) - Pre-validates before API calls
3. 🔄 **Enrichment Service** (needs enhancement) - Auto-fills missing fields
4. 🔄 **Content Save Pipeline** (needs integration) - Saves to new store
5. ✅ **Diagnostic Logging** (integrated in normalizer) - Structured console groups

---

## 📂 File Structure

```
aura-client/src/services/
├── intentNormalizer.ts ✅ (NEW)
├── validationService.ts 📝 (TO CREATE)
├── enrichmentService.ts 📝 (TO CREATE)
├── contentSaveService.ts 📝 (TO CREATE)
├── orchestrator.ts ✏️ (TO UPDATE)
├── workflowApi.ts ✏️ (TO UPDATE)
├── templateOrchestrator.ts ✏️ (TO UPDATE)
└── contextEnrichment.ts ✏️ (EXISTS - needs enhancement)
```

---

## 🔄 Data Flow

```
User Input (Voice/Text)
  ↓
Intent Detection (intentParser.ts)
  ↓
Intent Normalization (intentNormalizer.ts) ✅
  ↓
[Orchestrator] Content Type Routing
  ├→ CMA_REPORT
  ├→ PITCH_DECK
  ├→ MARKET_REPORT
  ├→ NEWSLETTER
  └→ SOCIAL_POST
  ↓
Pre-Validation (validationService.ts) 📝
  ├→ Valid → Proceed
  └→ Invalid → Enrichment
      ↓
  Enrichment (enrichmentService.ts) 📝
      ├→ Auto-filled → Proceed
      └→ Cannot fill → Ask user or fallback
  ↓
API Call (workflowApi.ts) ✏️
  ├→ 200 Success → Save Content
  ├→ 422 Validation → Self-Heal → Retry
  └→ Error → Fallback to Streaming
  ↓
Content Save (contentSaveService.ts) 📝
  ├→ Transform API response to schema
  ├→ Save via store.saveContent()
  └→ Update task with has_content=true
  ↓
Navigate to Viewer
  └→ /content/{type}/{taskId}
```

---

## ✅ Track 3.1: Intent Normalization (COMPLETE)

### Implementation

**File:** `aura-client/src/services/intentNormalizer.ts` ✅

**Features:**
- Maps legacy intent types to `SchemaContentType`
- Extracts entities (address, tone, platform, etc.)
- Identifies missing required fields
- Determines if auto-fill is possible
- Generates unique request IDs for tracing
- Provides structured diagnostic logs

**Usage Example:**
```typescript
import { normalizeIntent, formatDiagnosticLog } from './intentNormalizer';

const intent = detectIntent(userPrompt);
const normalized = normalizeIntent(intent, userPrompt);

if (!normalized) {
  // Fall back to streaming
  return;
}

console.log('[Orchestrator] Diagnostic Log:');
formatDiagnosticLog(normalized).forEach(line => console.log(line));

// normalized.contentType → SchemaContentType
// normalized.entities → { address, propertyType, ... }
// normalized.missingFields → ['field1', 'field2']
// normalized.canAutoFill → true/false
```

**Entity Extraction:**
- **CMA Report:** address, propertyType, comparableCount, dateRange
- **Pitch Deck:** address, investmentType, targetAudience, slideCount
- **Market Report:** region, propertyType, timePeriod, metricsRequired
- **Newsletter:** topic, tone, targetAudience
- **Social Post:** topic, platform, tone, hashtags

---

## 📝 Track 3.2: Validation & Enrichment (TO IMPLEMENT)

### Validation Service

**File:** `aura-client/src/services/validationService.ts` (TO CREATE)

```typescript
/**
 * Validation Service
 * Validates payloads before API calls
 * Calls backend validator endpoints
 */

import { ContentType, ValidationResult } from '../types/contentSchemas';
import { NormalizedIntent } from './intentNormalizer';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ValidationRequest {
  contentType: ContentType;
  payload: Record<string, any>;
  requestId: string;
}

/**
 * Validate payload with backend validator
 */
export const validatePayload = async (
  request: ValidationRequest
): Promise<ValidationResult> => {
  console.group(`[Validation] ${request.requestId}`);
  console.log('Content Type:', request.contentType);
  console.log('Payload:', request.payload);
  console.time('Validation');

  try {
    const endpoint = `/api/v1/validate/${request.contentType.toLowerCase()}`;
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request.payload),
    });

    const result: ValidationResult = await response.json();
    
    console.log('Validation Result:', {
      valid: result.valid,
      missing_fields: result.missing_fields,
      confidence: result.confidence,
      tips_count: result.tips.length,
    });
    
    console.timeEnd('Validation');
    console.groupEnd();

    return result;
  } catch (error) {
    console.error('Validation error:', error);
    console.timeEnd('Validation');
    console.groupEnd();

    // Return pessimistic validation result
    return {
      valid: false,
      missing_fields: ['unknown'],
      normalized_payload: request.payload,
      tips: ['Validation service unavailable - attempting enrichment'],
      confidence: 0,
    };
  }
};

/**
 * Build payload from normalized intent
 */
export const buildPayload = (normalized: NormalizedIntent): Record<string, any> => {
  const { contentType, entities } = normalized;
  
  switch (contentType) {
    case ContentType.CMA_REPORT:
      return {
        address: entities.address,
        property_type: entities.propertyType || 'mixed',
        comparable_count: entities.comparableCount || 5,
        date_range: entities.dateRange || '6_months',
      };
    
    case ContentType.PITCH_DECK:
      return {
        address: entities.address,
        property_type: entities.propertyType || 'luxury',
        investment_type: entities.investmentType || 'acquisition',
        target_audience: entities.targetAudience || 'investors',
        slide_count: entities.slideCount || 8,
      };
    
    case ContentType.MARKET_REPORT:
      return {
        region: entities.region,
        property_type: entities.propertyType || 'mixed',
        time_period: entities.timePeriod || 'quarterly',
        metrics: entities.metricsRequired || ['price_trends', 'volume', 'inventory'],
      };
    
    case ContentType.NEWSLETTER:
      return {
        topic: entities.topic,
        tone: entities.tone || 'professional',
        target_audience: entities.targetAudience || 'clients',
      };
    
    case ContentType.SOCIAL_POST:
      return {
        topic: entities.topic,
        platform: entities.platform || 'instagram',
        tone: entities.tone || 'engaging',
        hashtags: entities.hashtags || [],
      };
    
    default:
      return entities;
  }
};
```

### Enrichment Service

**File:** `aura-client/src/services/enrichmentService.ts` (TO CREATE)

```typescript
/**
 * Enrichment Service
 * Auto-fills missing fields from context, recent tasks, and defaults
 */

import { ValidationResult } from '../types/contentSchemas';
import { NormalizedIntent } from './intentNormalizer';

export interface EnrichmentResult {
  success: boolean;
  enrichedPayload: Record<string, any>;
  inferredFields: string[];
  stillMissing: string[];
  needsUserInput: boolean;
  suggestions: string[];
}

/**
 * Enrich payload with context and defaults
 */
export const enrichPayload = async (
  payload: Record<string, any>,
  validationResult: ValidationResult,
  normalized: NormalizedIntent,
  recentTasks: any[],
  contextHistory: string[]
): Promise<EnrichmentResult> => {
  console.group(`[Enrichment] ${normalized.requestId}`);
  console.log('Missing fields:', validationResult.missing_fields);
  console.log('Recent tasks:', recentTasks.length);
  console.time('Enrichment');

  const enriched = { ...payload };
  const inferredFields: string[] = [];
  const stillMissing: string[] = [];
  const suggestions: string[] = [];

  for (const field of validationResult.missing_fields) {
    // Try to infer from recent tasks
    const inferred = inferFromRecentTasks(field, recentTasks, normalized.contentType);
    if (inferred) {
      enriched[field] = inferred;
      inferredFields.push(field);
      console.log(`✓ Inferred ${field} from recent tasks:`, inferred);
      continue;
    }

    // Try to infer from context
    const fromContext = inferFromContext(field, contextHistory, normalized.contentType);
    if (fromContext) {
      enriched[field] = fromContext;
      inferredFields.push(field);
      console.log(`✓ Inferred ${field} from context:`, fromContext);
      continue;
    }

    // Try default value
    const defaultValue = getDefaultValue(field, normalized.contentType);
    if (defaultValue !== null) {
      enriched[field] = defaultValue;
      inferredFields.push(field);
      console.log(`✓ Using default for ${field}:`, defaultValue);
      continue;
    }

    // Still missing
    stillMissing.push(field);
    suggestions.push(formatSuggestion(field, normalized.contentType));
  }

  const result: EnrichmentResult = {
    success: stillMissing.length === 0,
    enrichedPayload: enriched,
    inferredFields,
    stillMissing,
    needsUserInput: stillMissing.length > 0 && !canProceedWithoutField(stillMissing, normalized.contentType),
    suggestions,
  };

  console.log('Enrichment Result:', {
    success: result.success,
    inferred: inferredFields.length,
    still_missing: stillMissing.length,
    needs_input: result.needsUserInput,
  });

  console.timeEnd('Enrichment');
  console.groupEnd();

  return result;
};

// Helper functions
const inferFromRecentTasks = (field: string, tasks: any[], contentType: string): any => {
  const relevantTasks = tasks.filter(t => t.type === contentType);
  if (relevantTasks.length === 0) return null;

  const recent = relevantTasks[0];
  return recent.metadata?.[field] || recent[field] || null;
};

const inferFromContext = (field: string, context: string[], contentType: string): any => {
  // Placeholder - implement context parsing logic
  return null;
};

const getDefaultValue = (field: string, contentType: string): any => {
  const defaults: Record<string, Record<string, any>> = {
    [ContentType.CMA_REPORT]: {
      propertyType: 'mixed',
      comparableCount: 5,
      dateRange: '6_months',
    },
    [ContentType.PITCH_DECK]: {
      slideCount: 8,
      targetAudience: 'investors',
      investmentType: 'acquisition',
    },
    [ContentType.MARKET_REPORT]: {
      propertyType: 'mixed',
      timePeriod: 'quarterly',
    },
    [ContentType.NEWSLETTER]: {
      tone: 'professional',
    },
    [ContentType.SOCIAL_POST]: {
      platform: 'instagram',
      tone: 'engaging',
    },
  };

  return defaults[contentType]?.[field] ?? null;
};

const canProceedWithoutField = (fields: string[], contentType: string): boolean => {
  // Critical fields that cannot be auto-filled
  const critical: Record<string, string[]> = {
    [ContentType.CMA_REPORT]: ['address'],
    [ContentType.PITCH_DECK]: ['address'],
    [ContentType.MARKET_REPORT]: ['region'],
    [ContentType.NEWSLETTER]: ['topic'],
    [ContentType.SOCIAL_POST]: ['topic'],
  };

  const criticalMissing = fields.filter(f => critical[contentType]?.includes(f));
  return criticalMissing.length === 0;
};

const formatSuggestion = (field: string, contentType: string): string => {
  const fieldMap: Record<string, string> = {
    address: 'property address',
    region: 'market region',
    topic: 'content topic',
    propertyType: 'property type',
    targetAudience: 'target audience',
  };

  const friendlyField = fieldMap[field] || field;
  return `Please provide the ${friendlyField}`;
};
```

---

## 🔄 Track 3.3: Self-Healing & Fallback (TO IMPLEMENT)

### Enhanced Orchestrator with Self-Healing

**File:** `aura-client/src/services/orchestrator.ts` (UPDATE)

```typescript
// Add to orchestrator.ts

import { normalizeIntent, formatDiagnosticLog } from './intentNormalizer';
import { validatePayload, buildPayload } from './validationService';
import { enrichPayload } from './enrichmentService';
import { saveGeneratedContent, navigateToViewer } from './contentSaveService';

/**
 * Enhanced orchestration with full validation and self-healing
 */
export async function orchestrateCommandEnhanced(
  prompt: string,
  parentId?: string,
  recentTasks: any[] = [],
  contextHistory: string[] = []
): Promise<OrchestrationResult> {
  const intent = detectIntent(prompt);
  
  // Step 1: Normalize intent
  const normalized = normalizeIntent(intent, prompt);
  if (!normalized) {
    console.log('[Orchestrator] Cannot normalize - fallback to streaming');
    return { intent, fallbackToStream: true, validationStatus: 'stream' };
  }

  // Log diagnostics
  console.log('[Orchestrator] Diagnostic Log:');
  formatDiagnosticLog(normalized).forEach(line => console.log(line));

  // Step 2: Build payload
  const payload = buildPayload(normalized);

  // Step 3: Pre-validate
  const validation = await validatePayload({
    contentType: normalized.contentType,
    payload,
    requestId: normalized.requestId,
  });

  if (validation.valid) {
    console.log('[Validation] ✅ Payload is valid - proceeding to generation');
    return await executeGeneration(normalized, payload, parentId);
  }

  // Step 4: Enrichment attempt
  console.log('[Validation] ❌ Payload invalid - attempting enrichment');
  const enrichment = await enrichPayload(
    payload,
    validation,
    normalized,
    recentTasks,
    contextHistory
  );

  if (enrichment.success) {
    console.log('[Enrichment] ✅ Enrichment successful - proceeding');
    return await executeGeneration(normalized, enrichment.enrichedPayload, parentId);
  }

  // Step 5: Self-healing on 422
  if (enrichment.needsUserInput) {
    console.log('[Enrichment] 🔄 User input needed');
    // Could show micro-questions here
    return {
      intent,
      fallbackToStream: true,
      validationStatus: 'fallback',
      userMessage: `I need more information: ${enrichment.suggestions.join(', ')}`,
    };
  }

  // Step 6: Final fallback
  console.log('[Enrichment] Cannot proceed - fallback to streaming');
  return {
    intent,
    fallbackToStream: true,
    validationStatus: 'fallback',
    userMessage: 'Let me help you with that through our conversation instead.',
  };
}

/**
 * Execute content generation with retry logic
 */
async function executeGeneration(
  normalized: NormalizedIntent,
  payload: Record<string, any>,
  parentId?: string
): Promise<OrchestrationResult> {
  try {
    // Call backend API
    const response = await callGenerationAPI(normalized.contentType, payload);

    if (response.success && response.content) {
      // Save content to store
      const savedContent = await saveGeneratedContent(response.content, normalized.requestId);
      
      // Navigate to viewer
      navigateToViewer(normalized.contentType, savedContent.taskId);

      return {
        intent: { type: normalized.contentType, confidence: normalized.confidence },
        contentGeneration: response,
        fallbackToStream: false,
        parentId,
        validationStatus: 'valid',
        userMessage: `Your ${normalized.contentType} is ready! Opening now...`,
      };
    }

    throw new Error('Generation returned no content');
  } catch (error) {
    // Handle 422 with self-healing
    if (is422Error(error)) {
      console.warn('[Orchestrator] 🛡️ 422 caught - user will not see this');
      // Could retry once with additional enrichment here
    }

    return {
      intent: { type: normalized.contentType, confidence: normalized.confidence },
      fallbackToStream: true,
      parentId,
      validationStatus: 'fallback',
      userMessage: 'I encountered an issue. Let me help you through conversation instead.',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

const is422Error = (error: any): boolean => {
  const msg = error?.message || '';
  return msg.includes('422') || msg.includes('Unprocessable');
};
```

---

## 💾 Track 3.5: Content Save Pipeline (TO IMPLEMENT)

### Content Save Service

**File:** `aura-client/src/services/contentSaveService.ts` (TO CREATE)

```typescript
/**
 * Content Save Service
 * Transforms API responses to schema format and persists
 */

import { useCommandStore } from '../store/commandStore';
import {
  GeneratedContent,
  ContentType,
  CONTENT_SCHEMA_VERSION,
  createContentTemplate,
} from '../types/contentSchemas';
import { useNavigate } from 'react-router-dom';

/**
 * Transform API response to schema format
 */
export const transformAPIResponse = (
  apiResponse: any,
  contentType: ContentType,
  taskId: string
): GeneratedContent => {
  const base = createContentTemplate(contentType, taskId, apiResponse.title || 'Generated Content');

  // Content type specific transformations
  switch (contentType) {
    case ContentType.CMA_REPORT:
      return {
        ...base,
        type: ContentType.CMA_REPORT,
        property: apiResponse.property || { address: '' },
        marketAnalysis: apiResponse.market_analysis || {},
        comparables: apiResponse.comparables || [],
        valuation: apiResponse.valuation || {},
        insights: apiResponse.insights || [],
        disclaimers: apiResponse.disclaimers || [],
        reportId: taskId,
        sections: apiResponse.sections || [],
      } as GeneratedContent;
    
    case ContentType.PITCH_DECK:
      return {
        ...base,
        type: ContentType.PITCH_DECK,
        property: apiResponse.property || { address: '', type: 'residential' },
        slides: apiResponse.slides || [],
        theme: apiResponse.theme || { primaryColor: '#667eea', accentColor: '#764ba2', fontFamily: 'Inter' },
      } as GeneratedContent;
    
    // Add other content types...
    
    default:
      return base as GeneratedContent;
  }
};

/**
 * Save generated content to store
 */
export const saveGeneratedContent = async (
  apiResponse: any,
  requestId: string
): Promise<{ taskId: string; content: GeneratedContent }> => {
  console.group(`[ContentSave] ${requestId}`);
  console.time('Save Content');

  const taskId = apiResponse.task_id || apiResponse.id || `task_${Date.now()}`;
  const contentType = apiResponse.content_type || apiResponse.type;

  // Transform API response to schema
  const content = transformAPIResponse(apiResponse, contentType, taskId);

  // Save to store
  const store = useCommandStore.getState();
  store.saveContent(content);

  console.log('✅ Content saved:', {
    taskId,
    contentType,
    sections: content.sections?.length || 0,
  });

  console.timeEnd('Save Content');
  console.groupEnd();

  return { taskId, content };
};

/**
 * Navigate to appropriate viewer
 */
export const navigateToViewer = (contentType: ContentType, taskId: string): void => {
  const routeMap: Record<ContentType, string> = {
    [ContentType.CMA_REPORT]: 'cma',
    [ContentType.PITCH_DECK]: 'deck',
    [ContentType.MARKET_REPORT]: 'market-report',
    [ContentType.NEWSLETTER]: 'newsletter',
    [ContentType.SOCIAL_POST]: 'social',
  };

  const route = `/content/${routeMap[contentType]}/${taskId}`;
  
  console.log(`[ContentSave] Navigating to: ${route}`);
  
  // Use router navigation
  const navigate = useNavigate();
  navigate(route);
};
```

---

## 📋 Integration Checklist

### Backend Prerequisites
- [ ] Validation endpoints per content type (`/api/v1/validate/{type}`)
- [ ] Generation endpoints return structured JSON
- [ ] Content includes `sections` array matching schema
- [ ] Task sync updates `has_content` flag
- [ ] Export endpoints handle new schema

### Frontend Integration
- [x] Intent normalizer created ✅
- [ ] Validation service created
- [ ] Enrichment service created  
- [ ] Content save service created
- [ ] Orchestrator updated to use new flow
- [ ] WorkflowApi updated for new content types
- [ ] Template orchestrator returns new schema
- [ ] Task sync triggers content hydration

---

## 🧪 Testing Strategy

### Unit Tests
```typescript
// intentNormalizer.test.ts
test('maps CMA intent to ContentType.CMA_REPORT', () => {
  const intent = { type: 'CMA', location: 'Dubai', confidence: 0.9 };
  const normalized = normalizeIntent(intent, 'Generate CMA for Dubai');
  expect(normalized?.contentType).toBe(ContentType.CMA_REPORT);
});

// validationService.test.ts
test('validates CMA payload with all required fields', async () => {
  const payload = { address: '123 Main St', property_type: 'residential' };
  const result = await validatePayload({
    contentType: ContentType.CMA_REPORT,
    payload,
    requestId: 'test_123',
  });
  expect(result.valid).toBe(true);
});

// enrichmentService.test.ts
test('enriches missing fields from recent tasks', async () => {
  const recentTasks = [{ type: 'CMA_REPORT', metadata: { property_type: 'commercial' } }];
  const result = await enrichPayload(
    { address: '456 Oak Ave' },
    { valid: false, missing_fields: ['property_type'] },
    normalized,
    recentTasks,
    []
  );
  expect(result.enrichedPayload.property_type).toBe('commercial');
});
```

### Integration Tests
- [ ] Voice → intent → normalize → validate → generate → save → navigate
- [ ] 422 error triggers enrichment and retry
- [ ] Missing critical field shows user prompt
- [ ] Content appears in store after save
- [ ] Viewer displays saved content correctly

---

## 📊 Success Metrics

- **Zero 422 errors** visible to users
- **> 80% auto-enrichment** success rate
- **< 2s validation latency**
- **100% content persistence** on success
- **Correct routing** to viewer every time

---

## 🚀 Next Steps

1. **Create validation service** with backend integration
2. **Create enrichment service** with context inference
3. **Create content save service** with schema transformation
4. **Update orchestrator** to use new pipeline
5. **Update workflowApi** for new content types
6. **Test end-to-end** flow with all content types
7. **Add micro-questions** UI for missing fields (optional)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-10  
**Estimated Effort:** 6-8 hours for full Track 3 implementation
