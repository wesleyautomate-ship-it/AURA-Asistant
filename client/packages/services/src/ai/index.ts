import { CONFIG } from '../config';
import type { AIProvider, AIContentRequest, AIContentResponse } from '@propertypro/features/types';
import { apiPost } from '../api';

export async function generateContent(
  req: AIContentRequest,
  provider?: AIProvider
): Promise<AIContentResponse> {
  const selected = provider || CONFIG.aiProvider;
  return apiPost<AIContentResponse>(`/ai/generate-content?provider=${selected}`, req);
}

export async function analyzeProperty(
  req: { description: string; details?: Record<string, unknown> },
  provider?: AIProvider
) {
  const selected = provider || CONFIG.aiProvider;
  return apiPost<any>(`/ai/analyze-property?provider=${selected}`, req);
}
