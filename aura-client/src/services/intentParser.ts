// Intent Detection System for Aura Command Center
// Analyzes user prompts and determines the appropriate action type

export type IntentType = 'CMA' | 'MARKET_REPORT' | 'SOCIAL_POST' | 'PITCH_DECK' | 'BROCHURE' | 'GENERIC';

export interface Intent {
  type: IntentType;
  location?: string;
  topic?: string;
  building?: string;
  beds?: number;
  unit?: string;
  confidence: number;
}

// Keyword patterns for each intent type
const keywords = {
  CMA: ['cma', 'valuation', 'market analysis', 'pricing', 'property value', 'appraisal', 'comparative market'],
  MARKET_REPORT: ['report', 'trend', 'analysis', 'market data', 'statistics', 'insights', 'market overview', 'sales data'],
  SOCIAL_POST: ['instagram', 'social', 'post', 'facebook', 'listing', 'marketing content', 'social media', 'tweet', 'linkedin'],
  PITCH_DECK: ['pitch', 'deck', 'presentation', 'investor', 'investment', 'slides', 'pitch deck'],
  BROCHURE: ['brochure', 'flyer', 'listing brochure', 'marketing brochure', 'property brochure', 'create brochure'],
};

// Location extraction patterns
const locationPatterns = [
  /(?:in|for|at)\s+([A-Z][A-Za-z\s]+?)(?:\s+with|\s+for|\s*$|[,.])/i,
  /([A-Z][A-Za-z\s]+?)\s+(?:market|area|region|district)/i,
];

/**
 * Extract location from prompt text
 */
function extractLocation(prompt: string): string {
  for (const pattern of locationPatterns) {
    const match = prompt.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }
  
  // Default locations based on common patterns
  if (prompt.toLowerCase().includes('downtown')) return 'Downtown Dubai';
  if (prompt.toLowerCase().includes('marina')) return 'Dubai Marina';
  if (prompt.toLowerCase().includes('palm')) return 'Palm Jumeirah';
  if (prompt.toLowerCase().includes('business bay')) return 'Business Bay';
  
  return 'Dubai'; // Fallback
}

/**
 * Extract building name from prompt
 */
function extractBuilding(prompt: string): string | undefined {
  // Common Dubai buildings
  const buildings = [
    'Orla Residences', 'Six Senses', 'Address Downtown', 'Burj Khalifa',
    'Emirates Hills', 'Dubai Hills', 'City Walk', 'Business Bay',
    'Marina Gate', 'JBR', 'Palm Jumeirah'
  ];
  
  const lower = prompt.toLowerCase();
  for (const building of buildings) {
    if (lower.includes(building.toLowerCase())) {
      return building;
    }
  }
  
  // Try to extract building name patterns like "at [Building Name]"
  const buildingMatch = prompt.match(/(?:at|in)\s+([A-Z][A-Za-z\s]+?)(?:\s+on|\s+with|\s*$|[,.])/i);
  if (buildingMatch && buildingMatch[1]) {
    return buildingMatch[1].trim();
  }
  
  return undefined;
}

/**
 * Extract number of bedrooms from prompt
 */
function extractBeds(prompt: string): number | undefined {
  // Match patterns like "2BR", "3-bedroom", "2 bedroom", "3 bed"
  const bedMatch = prompt.match(/(\d+)\s*(?:br|bed|bedroom)/i);
  if (bedMatch && bedMatch[1]) {
    return parseInt(bedMatch[1], 10);
  }
  return undefined;
}

/**
 * Extract unit information from prompt
 */
function extractUnit(prompt: string): string | undefined {
  // Match patterns like "Unit 1803", "unit 2A"
  const unitMatch = prompt.match(/unit\s+([A-Za-z0-9]+)/i);
  if (unitMatch && unitMatch[1]) {
    return unitMatch[1];
  }
  return undefined;
}

/**
 * Extract topic from social media prompts
 */
