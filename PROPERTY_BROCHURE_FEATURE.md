# Property Brochure Generation Feature

## Overview

The Property Brochure Generation feature allows users to create professional, comprehensive property marketing brochures using AI. Users can simply ask "Create a brochure for [Property Name]" and receive a beautifully formatted, print-ready brochure with all property details, investment insights, and agent contact information.

## Features

### Core Capabilities
- **Intelligent Property Lookup**: Fuzzy matching to find properties by name
- **Auto-Description Generation**: Creates compelling descriptions for properties with missing content
- **Structured Content Generation**: Produces consistent, schema-validated brochures
- **Print-Ready Layout**: Professional formatting optimized for marketing use
- **Real-time Progress Tracking**: Live updates showing generation stages
- **Property Disambiguation**: Handles multiple matches with user selection

### Content Sections
Each generated brochure includes:
- Property title and subtitle
- Key selling highlights
- Detailed specifications (price, bedrooms, bathrooms, area, etc.)
- Categorized features (interior, exterior, building, community amenities)
- Neighborhood information and nearby attractions
- Investment insights and rental yield estimates
- Agent contact information
- Gallery image captions

## Usage

### Voice Mode
1. Click the microphone button in Aura
2. Say: "Create a brochure for Marina Heights Penthouse"
3. Wait for property lookup and generation
4. Review the formatted brochure

### Text Mode
1. Open the text input in Aura
2. Type: "Create a brochure for Marina Heights Penthouse"
3. Click Send
4. Review the generated brochure

### Property Disambiguation
If multiple properties match your query:
1. A selection dialog will appear
2. Choose the correct property from the list
3. Generation will continue automatically

## Setup Instructions

### Prerequisites
- Python 3.11+ (backend)
- Node.js 18+ (frontend)
- SQLite database with property listings

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Seed the database with sample properties:
   ```bash
   python scripts/seed_mock_listings.py
   ```

4. Configure environment variables:
   ```bash
   # For real AI generation
   export GEMINI_API_KEY=your_gemini_api_key
   export AI_MOCK_MODE=false
   
   # For testing/development
   export AI_MOCK_MODE=true
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd aura-client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Testing the Feature
1. Run the backend test suite:
   ```bash
   cd backend
   python test_brochure_simple.py
   ```

2. Open the frontend and test manually:
   - Navigate to the Aura interface
   - Try: "Create a brochure for Marina Heights Penthouse"
   - Verify all progress stages display correctly
   - Check that the final brochure renders properly

## API Documentation

### Content Generation Endpoint
**POST** `/api/v1/intelligence/generate`

Request body:
```json
{
  "user_input": "Create a brochure for Marina Heights Penthouse",
  "content_type": "PROPERTY_BROCHURE",
  "context": {
    "property_query": "Marina Heights Penthouse",
    "source": "voice_ui"
  }
}
```

Response:
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "message": "Brochure generation started"
}
```

### Progress Streaming
**GET** `/api/v1/intelligence/stream/{task_id}`

Server-sent events with progress updates:
```json
{
  "event": "progress",
  "task_id": "uuid-string",
  "status": "processing",
  "progress": 25,
  "stage": "building_prompt"
}
```

### Content Retrieval
**GET** `/api/v1/intelligence/content/{content_id}`

Response includes structured brochure data:
```json
{
  "content": {
    "content_type": "PROPERTY_BROCHURE",
    "generated_content": {
      "structured": {
        "type": "property_brochure",
        "title": "Marina Heights Penthouse",
        "specs": {
          "price_aed": "AED 4,200,000",
          "bedrooms": 3,
          "bathrooms": 4
        }
      }
    }
  }
}
```

## Architecture

### Backend Components
- **Intelligence Router**: Handles brochure generation requests
- **Task Orchestrator**: Manages the end-to-end brochure workflow
- **AI Content Generator**: Produces structured brochure content
- **Property Serializer**: Formats property data for AI consumption
- **SSE Streaming**: Real-time progress updates

### Frontend Components
- **CommandCenter**: Main UI for voice/text input
- **BrochureViewer**: Renders structured brochure content
- **PropertyDisambiguation**: Handles multiple property matches
- **ProgressTracker**: Shows generation progress stages
- **ContentViewer**: Displays completed brochures

### Progress Stages
1. **Init (5%)**: Preparing brochure generation
2. **Property Lookup (15%)**: Finding property in database
3. **Building Prompt (25%)**: Gathering property information
4. **Generating (60%)**: AI content creation
5. **Formatting (90%)**: Structuring final output
6. **Completed (100%)**: Brochure ready

## Configuration

### Feature Flags
Enable/disable the brochure feature:
```bash
export ENABLE_BROCHURE_GEN=true
```

### Mock Mode
For development and testing:
```bash
export AI_MOCK_MODE=true  # Uses deterministic mock content
export AI_MOCK_MODE=false # Uses real Gemini API
```

### Content Type Detection
The system automatically detects brochure requests from keywords:
- "brochure"
- "flyer" 
- "listing brochure"
- "property brochure"
- "marketing brochure"

## Troubleshooting

### Common Issues

**Property Not Found**
- Ensure the property exists in the database
- Check property title spelling
- Use the seed script to add sample data

**Generation Fails**
- Check Gemini API key configuration
- Verify AI_MOCK_MODE setting
- Review backend logs for errors

**Progress Not Updating**
- Confirm SSE streaming is working
- Check network connectivity
- Verify task ID is valid

**Brochure Not Displaying**
- Check ContentViewer integration
- Verify structured data format
- Review browser console for errors

## Future Enhancements

### Planned Features
- PDF export functionality
- Template customization options
- Bulk brochure generation
- Integration with image galleries
- Multi-language support
- Brand customization

### Performance Optimizations
- Property lookup caching
- Brochure template pre-generation
- Optimized image handling
- Parallel content generation

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs for error details
3. Test with mock mode first
4. Verify all dependencies are installed correctly

## Contributing

When contributing to this feature:
1. Run all tests: `python test_brochure_simple.py`
2. Test both mock and real AI modes
3. Verify frontend components work correctly
4. Check SSE streaming functionality
5. Update documentation as needed