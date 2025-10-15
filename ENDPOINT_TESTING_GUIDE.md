# API Endpoint Testing Guide
## Newsletter & Pitch Deck Generation

**Date:** 2025  
**Version:** 1.0.0  
**Purpose:** Complete testing guide for the newly implemented Newsletter and Pitch Deck API endpoints

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Newsletter Endpoints](#newsletter-endpoints)
3. [Pitch Deck Endpoints](#pitch-deck-endpoints)
4. [Integration Testing](#integration-testing)
5. [Frontend Testing](#frontend-testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Environment Setup

```bash
# Start the backend server
cd C:\Dev\RealtorProAI\Realtor-assistant\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Authentication Token

All requests require a valid JWT token. First, obtain a token:

```bash
# Login to get auth token (replace with your credentials)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "your-email@example.com",
    "role": "agent"
  }
}
```

Save the `access_token` for use in subsequent requests:
```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Newsletter Endpoints

### 1. Generate Newsletter

**Endpoint:** `POST /api/v1/newsletter/generate`

**Purpose:** Generate a real estate newsletter with market updates and property listings.

#### Test Case 1: Basic Market Update Newsletter

```bash
curl -X POST http://localhost:8000/api/v1/newsletter/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dubai Marina Market Update - January 2025",
    "content_type": "market_update",
    "target_audience": "buyers",
    "include_market_data": true,
    "include_featured_listings": true,
    "location_focus": "Dubai Marina",
    "output_formats": ["html", "pdf"]
  }'
```

**Expected Response (200 OK):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Dubai Marina Market Update - January 2025",
  "content_type": "market_update",
  "target_audience": "buyers",
  "status": "processing",
  "message": "Newsletter 'Dubai Marina Market Update - January 2025' generation started. Processing 5 properties.",
  "estimated_completion": "5-8 minutes",
  "check_status_url": "/api/v1/newsletter/550e8400-e29b-41d4-a716-446655440000/status",
  "created_at": "2025-01-10T14:30:00Z"
}
```

#### Test Case 2: Property Showcase Newsletter

```bash
curl -X POST http://localhost:8000/api/v1/newsletter/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Featured Luxury Properties This Week",
    "content_type": "property_showcase",
    "target_audience": "investors",
    "include_market_data": false,
    "include_featured_listings": true,
    "featured_property_ids": [101, 102, 103],
    "custom_message": "Exclusive investment opportunities in prime Dubai locations.",
    "output_formats": ["html"]
  }'
```

**Expected Response (200 OK):**
```json
{
  "task_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Featured Luxury Properties This Week",
  "content_type": "property_showcase",
  "target_audience": "investors",
  "status": "processing",
  "message": "Newsletter 'Featured Luxury Properties This Week' generation started. Processing 3 properties.",
  "estimated_completion": "5-8 minutes",
  "check_status_url": "/api/v1/newsletter/660e8400-e29b-41d4-a716-446655440001/status",
  "created_at": "2025-01-10T14:35:00Z"
}
```

#### Test Case 3: Validation Error - Missing Required Field

```bash
curl -X POST http://localhost:8000/api/v1/newsletter/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "market_update",
    "target_audience": "buyers"
  }'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 2. Check Newsletter Status

**Endpoint:** `GET /api/v1/newsletter/{task_id}/status`

```bash
curl -X GET http://localhost:8000/api/v1/newsletter/550e8400-e29b-41d4-a716-446655440000/status \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK - In Progress):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "title": "Dubai Marina Market Update - January 2025",
  "content_type": "market_update",
  "created_at": "2025-01-10T14:30:00Z",
  "completed_at": null,
  "output": null,
  "error": null
}
```

**Expected Response (200 OK - Completed):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "title": "Dubai Marina Market Update - January 2025",
  "content_type": "market_update",
  "created_at": "2025-01-10T14:30:00Z",
  "completed_at": "2025-01-10T14:37:00Z",
  "output": {
    "html_content": "<html>...</html>",
    "pdf_url": "/downloads/newsletter_550e8400.pdf",
    "subject_line": "Dubai Marina Market Update - January 2025",
    "preview_text": "Latest market trends and featured properties..."
  },
  "error": null
}
```

---

### 3. List Newsletter Templates

**Endpoint:** `GET /api/v1/newsletter/templates`

```bash
curl -X GET http://localhost:8000/api/v1/newsletter/templates \
  -H "Authorization: Bearer $TOKEN"
