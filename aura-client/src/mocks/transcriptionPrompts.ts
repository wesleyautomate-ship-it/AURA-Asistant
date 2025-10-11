/**
 * Mock Transcription Prompts
 * ==========================
 * 
 * Predefined transcription text samples for development and testing.
 * Used when AURA_MOCK_MODE=true for consistent UI testing without real audio.
 * 
 * These prompts simulate various real estate intelligence requests.
 */

export interface MockTranscriptionPrompt {
  text: string;
  mockType: string;
  description: string;
  contentType: string;
  expectedDuration: number; // Expected processing time in seconds
}

export const MOCK_PROMPTS: MockTranscriptionPrompt[] = [
  {
    text: "Prepare a detailed property valuation report for my client in Dubai Marina.",
    mockType: "cma_request",
    description: "CMA report generation request",
    contentType: "CMA_REPORT",
    expectedDuration: 30
  },
  {
    text: "Generate a comprehensive social media campaign for my luxury villa listing in Palm Jumeirah.",
    mockType: "social_campaign",
    description: "Social media content generation",
    contentType: "SOCIAL_POST",
    expectedDuration: 15
  },
  {
    text: "Create an investor pitch deck for a mixed-use development project in Downtown Dubai.",
    mockType: "pitch_deck",
    description: "Pitch deck presentation request",
    contentType: "PITCH_DECK",
    expectedDuration: 45
  },
  {
    text: "Analyze market trends and prepare a market report for Q4 2024 in the UAE real estate sector.",
    mockType: "market_analysis",
    description: "Market trend analysis request",
    contentType: "MARKET_REPORT",
    expectedDuration: 25
  },
  {
    text: "Draft a professional property description for a 3-bedroom apartment with marina views.",
    mockType: "property_description",
    description: "Property listing description",
    contentType: "PROPERTY_DESCRIPTION",
    expectedDuration: 10
  },
  {
    text: "Create a comprehensive listing strategy for a luxury penthouse in Business Bay.",
    mockType: "listing_strategy",
    description: "Strategic listing planning",
    contentType: "LISTING_STRATEGY",
    expectedDuration: 20
  },
  {
    text: "Generate an email marketing campaign to nurture leads for off-plan projects.",
    mockType: "email_campaign",
    description: "Email marketing content",
    contentType: "EMAIL_CAMPAIGN",
    expectedDuration: 18
  },
  {
    text: "Analyze the competitive landscape for luxury properties in Emirates Hills.",
    mockType: "competitive_analysis",
    description: "Competitive market analysis",
    contentType: "MARKET_REPORT",
    expectedDuration: 35
  },
  {
    text: "Create compelling marketing copy for a waterfront development in JBR.",
    mockType: "marketing_copy",
    description: "Marketing content creation",
    contentType: "GENERAL",
    expectedDuration: 12
  },
  {
    text: "Prepare a client presentation showcasing investment opportunities in Dubai's new districts.",
    mockType: "client_presentation",
    description: "Investment presentation",
    contentType: "PITCH_DECK",
    expectedDuration: 40
  }
];

/**
 * Simulate mock transcription with realistic delay
 * Temporary development mock – safe to remove for production.
 */
export const simulateMockTranscription = async (): Promise<string> => {
  // Simulate realistic transcription delay (1-1.5 seconds)
  const delay = 1000 + Math.random() * 500;
  await new Promise(resolve => setTimeout(resolve, delay));
  
  // Return random mock prompt text
  const prompt = getRandomPrompt();
  console.log(`[Mock Transcription] Generated: ${prompt.mockType} - ${prompt.text}`);
  return prompt.text;
};

/**
 * Get a random mock prompt
 */
export const getRandomPrompt = (): MockTranscriptionPrompt => {
  const randomIndex = Math.floor(Math.random() * MOCK_PROMPTS.length);
  return MOCK_PROMPTS[randomIndex];
};

/**
 * Get mock prompt by ID or random if not found
 */
export const getMockPrompt = (id?: string): MockTranscriptionPrompt => {
  if (id) {
    const prompt = MOCK_PROMPTS.find(p => p.mockType === id);
    if (prompt) return prompt;
  }
  return getRandomPrompt();
};

/**
 * Get prompts by content type
 */
export const getPromptsByType = (contentType: string): MockTranscriptionPrompt[] => {
  return MOCK_PROMPTS.filter(prompt => prompt.contentType === contentType);
};

/**
 * Get prompts by mock type
 */
export const getPromptsByMockType = (mockType: string): MockTranscriptionPrompt[] => {
  return MOCK_PROMPTS.filter(prompt => prompt.mockType === mockType);
};

/**
 * Simulate transcription confidence based on prompt complexity
 */
export const getConfidenceForPrompt = (prompt: MockTranscriptionPrompt): number => {
  // Longer, more complex prompts have slightly lower confidence
  const baseConfidence = 0.95;
  const lengthPenalty = Math.min(prompt.text.length / 1000, 0.1);
  return Math.max(baseConfidence - lengthPenalty, 0.85);
};

/**
 * Get prompt categories for UI filtering
 */
export const getPromptCategories = (): Array<{ label: string; value: string; count: number }> => {
  const categories = MOCK_PROMPTS.reduce((acc, prompt) => {
    if (!acc[prompt.contentType]) {
      acc[prompt.contentType] = 0;
    }
    acc[prompt.contentType]++;
    return acc;
  }, {} as Record<string, number>);

  return Object.entries(categories).map(([type, count]) => ({
    label: type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase()),
    value: type,
    count
  }));
};

/**
 * Legacy exports for backward compatibility
 */
export default MOCK_PROMPTS;