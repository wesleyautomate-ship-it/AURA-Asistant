# Track 1: Backend Alignment & Schema Standardization
## Implementation Summary - Phase 3.2

**Status:** ✅ In Progress (40% Complete)  
**Started:** 2025-10-10  
**Target Completion:** Week 2

---

## Overview

Track 1 establishes the backend foundation for Aura's transformation into a production-grade AI Content Engine. This includes standardized schemas, validation layers, task API enhancements, export services, and observability infrastructure.

---

## ✅ Completed Work

### 1.1 Backend Content Taxonomy and OpenAPI Contracts ✅

**File:** `backend/app/schemas/content_types.py`

Created standardized content type enums and schemas:

#### Content Types
- `CMA_REPORT` - Comparative Market Analysis
- `PITCH_DECK` - Investor Pitch Decks
- `MARKET_REPORT` - Market Analysis Reports
- `NEWSLETTER` - Email Newsletters
- `SOCIAL_POST` - Social Media Posts

#### Key Schemas Implemented

1. **ValidationResult**
   - `valid`: boolean
   - `missing_fields`: string[]
   - `normalized_payload`: object
   - `tips`: string[]
   - `confidence`: 0.0-1.0

2. **ValidationError422**
   - Machine-parsable error structure
   - `missing_fields`: explicit list
   - `hints`: user-friendly suggestions
   - `suggested_defaults`: auto-heal values
   - `can_auto_heal`: boolean flag

3. **TaskResponse** (Canonical)
   - Standard fields: id, title, status, type, timestamps
   - Content flags: `has_content`, `content_type`
   - Relationships: `parent_id`, `related_tasks`
   - Export metadata: `exported_at`, `export_formats`
   - Error handling: `error` field

4. **TaskSyncResponse**
   - `tasks`: TaskResponse[]
   - `last_sync`: ISO timestamp
   - `has_more`: pagination flag
   - `cursor`: optional string for next page

5. **Content-Specific Requests**
   - `CMAReportRequest`: location, property_type, bedrooms, bathrooms, sqft, time_range, comparable_count
   - `PitchDeckRequest`: property_address, investment_type, target_audience, slide_count, include_financials
   - `MarketReportRequest`: region, property_type, time_period, metrics[]
   - `NewsletterRequest`: topic, tone, target_audience, include_listings, max_length
   - `SocialPostRequest`: platform, topic, tone, include_hashtags, character_limit, property_id

**Alignment:** ✅ Maps 1:1 with frontend `ContentType` and `docs/content_templates/README.md`

---

### 1.2 Validation Layer per Content Type ✅

**File:** `backend/app/services/content_validators.py`

Implemented validators for all five content types with consistent interface:

#### Validator Functions

1. **validate_cma_report()**
   - Required: location
   - Normalizes: property_type, numeric fields, comparable_count (3-10)
   - Tips: Location formats, minimum comparables
   - Confidence scoring based on completeness

2. **validate_pitch_deck()**
   - Required: property_address
   - Normalizes: investment_type, target_audience, slide_count (5-20)
   - Validates: Investment type enum
   - Smart defaults for missing fields

3. **validate_market_report()**
   - Required: region
   - Normalizes: property_type, time_period, metrics[]
   - Defaults: price_per_sqft, trend_analysis, demand_index
   - Flexible metric combinations

4. **validate_newsletter()**
   - Required: topic
   - Normalizes: tone, target_audience, max_length (100-2000)
   - Validates: Tone enum values
   - Persona-aware defaults

5. **validate_social_post()**
   - Required: platform, topic
   - Normalizes: tone, hashtags, character_limit
   - Platform-specific: Auto-sets character limits (Twitter: 280, Instagram: 2200, etc.)
   - Validates: Platform enum

#### Helper Functions

- `normalize_location()`: Standardizes Dubai neighborhood names
- `normalize_property_type()`: Maps variations to standard types
- `extract_number_from_text()`: Extracts numeric values from prompts
- `enrich_from_context()`: Attempts auto-healing from recent tasks and prompts
- `extract_location_from_text()`: Location entity extraction
- `extract_property_type_from_text()`: Property type entity extraction

#### Main Dispatcher