```

**With Filters:**
```bash
curl -X GET "http://localhost:8000/api/v1/newsletter/templates?content_type=market_update" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "market_update_professional",
    "name": "Professional Market Update",
    "description": "Clean, data-driven layout perfect for market statistics and trends",
    "content_type": "market_update",
    "preview_image_url": "/templates/previews/market_update_pro.png",
    "suitable_for": ["buyers", "sellers", "investors", "all_clients"]
  },
  {
    "id": "property_showcase_luxury",
    "name": "Luxury Property Showcase",
    "description": "Elegant layout highlighting premium properties with large images",
    "content_type": "property_showcase",
    "preview_image_url": "/templates/previews/property_showcase_lux.png",
    "suitable_for": ["buyers", "investors"]
  }
]
```

---

### 4. Cancel Newsletter Task

**Endpoint:** `DELETE /api/v1/newsletter/{task_id}`

```bash
curl -X DELETE http://localhost:8000/api/v1/newsletter/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "Newsletter generation task cancelled successfully"
}
```

---

### 5. Newsletter Health Check

**Endpoint:** `GET /api/v1/newsletter/health`

```bash
curl -X GET http://localhost:8000/api/v1/newsletter/health
```

**Expected Response (200 OK):**
```json
{
  "service": "Newsletter Generation",
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-10T14:45:00.123456"
}
```

---

## Pitch Deck Endpoints

### 1. Generate Pitch Deck

**Endpoint:** `POST /api/v1/pitchdeck/generate`

**Purpose:** Generate a professional property pitch deck presentation.

#### Test Case 1: Buyer-Focused Pitch Deck

```bash
curl -X POST http://localhost:8000/api/v1/pitchdeck/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 101,
    "target_audience": "buyer",
    "presentation_style": "professional",
    "include_sections": [
      "cover",
      "property_overview",
      "location",
      "amenities",
      "neighborhood",
      "call_to_action"
    ],
    "include_financial_projections": false,
    "include_comparable_properties": true,
    "output_formats": ["pdf"]
  }'
```

**Expected Response (200 OK):**
```json
{
  "task_id": "770e8400-e29b-41d4-a716-446655440002",
  "property_id": 101,
  "property_title": "Luxury Penthouse in Dubai Marina",
  "target_audience": "buyer",
  "presentation_style": "professional",
  "status": "processing",
  "message": "Pitch deck generation started for 'Luxury Penthouse in Dubai Marina'. Creating 6 slides.",
  "estimated_completion": "3-5 minutes",
  "check_status_url": "/api/v1/pitchdeck/770e8400-e29b-41d4-a716-446655440002/status",
  "created_at": "2025-01-10T14:50:00Z"
}
```

#### Test Case 2: Investor-Focused Pitch Deck with Financials

```bash
curl -X POST http://localhost:8000/api/v1/pitchdeck/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 102,
    "target_audience": "investor",
    "presentation_style": "modern",
    "include_sections": [
      "cover",
      "property_overview",
      "market_analysis",
      "investment_highlights",
      "financials",
      "comparable_properties",
      "call_to_action"
    ],
    "include_financial_projections": true,
    "include_comparable_properties": true,
    "custom_message": "Prime investment opportunity with strong ROI potential.",
    "output_formats": ["pdf", "pptx"]
  }'
```

**Expected Response (200 OK):**
```json
{
  "task_id": "880e8400-e29b-41d4-a716-446655440003",
  "property_id": 102,
  "property_title": "Premium Office Space in Business Bay",
  "target_audience": "investor",
  "presentation_style": "modern",
  "status": "processing",
  "message": "Pitch deck generation started for 'Premium Office Space in Business Bay'. Creating 7 slides.",
  "estimated_completion": "3-5 minutes",
  "check_status_url": "/api/v1/pitchdeck/880e8400-e29b-41d4-a716-446655440003/status",
  "created_at": "2025-01-10T14:55:00Z"
}
```

#### Test Case 3: Validation Error - Invalid Property ID

```bash
curl -X POST http://localhost:8000/api/v1/pitchdeck/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 99999,
    "target_audience": "buyer",
    "presentation_style": "professional"
  }'
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Property 99999 not found"
}
```

#### Test Case 4: Validation Error - Invalid Sections

```bash
curl -X POST http://localhost:8000/api/v1/pitchdeck/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 101,
    "target_audience": "buyer",
    "include_sections": ["invalid_section", "another_bad_section"]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "Invalid sections: ['invalid_section', 'another_bad_section']. Valid options: ['cover', 'property_overview', 'location', 'amenities', 'market_analysis', 'investment_highlights', 'financials', 'comparable_properties', 'neighborhood', 'call_to_action']"
}
```

---

### 2. Check Pitch Deck Status

**Endpoint:** `GET /api/v1/pitchdeck/{task_id}/status`

```bash
curl -X GET http://localhost:8000/api/v1/pitchdeck/770e8400-e29b-41d4-a716-446655440002/status \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK - Completed):**
```json
{
  "task_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "completed",
  "progress": 100,
  "property_id": 101,
  "property_title": "Luxury Penthouse in Dubai Marina",
  "target_audience": "buyer",
  "created_at": "2025-01-10T14:50:00Z",
  "completed_at": "2025-01-10T14:54:00Z",
  "output": {
    "slides_generated": 6,
    "total_pages": 6,
    "presentation_title": "Luxury Penthouse in Dubai Marina - Property Presentation"
  },
  "download_urls": {
    "pdf": "/downloads/pitchdeck_770e8400.pdf",
    "preview_images": [
      "/downloads/pitchdeck_770e8400_slide_1.png",
      "/downloads/pitchdeck_770e8400_slide_2.png"
    ]
  },
  "error": null
}
```

