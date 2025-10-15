/**
 * Intelligence API Types
 * =====================
 * 
 * TypeScript interfaces that match the backend Pydantic schemas exactly.
 * Ensures no validation errors (422) between frontend and backend.
 * 
 * Generated from: backend/app/schemas/intelligence.py
 */

// Enums matching backend
export enum ContentType {
  CMA_REPORT = "CMA_REPORT",
  PITCH_DECK = "PITCH_DECK",
  SOCIAL_POST = "SOCIAL_POST",
  MARKET_REPORT = "MARKET_REPORT",
  EMAIL_CAMPAIGN = "EMAIL_CAMPAIGN",
  PROPERTY_DESCRIPTION = "PROPERTY_DESCRIPTION",
  LISTING_STRATEGY = "LISTING_STRATEGY",
  PROPERTY_BROCHURE = "PROPERTY_BROCHURE",
  GENERAL = "GENERAL"
}

export enum TaskStatus {
  QUEUED = "queued",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled"
}

export enum TaskPriority {
  LOW = "low",
  NORMAL = "normal", 
  HIGH = "high",
  URGENT = "urgent"
}

// Core data structures
export interface QualityRequirements {
  min_score?: number;
  brand_consistency?: boolean;
  compliance_checks?: string[];
}

export interface MemoryContext {
  relevant_memories?: Array<{ [key: string]: any }>;
  contextual_insights?: string[];
  brand_alignment?: number;
}

export interface QualityScores {
  overall_score: number;
  content_quality: number;
  brand_compliance: number;
  validation_score: number;
}

export interface GeneratedContent {
  structured?: { [key: string]: any };
  narrative?: string;
  key_insights?: string[];
  actionable_recommendations?: string[];
}

export interface ContentMetadata {
  generation_timestamp: string;
  model: string;
  processing_time_ms?: number;
  confidence_level?: number;
  sources?: string[];
  mock_origin?: boolean;
}

export interface IntelligenceContent {
  content_id: string;
  task_id: string;
  content_type: ContentType;
  title: string;
  enhanced: boolean;
  quality_scores: QualityScores;
  memory_context: MemoryContext;
  generated_content: GeneratedContent;
  metadata: ContentMetadata;
  export_ready?: boolean;
  version?: string;
}

// Request interfaces
export interface ContentGenerationRequest {
  user_input: string;
  content_type?: ContentType | null;
  session_id?: string | null;
  priority?: TaskPriority;
  quality_requirements?: QualityRequirements | null;
  memory_enhanced?: boolean;
  context?: { [key: string]: any } | null;
}

export interface TranscriptionRequest {
  audio_data?: string | null;
  language?: string;
  use_mock?: boolean;
}

export interface RefinementRequest {
  content_id: string;
  refinement_prompt: string;
  quality_requirements?: QualityRequirements | null;
  context?: { [key: string]: any } | null;
}

// Response interfaces
export interface TranscriptionResponse {
  text: string;
  confidence: number;
  language_detected: string;
  is_mock?: boolean;
  processing_time_ms?: number;
}

export interface TaskStatusResponse {
  task_id: string;
  status: TaskStatus;
  progress: number;
  current_step?: string | null;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  estimated_completion?: string | null;
  retries?: number;
}

export interface ContentGenerationResponse {
  task_id: string;
  status: TaskStatus;
  message: string;
  estimated_duration_ms?: number;
  content_id?: string | null;
}

export interface ContentRetrievalResponse {
  content: IntelligenceContent;
  recommendations?: string[];
  refinement_suggestions?: string[];
}

export interface RefinementResponse {
  task_id: string;
  original_content_id: string;
  refined_content_id: string;
  status: TaskStatus;
  message: string;
  improvements_made?: string[];
}

export interface MockPromptResponse {
  text: string;
  mock_type: string;
  description: string;
}

export interface StreamProgressEvent {
  event?: string;
  task_id: string;
  status: TaskStatus;
  progress: number;
  current_step?: string | null;
  data?: { [key: string]: any } | null;
  timestamp: string;
}

// Error interfaces
export interface ValidationErrorDetail {
  field: string;
  message: string;
  value: any;
}

export interface ValidationErrorResponse {
  error_code?: string;
  message?: string;
  details: ValidationErrorDetail[];
  timestamp: string;
}

export interface IntelligenceError {
  error_code: string;
  message: string;
  details?: { [key: string]: any } | null;
  task_id?: string | null;
  timestamp: string;
}

// Utility types for API responses
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: IntelligenceError;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  per_page: number;
}

// Content type metadata
export interface ContentTypeInfo {
  type: string;
  name: string;
  description: string;
}

// Health check response
export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  mock_mode: boolean;
  timestamp: string;
}

// Legacy compatibility - map old types to new ones
export type IntelligenceContentOld = IntelligenceContent;
export type ContentTypeOld = ContentType;

// Helper type for content creation
export interface CreateContentPayload {
  userInput: string;
  contentType?: ContentType;
  priority?: TaskPriority;
  context?: { [key: string]: any };
  qualityRequirements?: QualityRequirements;
}

// Helper type for refined content tracking
export interface ContentVersionHistory {
  original_content_id: string;
  versions: Array<{
    content_id: string;
    refinement_prompt: string;
    quality_improvement: number;
    created_at: string;
  }>;
}

// SSE Event types for streaming
export interface SSEEventData {
  event: string;
  data: string;
}

export interface ProgressEventData {
  task_id: string;
  status: TaskStatus;
  progress: number;
  current_step?: string;
  data?: { [key: string]: any };
  timestamp: string;
}

// Export utility functions for type guards
export const isContentType = (value: string): value is ContentType => {
  return Object.values(ContentType).includes(value as ContentType);
};

export const isTaskStatus = (value: string): value is TaskStatus => {
  return Object.values(TaskStatus).includes(value as TaskStatus);
};

export const isTaskPriority = (value: string): value is TaskPriority => {
  return Object.values(TaskPriority).includes(value as TaskPriority);
};

// Content type display helpers
export const getContentTypeDisplay = (type: ContentType): string => {
  const displayMap: Record<ContentType, string> = {
    [ContentType.CMA_REPORT]: "CMA Report",
    [ContentType.PITCH_DECK]: "Pitch Deck",
    [ContentType.SOCIAL_POST]: "Social Media Post",
    [ContentType.MARKET_REPORT]: "Market Report", 
    [ContentType.EMAIL_CAMPAIGN]: "Email Campaign",
    [ContentType.PROPERTY_DESCRIPTION]: "Property Description",
    [ContentType.LISTING_STRATEGY]: "Listing Strategy",
    [ContentType.PROPERTY_BROCHURE]: "Property Brochure",
    [ContentType.GENERAL]: "General Content"
  };
  return displayMap[type] || type;
};

export const getTaskStatusDisplay = (status: TaskStatus): string => {
  const displayMap: Record<TaskStatus, string> = {
    [TaskStatus.QUEUED]: "Queued",
    [TaskStatus.PROCESSING]: "Processing",
    [TaskStatus.COMPLETED]: "Completed",
    [TaskStatus.FAILED]: "Failed",
    [TaskStatus.CANCELLED]: "Cancelled"
  };
  return displayMap[status] || status;
};

export const getPriorityDisplay = (priority: TaskPriority): string => {
  const displayMap: Record<TaskPriority, string> = {
    [TaskPriority.LOW]: "Low",
    [TaskPriority.NORMAL]: "Normal",
    [TaskPriority.HIGH]: "High", 
    [TaskPriority.URGENT]: "Urgent"
  };
  return displayMap[priority] || priority;
};