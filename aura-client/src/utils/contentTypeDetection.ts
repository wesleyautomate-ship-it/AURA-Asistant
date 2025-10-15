/**
 * Content Type Detection Utilities
 * ================================
 * 
 * Frontend utilities for detecting content type from user input
 * and extracting context information for better content generation.
 */

import { ContentType } from '../types/intelligence';

export interface ContentDetectionResult {
  contentType: ContentType;
  confidence: number;
  extractedContext?: { [key: string]: any };
}

/**
 * Detect content type from user input text
 */
export function detectContentType(userInput: string): ContentDetectionResult {
  const input = userInput.toLowerCase().trim();

  // Property brochure detection - highest priority for specific real estate content
  if (hasBrochureIntent(input)) {
    const propertyQuery = extractPropertyQuery(input);
    return {
      contentType: ContentType.PROPERTY_BROCHURE,
      confidence: 0.9,
      extractedContext: propertyQuery ? { property_query: propertyQuery } : undefined
    };
  }

  // CMA report detection
  if (hasCMAIntent(input)) {
    return {
      contentType: ContentType.CMA_REPORT,
      confidence: 0.85
    };
  }

  // Social media post detection
  if (hasSocialIntent(input)) {
    return {
      contentType: ContentType.SOCIAL_POST,
      confidence: 0.8
    };
  }

  // Pitch deck detection
  if (hasPitchDeckIntent(input)) {
    return {
      contentType: ContentType.PITCH_DECK,
      confidence: 0.8
    };
  }

  // Market report detection
  if (hasMarketReportIntent(input)) {
    return {
      contentType: ContentType.MARKET_REPORT,
      confidence: 0.75
    };
  }

  // Property description detection
  if (hasPropertyDescriptionIntent(input)) {
    return {
      contentType: ContentType.PROPERTY_DESCRIPTION,
      confidence: 0.7
    };
  }

  // Default to general
  return {
    contentType: ContentType.GENERAL,
    confidence: 0.5
  };
}

/**
 * Check if input has property brochure intent
 */
function hasBrochureIntent(input: string): boolean {
  const brochureKeywords = [
    'brochure',
    'flyer', 
    'property brochure',
    'listing brochure',
    'marketing brochure',
    'property flyer',
    'listing flyer',
    'marketing flyer'
  ];

  return brochureKeywords.some(keyword => input.includes(keyword));
}

/**
 * Check if input has CMA intent
 */
function hasCMAIntent(input: string): boolean {
  const cmaKeywords = [
    'cma',
    'comparative market analysis',
    'market analysis',
    'valuation',
    'property valuation',
    'market comparison',
    'comparable properties',
    'comps'
  ];

  return cmaKeywords.some(keyword => input.includes(keyword));
}

/**
 * Check if input has social media intent
 */
function hasSocialIntent(input: string): boolean {
  const socialKeywords = [
    'social media',
    'social post',
    'instagram',
    'facebook',
    'twitter',
    'linkedin',
    'social campaign',
    'post'
  ];

  return socialKeywords.some(keyword => input.includes(keyword));
}

/**
 * Check if input has pitch deck intent
 */
function hasPitchDeckIntent(input: string): boolean {
  const pitchKeywords = [
    'pitch deck',
    'presentation',
    'investor presentation',
    'investment pitch',
    'pitch',
    'slides',
    'deck'
  ];

  return pitchKeywords.some(keyword => input.includes(keyword));
}

/**
 * Check if input has market report intent
 */
function hasMarketReportIntent(input: string): boolean {
  const marketKeywords = [
    'market report',
    'market trend',
    'market overview',
    'market analysis',
    'trend analysis',
    'market conditions'
  ];

  return marketKeywords.some(keyword => input.includes(keyword));
}

/**
 * Check if input has property description intent
 */
function hasPropertyDescriptionIntent(input: string): boolean {
  const descriptionKeywords = [
    'property description',
    'listing description',
    'describe property',
    'property copy',
    'listing copy'
  ];

  return descriptionKeywords.some(keyword => input.includes(keyword));
}

/**
 * Extract property name/query from user input
 */
export function extractPropertyQuery(userInput: string): string | null {
  // Look for patterns like "for [Property Name]" or quoted property names
  const patterns = [
    /\bfor\s+([A-Z][A-Za-z\s]+(?:Penthouse|Villa|Apartment|Townhouse|Studio))/i,
    /\bfor\s+"([^"]+)"/i,
    /\bfor\s+'([^']+)'/i,
    /\b(Marina Heights[A-Za-z\s]*)/i,
    /\b(Downtown Dubai[A-Za-z\s]*)/i,
    /\b(Palm Jumeirah[A-Za-z\s]*)/i,
    /\b(Business Bay[A-Za-z\s]*)/i,
    /\b(Jumeirah Beach[A-Za-z\s]*)/i
  ];

  for (const pattern of patterns) {
    const match = userInput.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }

  // Fallback: look for the longest capitalized phrase
  const words = userInput.split(/\s+/);
  const capitalizedPhrases: string[] = [];
  let currentPhrase: string[] = [];

  for (const word of words) {
    if (word.length > 2 && /^[A-Z]/.test(word)) {
      currentPhrase.push(word);
    } else {
      if (currentPhrase.length > 0) {
        capitalizedPhrases.push(currentPhrase.join(' '));
        currentPhrase = [];
      }
    }
  }

  if (currentPhrase.length > 0) {
    capitalizedPhrases.push(currentPhrase.join(' '));
  }

  // Return the longest capitalized phrase
  return capitalizedPhrases.length > 0 
    ? capitalizedPhrases.reduce((longest, current) => 
        current.length > longest.length ? current : longest
      )
    : null;
}

/**
 * Get user-friendly content type description
 */
export function getContentTypeDescription(contentType: ContentType): string {
  const descriptions = {
    [ContentType.CMA_REPORT]: 'A comprehensive market analysis with comparable properties and pricing insights',
    [ContentType.PROPERTY_BROCHURE]: 'A professional property marketing brochure with specifications and features',
    [ContentType.SOCIAL_POST]: 'Engaging social media content optimized for real estate marketing',
    [ContentType.PITCH_DECK]: 'An investment presentation with financial modeling and market positioning',
    [ContentType.MARKET_REPORT]: 'A detailed market analysis with trends and forecasting',
    [ContentType.PROPERTY_DESCRIPTION]: 'Compelling property listing descriptions and marketing copy',
    [ContentType.LISTING_STRATEGY]: 'Strategic marketing plans for property listings',
    [ContentType.EMAIL_CAMPAIGN]: 'Email marketing campaigns with segmentation and automation',
    [ContentType.GENERAL]: 'General AI assistance and content generation'
  };

  return descriptions[contentType] || 'AI-generated content';
}

/**
 * Check if a content type requires property context
 */
export function requiresPropertyContext(contentType: ContentType): boolean {
  return [
    ContentType.PROPERTY_BROCHURE,
    ContentType.PROPERTY_DESCRIPTION,
    ContentType.CMA_REPORT
  ].includes(contentType);
}