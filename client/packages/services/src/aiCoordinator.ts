// Simple AI coordinator service to centralize AI features across modules
// This is a front-end stub. Replace with real backend/OpenAI calls in Alpha-2.

import { ChatMessage } from "@propertypro/features/types";

type MetricsEvent = {
  type: "request" | "response" | "error";
  timestamp: number;
  latencyMs?: number;
  tokensIn?: number;
  tokensOut?: number;
  module?: string;
};

export type AIContext = {
  module?: "property" | "crm" | "marketing" | "social" | "strategy" | "packages" | "analytics";
  entityId?: string;
};

export type AIRequest = {
  prompt: string;
  context?: AIContext;
};

export type AIResponse = Omit<ChatMessage, "id" | "sender"> & {
  // enrich as needed
};

const subscribers = new Set<(event: MetricsEvent) => void>();

function emit(event: MetricsEvent) {
  subscribers.forEach((cb) => {
    try { cb(event); } catch {}
  });
}

export function subscribeMetrics(cb: (event: MetricsEvent) => void) {
  subscribers.add(cb);
  return () => subscribers.delete(cb);
}

import { apiPost } from "./api";

export async function sendMessage(req: AIRequest): Promise<AIResponse> {
  const start = performance.now();
  emit({ type: "request", timestamp: Date.now(), module: req.context?.module });

  try {
    const response = await apiPost<AIResponse>("/api/requests", req);
    const end = performance.now();
    emit({ type: "response", timestamp: Date.now(), latencyMs: end - start, module: req.context?.module });
    return response;
  } catch (error) {
    const end = performance.now();
    emit({ type: "error", timestamp: Date.now(), latencyMs: end - start, module: req.context?.module });
    throw error;
  }
}

export default { sendMessage, subscribeMetrics };