---

### 3. List Pitch Deck Templates

**Endpoint:** `GET /api/v1/pitchdeck/templates`

```bash
curl -X GET http://localhost:8000/api/v1/pitchdeck/templates \
  -H "Authorization: Bearer $TOKEN"
```

**With Filters:**
```bash
curl -X GET "http://localhost:8000/api/v1/pitchdeck/templates?style=luxury&target_audience=investor" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "professional_buyer",
    "name": "Professional Buyer Presentation",
    "description": "Classic business presentation highlighting property features and lifestyle",
    "style": "professional",
    "preview_image_url": "/templates/previews/professional_buyer.png",
    "suitable_for": ["buyer"],
    "included_sections": ["cover", "property_overview", "location", "amenities", "neighborhood", "call_to_action"]
  },
  {
    "id": "investor_analysis",
    "name": "Investor Analysis Deck",
    "description": "Data-driven presentation with financial projections and ROI analysis",
    "style": "professional",
    "preview_image_url": "/templates/previews/investor_analysis.png",
    "suitable_for": ["investor"],
    "included_sections": ["cover", "property_overview", "market_analysis", "investment_highlights", "financials", "comparable_properties", "call_to_action"]
  }
]
```

---

### 4. Cancel Pitch Deck Task

**Endpoint:** `DELETE /api/v1/pitchdeck/{task_id}`

```bash
curl -X DELETE http://localhost:8000/api/v1/pitchdeck/770e8400-e29b-41d4-a716-446655440002 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "task_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "cancelled",
  "message": "Pitch deck generation task cancelled successfully"
}
```

---

### 5. Pitch Deck Health Check

**Endpoint:** `GET /api/v1/pitchdeck/health`

```bash
curl -X GET http://localhost:8000/api/v1/pitchdeck/health
```

**Expected Response (200 OK):**
```json
{
  "service": "Pitch Deck Generation",
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-10T15:00:00.123456"
}
```

---

## Integration Testing

### Full Workflow Test: Newsletter Generation

```bash
# Step 1: Generate newsletter
NEWSLETTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/newsletter/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Integration Test Newsletter",
    "content_type": "market_update",
    "target_audience": "all_clients",
    "include_market_data": true,
    "include_featured_listings": true,
    "output_formats": ["html"]
  }')

TASK_ID=$(echo $NEWSLETTER_RESPONSE | jq -r '.task_id')
echo "Newsletter task created: $TASK_ID"

# Step 2: Poll for completion
while true; do
  STATUS_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/newsletter/$TASK_ID/status \
    -H "Authorization: Bearer $TOKEN")
  
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
  PROGRESS=$(echo $STATUS_RESPONSE | jq -r '.progress')
  
  echo "Status: $STATUS | Progress: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  
  sleep 5
done

# Step 3: Display result
echo "Final result:"
echo $STATUS_RESPONSE | jq
```

---

### Full Workflow Test: Pitch Deck Generation