- `validate_content_request(content_type, payload)`: Routes to appropriate validator

**Key Features:**
- Consistent return structure (ValidationResult)
- Helpful tips for missing fields
- Smart defaults to minimize user friction
- Confidence scoring
- Context enrichment preparation

---

### 1.3 Tasks API Alignment (Partial) ✅

**File:** `backend/app/api/v1/tasks_router.py`

#### TaskEntity Enhancements

Added Phase 3.2 fields to `TaskEntity` class:
- `has_content`: boolean (default False)
- `content_type`: ContentType enum
- `parent_id`: string (for follow-up tasks)
- `related_tasks`: string[] (related task IDs)
- `exported_at`: datetime (last export timestamp)
- `export_formats`: string[] (available formats)
- `type`: string (task type for frontend routing)

#### to_dict() Method Enhanced

Updated to include:
- All new Phase 3.2 fields
- `timestamp`: alias for `created_at` (frontend compatibility)
- `metadata`: object with location and report_url

#### Sync Endpoint Redesigned

**Endpoint:** `GET /api/v1/tasks/sync`

**Query Parameters:**
- `since`: ISO timestamp for incremental sync
- `limit`: max tasks to return (default 50, max 100)

**Response Structure:**
```json
{
  "tasks": [TaskResponse],
  "last_sync": "ISO timestamp",
  "has_more": boolean,
  "cursor": "optional pagination cursor"
}
```

**Features:**
- Idempotent polling support
- Incremental updates (only changed tasks)
- Stable ordering by `updated_at` and `id`
- Mock data for development mode
- Canonical task structure matching frontend expectations

**Development Mode:**
Returns 3 mock tasks with varied states:
- Complete CMA Report (has_content=true)
- Processing Market Report
- Error Social Post (with error message)

---

## 🔧 In Progress

### 1.4 Export Service (Next Up)

**Planned Files:**
- `backend/app/api/v1/export_router.py`
- `backend/app/services/exporters/` (directory)
  - `base_exporter.py`
  - `pdf_exporter.py`
  - `html_exporter.py`
  - `share_link_generator.py`

**Requirements:**
- `POST /api/v1/export` endpoint
- Support formats: `pdf`, `html`
- PDF generation: Playwright for Python or WeasyPrint
- HTML templates mirroring frontend structure
- Share link generation with signed tokens
- Time-boxed link expiry (configurable TTL)
- Export metadata persistence

---

## 📋 Remaining Work

### 1.5 Structured Observability
- JSON logger with structured fields
- Request ID correlation (frontend↔backend)
- OpenTelemetry traces
- Validation metrics dashboard

### 1.6 Security & Rate Limiting
- JWT validation on all endpoints
- Share link token signing
- Rate limiting per user
- Input sanitization

### 1.7 Backend QA & Migrations
- Database migrations for new task fields
- Optional exports table
- Unit tests for validators
- Integration tests for sync endpoint
- Load testing
- Contract test artifacts for CI

---

## 🎯 Acceptance Criteria

### Completed ✅
- [x] Content types enum matches frontend 1:1
- [x] Validation functions return consistent structure
- [x] 422 errors include `missing_fields` and `hints`
- [x] Task sync supports incremental updates
- [x] TaskEntity includes content generation fields

### Pending ⏳
- [ ] Export service generates valid PDFs/HTML
- [ ] Share links use signed tokens with TTL
- [ ] Structured logs correlate with frontend
- [ ] Migrations run without errors
- [ ] All validators have unit tests
- [ ] Sync endpoint passes contract tests

---

## 🔗 Dependencies

### Downstream (Track 2 - Frontend)
Frontend needs these backend contracts:
- `ContentType` enum values
- `ValidationError422` structure
- `TaskResponse` canonical shape
- `/api/v1/tasks/sync` response format
- Export endpoint contract (pending)

### Upstream (Track 3 - Orchestrator)
Orchestrator will use:
- `validate_content_request()` function
- `enrich_from_context()` helper
- 422 error structures for auto-healing

---

## 📊 API Documentation

### New Endpoints

1. **GET /api/v1/tasks/sync**
   - Returns changed tasks since timestamp
   - Idempotent polling support
   - Status: ✅ Implemented