function extractTopic(prompt: string): string {
  const lower = prompt.toLowerCase();
  
  if (lower.includes('villa')) return 'luxury villa listing';
  if (lower.includes('apartment')) return 'apartment listing';
  if (lower.includes('penthouse')) return 'penthouse showcase';
  if (lower.includes('commercial')) return 'commercial property';
  if (lower.includes('listing')) return 'new listing announcement';
  
  return 'property update'; // Fallback
}

/**
 * Calculate confidence score based on keyword matches
 */
function calculateConfidence(prompt: string, keywords: string[]): number {
  const lower = prompt.toLowerCase();
  const matches = keywords.filter(keyword => lower.includes(keyword));
  
  if (matches.length === 0) return 0;
  if (matches.length === 1) return 0.6;
  if (matches.length === 2) return 0.8;
  return 0.9;
}

/**
 * Detect user intent from prompt text
 * Returns the most confident intent with metadata
 */
export function detectIntent(prompt: string): Intent {
  // Calculate confidence for each intent type
  const cmaConfidence = calculateConfidence(prompt, keywords.CMA);
  const reportConfidence = calculateConfidence(prompt, keywords.MARKET_REPORT);
  const socialConfidence = calculateConfidence(prompt, keywords.SOCIAL_POST);
  const pitchDeckConfidence = calculateConfidence(prompt, keywords.PITCH_DECK);
  const brochureConfidence = calculateConfidence(prompt, keywords.BROCHURE);
  
  // Find highest confidence intent (minimum 0.6 threshold)
  const confidences = [
    { type: 'CMA' as const, confidence: cmaConfidence },
    { type: 'MARKET_REPORT' as const, confidence: reportConfidence },
    { type: 'SOCIAL_POST' as const, confidence: socialConfidence },
    { type: 'PITCH_DECK' as const, confidence: pitchDeckConfidence },
    { type: 'BROCHURE' as const, confidence: brochureConfidence },
  ];
  
  const bestMatch = confidences.reduce((prev, curr) => 
    curr.confidence > prev.confidence ? curr : prev
  );
  
  // If confidence is too low, return GENERIC
  if (bestMatch.confidence < 0.6) {
    console.log('[Intent] No strong match, using GENERIC');
    return { type: 'GENERIC', confidence: 0.5 };
  }
  
  // Build specific intent with metadata
  console.log(`[Intent] Detected ${bestMatch.type} with confidence ${bestMatch.confidence}`);
  
  switch (bestMatch.type) {
    case 'CMA':
      return {
        type: 'CMA',
        location: extractLocation(prompt),
        confidence: bestMatch.confidence,
      };
    
    case 'MARKET_REPORT':
      return {
        type: 'MARKET_REPORT',
        location: extractLocation(prompt),
        confidence: bestMatch.confidence,
      };
    
    case 'SOCIAL_POST':
      return {
        type: 'SOCIAL_POST',
        topic: extractTopic(prompt),
        confidence: bestMatch.confidence,
      };
    
    case 'PITCH_DECK':
      return {
        type: 'PITCH_DECK',
        location: extractLocation(prompt),
        topic: extractTopic(prompt),
        confidence: bestMatch.confidence,
      };
    
    case 'BROCHURE':
      return {
        type: 'BROCHURE',
        building: extractBuilding(prompt),
        beds: extractBeds(prompt),
        unit: extractUnit(prompt),
        confidence: bestMatch.confidence,
      };
    
    default:
      return { type: 'GENERIC', confidence: 0.5 };
  }
}

/**
 * Format intent as human-readable description
 */
export function formatIntentDescription(intent: Intent): string {
  switch (intent.type) {
    case 'CMA':
      return `CMA Report for ${intent.location}`;
    case 'MARKET_REPORT':
      return `Market Analysis for ${intent.location}`;
    case 'SOCIAL_POST':
      return `Social Media: ${intent.topic}`;
    case 'PITCH_DECK':
      return `Investor Pitch Deck for ${intent.location}`;
    case 'BROCHURE':
      const building = intent.building || 'Property';
      const beds = intent.beds ? `${intent.beds}BR ` : '';
      return `Property Brochure: ${beds}${building}`;
    case 'GENERIC':
      return 'AI Assistant';
    default:
      return 'Unknown Task';
  }
}
