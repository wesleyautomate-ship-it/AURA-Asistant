/**
 * Track 3 Integration Tests
 * ==========================
 * 
 * Comprehensive tests for the full content generation pipeline
 * Tests all 5 services: normalizer, validator, enricher, saver, orchestrator
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { normalizeIntent } from '../intentNormalizer';
import { validatePayload, buildPayload } from '../validationService';
import { enrichPayload } from '../enrichmentService';
import { saveGeneratedContent } from '../contentSaveService';
import { generateContent } from '../orchestratorService';
import { ContentType } from '../../types/contentSchemas';

// Mock fetch for API calls
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Track 3: Pipeline Integration Tests', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  describe('Intent Normalizer', () => {
    it('should normalize CMA request correctly', async () => {
      const result = await normalizeIntent({
        userInput: 'Create a CMA report for 123 Main St, Seattle',
        requestId: 'test_001',
      });

      expect(result.contentType).toBe(ContentType.CMA_REPORT);
      expect(result.entities.address).toBe('123 Main St, Seattle');
      expect(result.confidence).toBeGreaterThan(0.7);
      expect(result.rawIntent).toBe('Create a CMA report for 123 Main St, Seattle');
    });

    it('should normalize pitch deck request correctly', async () => {
      const result = await normalizeIntent({
        userInput: 'Generate a pitch deck for luxury property investment',
        requestId: 'test_002',
      });

      expect(result.contentType).toBe(ContentType.PITCH_DECK);
      expect(result.entities.investmentType).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0.6);
    });

    it('should throw error for unclear intent', async () => {
      await expect(
        normalizeIntent({
          userInput: 'hello world random text',
          requestId: 'test_003',
        })
      ).rejects.toThrow('Unable to determine content type');
    });

    it('should extract entities from complex prompt', async () => {
      const result = await normalizeIntent({
        userInput: 'CMA for 456 Oak Ave with 5 comps from last 6 months',
        requestId: 'test_004',
      });

      expect(result.entities.address).toContain('456 Oak Ave');
      expect(result.entities.comparableCount).toBe(5);
      expect(result.entities.dateRange).toBe('6_months');
    });
  });

  describe('Validation Service', () => {
    it('should build payload from normalized intent', () => {
      const normalized = {
        contentType: ContentType.CMA_REPORT,
        entities: {
          address: '123 Main St',
          propertyType: 'single_family',
        },
        confidence: 0.9,
        rawIntent: 'test',
        requestId: 'test_005',
        inferredFrom: [],
        missingFields: [],
        canAutoFill: true,
      };

      const payload = buildPayload(normalized);

      expect(payload.address).toBe('123 Main St');
      expect(payload.property_type).toBe('single_family');
      expect(payload.comparable_count).toBeDefined();
      expect(payload.date_range).toBeDefined();
    });

    it('should validate payload with backend (mocked)', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          valid: true,
          missing_fields: [],
          normalized_payload: { address: '123 Main St' },
          tips: ['Consider setting comparable_count to 5'],
          confidence: 0.9,
        }),
      });

      const result = await validatePayload({
        contentType: ContentType.CMA_REPORT,
        payload: { address: '123 Main St' },
        requestId: 'test_006',
      });

      expect(result.valid).toBe(true);
      expect(result.tips).toHaveLength(1);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/validate/cma_report'),
        expect.any(Object)
      );
    });

    it('should handle backend validation failure gracefully', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      const result = await validatePayload({
        contentType: ContentType.CMA_REPORT,
        payload: { address: '123 Main St' },
        requestId: 'test_007',
      });

      // Should return pessimistic validation but not fail
      expect(result.valid).toBe(false);
      expect(result.tips).toContain('Validation service unavailable - will attempt enrichment');
    });
  });

  describe('Enrichment Service', () => {
    it('should enrich missing fields with smart defaults', async () => {
      const result = await enrichPayload({
        contentType: ContentType.CMA_REPORT,
        payload: { address: '123 Main St' },
        missingFields: ['comparable_count', 'date_range'],
        validationResult: {
          valid: false,
          missing_fields: ['comparable_count', 'date_range'],
          normalized_payload: {},
          tips: [],
          confidence: 0.5,
        },
        requestId: 'test_008',
      });

      expect(result.enriched_payload.comparable_count).toBe(5);
      expect(result.enriched_payload.date_range).toBe('6_months');
      expect(result.filled_fields).toContain('comparable_count');
      expect(result.filled_fields).toContain('date_range');
      expect(result.confidence).toBeGreaterThan(0.3);
    });

    it('should use user preferences when available', async () => {
      localStorage.setItem('preferred_comparable_count', '10');

      const result = await enrichPayload({
        contentType: ContentType.CMA_REPORT,
        payload: { address: '123 Main St' },
        missingFields: ['comparable_count'],
        validationResult: {
          valid: false,
          missing_fields: ['comparable_count'],
          normalized_payload: {},
          tips: [],
          confidence: 0.5,
        },
        requestId: 'test_009',
      });

      expect(result.sources.comparable_count).toBe('user_preferences');
      expect(result.confidence).toBeGreaterThan(0.5);
    });
  });

  describe('Content Save Service', () => {
    it('should transform and save CMA content', async () => {
      const backendResponse = {
        content_type: 'CMA_REPORT',
        data: {
          sections: [{ type: 'header', content: 'CMA Report' }],
          summary: 'Test CMA',
          comparables: [
            { address: '124 Main St', price: 500000 },
          ],
          valuation_range: {
            low: 480000,
            mid: 500000,
            high: 520000,
            confidence: 0.85,
          },
          market_metrics: {
            avg_price: 500000,
            median_price: 495000,
          },
        },
        metadata: { address: '123 Main St' },
      };

      const result = await saveGeneratedContent({
        requestId: 'test_010',
        backendResponse,
        originalPayload: { address: '123 Main St' },
      });

      expect(result.success).toBe(true);
      expect(result.contentId).toBeDefined();
      expect(result.contentId).toMatch(/^content_/);
    });

    it('should fail validation for incomplete content', async () => {
      const backendResponse = {
        content_type: 'CMA_REPORT',
        data: {
          sections: [],
          // Missing required fields: comparables, valuationRange
        },
      };

      const result = await saveGeneratedContent({
        requestId: 'test_011',
        backendResponse,
        originalPayload: {},
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('validation failed');
    });
  });

  describe('Full Pipeline Integration', () => {
    it('should run complete pipeline successfully', async () => {
      // Mock all API calls
      (global.fetch as any)
        // Validation call
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            valid: true,
            missing_fields: [],
            normalized_payload: { address: '123 Main St' },
            tips: [],
            confidence: 0.9,
          }),
        })
        // Generation call
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            content: {
              sections: [{ type: 'header', content: 'CMA Report' }],
              summary: 'Generated CMA',
              comparables: [{ address: '124 Main St', price: 500000 }],
              valuation_range: {
                low: 480000,
                mid: 500000,
                high: 520000,
                confidence: 0.85,
              },
              market_metrics: {},
            },
            metadata: {},
            generation_info: { duration_ms: 2000 },
          }),
        });

      const result = await generateContent({
        userInput: 'Create a CMA for 123 Main St',
        requestId: 'test_012',
      });

      expect(result.success).toBe(true);
      expect(result.contentId).toBeDefined();
      expect(result.logs).toContain(expect.stringContaining('Pipeline completed'));
      expect(result.logs.length).toBeGreaterThan(5);
    });

    it('should handle pipeline failure gracefully', async () => {
      // Mock API failure
      (global.fetch as any).mockRejectedValueOnce(new Error('Backend unavailable'));

      const result = await generateContent({
        userInput: 'Create a CMA for 123 Main St',
        requestId: 'test_013',
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.logs).toContain(expect.stringContaining('Pipeline failed'));
    });

    it('should enrich and generate when fields are missing', async () => {
      // Mock validation with missing fields
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            valid: false,
            missing_fields: ['property_type', 'comparable_count'],
            normalized_payload: { address: '123 Main St' },
            tips: ['Consider setting comparable_count to 5'],
            confidence: 0.7,
          }),
        })
        // Enrichment falls back to local
        // Generation call
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            content: {
              sections: [],
              summary: 'Generated',
              comparables: [{ address: '124 Main St', price: 500000 }],
              valuation_range: {
                low: 480000,
                mid: 500000,
                high: 520000,
                confidence: 0.85,
              },
            },
          }),
        });

      const result = await generateContent({
        userInput: 'CMA for 123 Main St',
        requestId: 'test_014',
      });

      expect(result.success).toBe(true);
      expect(result.logs).toContain(expect.stringContaining('enrichment'));
    });
  });

  describe('Error Handling', () => {
    it('should handle low confidence intent', async () => {
      const result = await generateContent({
        userInput: 'random words no intent',
        requestId: 'test_015',
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('determine');
    });

    it('should handle missing critical fields after enrichment', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            valid: false,
            missing_fields: ['address'], // Critical required field
            normalized_payload: {},
            tips: [],
            confidence: 0.3,
          }),
        });

      const result = await generateContent({
        userInput: 'Create a CMA',
        requestId: 'test_016',
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('missing');
    });
  });
});

describe('Performance Tests', () => {
  it('should complete normalization in under 100ms', async () => {
    const start = Date.now();
    await normalizeIntent({
      userInput: 'Create a CMA for 123 Main St',
      requestId: 'perf_001',
    });
    const duration = Date.now() - start;

    expect(duration).toBeLessThan(100);
  });

  it('should handle batch enrichment efficiently', async () => {
    const start = Date.now();
    
    const requests = Array.from({ length: 10 }, (_, i) => ({
      contentType: ContentType.CMA_REPORT,
      payload: { address: `${i + 100} Main St` },
      missingFields: ['comparable_count'],
      validationResult: {
        valid: false,
        missing_fields: ['comparable_count'],
        normalized_payload: {},
        tips: [],
        confidence: 0.5,
      },
      requestId: `perf_${i + 2}`,
    }));

    await Promise.all(requests.map(req => enrichPayload(req)));
    
    const duration = Date.now() - start;

    // Should handle 10 enrichments in under 1 second
    expect(duration).toBeLessThan(1000);
  });
});

// Export test utilities for reuse
export const mockBackendSuccess = () => {
  (global.fetch as any).mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: true,
      missing_fields: [],
      normalized_payload: {},
      tips: [],
      confidence: 0.9,
    }),
  });
};

export const mockBackendFailure = () => {
  (global.fetch as any).mockRejectedValue(new Error('Network error'));
};