2. **POST /api/v1/export** (planned)
   - Exports content as PDF or HTML
   - Returns file or share link
   - Status: ⏳ Next sprint

### Updated Endpoints

1. **GET /api/v1/tasks**
   - Now returns `has_content`, `content_type`, `parent_id`
   - Status: ✅ Implemented

2. **POST /api/v1/cma/create** (next)
   - Will use validation layer
   - Returns structured 422 on validation failure
   - Status: ⏳ Track 1.4

---

## 🧪 Testing Strategy

### Unit Tests (Pending)
```python
# backend/app/tests/test_content_validators.py
def test_cma_validator_happy_path()
def test_cma_validator_missing_location()
def test_cma_validator_normalization()
def test_pitch_deck_validator_slide_bounds()
def test_social_post_validator_platform_limits()
```

### Integration Tests (Pending)
```python
# backend/app/tests/test_tasks_api.py
def test_sync_endpoint_incremental()
def test_sync_endpoint_pagination()
def test_sync_endpoint_no_duplicates()
```

### Contract Tests (Pending)
- OpenAPI spec validation
- Response schema validation
- Frontend/backend parity checks

---

## 📖 Developer Notes

### How to Use Validators

```python
from app.schemas.content_types import ContentType
from app.services.content_validators import validate_content_request

# Example usage
payload = {
    "location": "Dubai Marina",
    "property_type": "apartment",
    "bedrooms": 2
}

result = validate_content_request(ContentType.CMA_REPORT, payload)

if not result.valid:
    # Return 422 with helpful hints
    return ValidationError422(
        detail=f"Missing required fields: {', '.join(result.missing_fields)}",
        missing_fields=result.missing_fields,
        hints=result.tips,
        suggested_defaults=result.normalized_payload,
        can_auto_heal=True
    )

# Use normalized payload
normalized = result.normalized_payload
```

### How to Create Tasks with Content Flags

```python
from backend.app.api.v1.tasks_router import TaskEntity

task = TaskEntity(
    title="CMA Report for Dubai Marina",
    type="CMA_REPORT",
    content_type="CMA_REPORT",
    has_content=True,
    export_formats=["pdf", "html"],
    created_by=user_id,
    assigned_to=[user_id]
)
```

### How to Query Sync Endpoint

```bash
# Initial sync (get all tasks)
curl "http://localhost:8000/api/v1/tasks/sync"

# Incremental sync (get only updated tasks)
curl "http://localhost:8000/api/v1/tasks/sync?since=2025-10-10T08:00:00Z"

# With pagination
curl "http://localhost:8000/api/v1/tasks/sync?since=2025-10-10T08:00:00Z&limit=25"
```

---

## 🚀 Next Actions

1. **Complete Export Service** (Track 1.4)
   - Create export router
   - Implement PDF/HTML exporters
   - Add share link generation

2. **Add Observability** (Track 1.5)
   - Structured logging
   - Request ID correlation
   - Metrics dashboard

3. **Security Hardening** (Track 1.6)
   - Rate limiting
   - Token signing
   - Input sanitization

4. **Database Migrations** (Track 1.7)
   - Task table updates
   - Exports table creation
   - Migration scripts

---

## 📝 Change Log

### 2025-10-10 - Initial Implementation
- Created `content_types.py` with all schemas
- Implemented `content_validators.py` with 5 validators
- Enhanced `tasks_router.py` with sync endpoint
- Added content generation fields to TaskEntity
- Updated documentation

---

## 🤝 Integration Points

### Frontend Integration
Frontend should import TypeScript equivalents of:
- `ContentType` enum
- `TaskResponse` interface
- `ValidationError422` interface

### Orchestrator Integration
Orchestrator should call validators before generation:
```typescript
const validation = await fetch('/api/v1/validate', {
  method: 'POST',
  body: JSON.stringify({ content_type, payload })
});

if (!validation.ok) {
  // Attempt enrichment or ask clarifying question
}
```

---

**Last Updated:** 2025-10-10T08:30:00Z  
**Track Lead:** Phase 3.2 Backend Team  
**Review Status:** ⏳ Pending code review