```bash
# Step 1: Generate pitch deck
PITCHDECK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/pitchdeck/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 101,
    "target_audience": "investor",
    "presentation_style": "professional",
    "include_financial_projections": true,
    "output_formats": ["pdf"]
  }')

TASK_ID=$(echo $PITCHDECK_RESPONSE | jq -r '.task_id')
echo "Pitch deck task created: $TASK_ID"

# Step 2: Poll for completion
while true; do
  STATUS_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/pitchdeck/$TASK_ID/status \
    -H "Authorization: Bearer $TOKEN")
  
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
  PROGRESS=$(echo $STATUS_RESPONSE | jq -r '.progress')
  
  echo "Status: $STATUS | Progress: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  
  sleep 5
done

# Step 3: Display result and download URLs
echo "Final result:"
echo $STATUS_RESPONSE | jq
echo "Download URLs:"
echo $STATUS_RESPONSE | jq '.download_urls'
```

---

## Frontend Testing

### Testing from AURA Frontend

Navigate to the AURA content generation interface and test through the UI:

```bash
cd C:\Dev\RealtorProAI\Realtor-assistant\aura-client
npm run dev
```

#### Test Checklist:

**Newsletter Generation:**
- [ ] Open content generation modal
- [ ] Select "Newsletter" content type
- [ ] Fill in title and select options
- [ ] Submit generation request
- [ ] Verify task appears in task sync
- [ ] Monitor progress updates
- [ ] Confirm completion notification
- [ ] Download generated newsletter

**Pitch Deck Generation:**
- [ ] Open content generation modal
- [ ] Select "Pitch Deck" content type
- [ ] Choose a property
- [ ] Select target audience and style
- [ ] Submit generation request
- [ ] Verify task appears in task sync
- [ ] Monitor progress updates
- [ ] Confirm completion notification
- [ ] Download generated pitch deck

---

## Troubleshooting

### Common Issues

#### 1. 404 Not Found

**Problem:** Endpoint returns 404
**Solution:** Verify backend server is running and routers are registered in `main.py`

```bash
# Check server logs
tail -f backend/logs/app.log

# Verify routers are loaded
curl http://localhost:8000/docs
```

#### 2. 422 Validation Error

**Problem:** Request payload validation fails
**Solution:** Check request schema against Pydantic models

```bash
# View full validation error details
curl -v -X POST http://localhost:8000/api/v1/newsletter/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "invalid": "data" }' | jq
```

#### 3. 401 Unauthorized

**Problem:** Authentication token expired or invalid
**Solution:** Re-authenticate and obtain new token

```bash
# Login again
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "password": "your-password"}'
```

#### 4. 500 Internal Server Error

**Problem:** Backend error during processing
**Solution:** Check backend logs for stack traces

```bash
# View detailed logs
tail -50 backend/logs/app.log

# Check for database connection issues
curl http://localhost:8000/health
```

#### 5. Task Status Never Completes

**Problem:** Task remains in "processing" status indefinitely
**Solution:** Check AI orchestrator and background workers

```bash
# Check orchestrator health
curl http://localhost:8000/api/v1/orchestration/health

# Verify task queue
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

---

## Success Criteria

### Newsletter Endpoint Tests ✓
- [ ] POST /api/v1/newsletter/generate returns 200 with valid payload
- [ ] GET /api/v1/newsletter/{task_id}/status returns task progress
- [ ] GET /api/v1/newsletter/templates returns template list
- [ ] DELETE /api/v1/newsletter/{task_id} cancels task
- [ ] Validation errors return 422 with proper error messages
- [ ] Unauthorized requests return 401

### Pitch Deck Endpoint Tests ✓
- [ ] POST /api/v1/pitchdeck/generate returns 200 with valid payload
- [ ] GET /api/v1/pitchdeck/{task_id}/status returns task progress
- [ ] GET /api/v1/pitchdeck/templates returns template list
- [ ] DELETE /api/v1/pitchdeck/{task_id} cancels task
- [ ] Validation errors return 422 with proper error messages
- [ ] Invalid property ID returns 404

### Integration Tests ✓
- [ ] Frontend can successfully call both endpoints
- [ ] Task sync displays both content types correctly
- [ ] Progress updates work in real-time
- [ ] Download URLs are accessible
- [ ] Error handling works end-to-end

---

## Next Steps

1. ✅ Verify all endpoints return expected responses
2. ✅ Test with frontend orchestrator integration
3. ✅ Validate error handling for edge cases
4. ✅ Load test endpoints with multiple concurrent requests
5. ✅ Document any issues in GitHub/tracking system

---

**Testing Completed:** _________  
**Verified By:** _________  
**Status:** ✅ Ready for Production / ⚠️ Issues Found / ❌ Blocked

---

*Generated for PropertyPro AI AURA System v2.7.1*
