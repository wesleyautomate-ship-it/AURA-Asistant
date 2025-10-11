/**
 * Content Schemas - TypeScript Definitions
 * =========================================
 * 
 * Type-safe schemas matching backend content_types.py
 * Used for content generation, storage, and rendering
 * 
 * Version: 3.2
 * Phase: Track 2.1 - Frontend Content Schemas
 */

// =============================================================================
// CONTENT TYPE ENUMS
// =============================================================================

export enum ContentType {
  CMA_REPORT = 'CMA_REPORT',
  PITCH_DECK = 'PITCH_DECK',
  MARKET_REPORT = 'MARKET_REPORT',
  NEWSLETTER = 'NEWSLETTER',
  SOCIAL_POST = 'SOCIAL_POST',
}

export enum TaskStatus {
  PENDING = 'Pending',
  PROCESSING = 'Processing',
  COMPLETE = 'Complete',
  ERROR = 'Error',
}

export enum ContentStatus {
  DRAFT = 'DRAFT',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  ERROR = 'ERROR',
}

export enum SchemaVersion {
  V1 = '1.0.0',
}

// =============================================================================
// BASE CONTENT STRUCTURE
// =============================================================================

export interface ContentMetadata {
  taskId: string;
  title: string;
  type: ContentType;
  createdAt: string;
  updatedAt?: string;
  exportedAt?: string;
  exportFormats?: string[];
  version: string; // Schema version for migrations
}

export interface BaseContent {
  id: string;
  type: ContentType;
  status: ContentStatus;
  version: number;
  schemaVersion: SchemaVersion;
  createdAt: string;
  updatedAt: string;
  metadata: Record<string, any>;
  sections: Section[];
}

export interface CMAReportContent extends BaseContent {
  type: ContentType.CMA_REPORT;
  summary: string;
  comparables: any[];
  valuationRange: {
    low: number;
    mid: number;
    high: number;
    confidence: number;
  };
  marketMetrics: Record<string, any>;
}

export interface PitchDeckContent extends BaseContent {
  type: ContentType.PITCH_DECK;
  slides: any[];
  theme: string;
  targetAudience: string;
}

export interface MarketReportContent extends BaseContent {
  type: ContentType.MARKET_REPORT;
  insights: string[];
  chartData: any[];
}

export interface NewsletterContent extends BaseContent {
  type: ContentType.NEWSLETTER;
  topic: string;
  tone: string;
  targetAudience: string;
}

export interface SocialPostContent extends BaseContent {
  type: ContentType.SOCIAL_POST;
  platform: string;
  content: string;
  hashtags: string[];
  characterCount: number;
}

export interface Section {
  id: string;
  type: string;
  title: string;
  order: number;
  content: any; // Flexible content based on section type
}

// =============================================================================
// CMA REPORT SCHEMA
// =============================================================================

export interface CMAProperty {
  address: string;
  sqft?: number;
  bedrooms?: number;
  bathrooms?: number;
  yearBuilt?: number;
  lotSize?: string;
  type?: string;
  description?: string;
}

export interface CMAComparable {
  address: string;
  price: number;
  sqft: number;
  bedrooms: number;
  bathrooms: number;
  soldDate: string;
  distance: number; // miles or km
  pricePerSqft: number;
  adjustedPrice?: number;
  adjustments?: Record<string, number>;
  status?: 'sold' | 'active' | 'pending';
}

export interface CMAMarketAnalysis {
  avgPrice: number;
  medianPrice: number;
  pricePerSqft: number;
  marketTrend: 'up' | 'down' | 'stable';
  trendPercentage?: number;
  daysOnMarket: number;
  inventory: number;
  absorptionRate?: number;
}

export interface CMAValuation {
  estimatedValue: number;
  confidenceRange: { min: number; max: number };
  methodology: string[];
  adjustmentFactors?: Record<string, number>;
}

export interface CMAReport extends ContentMetadata {
  type: ContentType.CMA_REPORT;
  property: CMAProperty;
  marketAnalysis: CMAMarketAnalysis;
  comparables: CMAComparable[];
  valuation: CMAValuation;
  insights: string[];
  recommendations?: string[];
  disclaimers: string[];
  reportId: string;
  sections: Section[];
}

// =============================================================================
// PITCH DECK SCHEMA
// =============================================================================

export interface DeckProperty {
  address: string;
  type: 'residential' | 'commercial' | 'mixed' | 'land';
  sqft?: number;
  lotSize?: string;
  yearBuilt?: number;
  occupancy?: number;
  zoning?: string;
}

export type SlideType = 
  | 'title'
  | 'property-overview'
  | 'market-analysis'
  | 'financial-projections'
  | 'investment-highlights'
  | 'neighborhood'
  | 'team'
  | 'timeline'
  | 'conclusion'
  | 'custom';

export interface ChartData {
  type: 'bar' | 'line' | 'pie' | 'area' | 'scatter';
  title: string;
  data: any[];
  xAxis?: string;
  yAxis?: string;
  colors?: string[];
}

export interface ImageAsset {
  url: string;
  alt: string;
  caption?: string;
  width?: number;
  height?: number;
}

export interface SlideContent {
  text?: string;
  subtitle?: string;
  bullets?: string[];
  data?: Record<string, any>;
  charts?: ChartData[];
  images?: ImageAsset[];
  metrics?: Array<{ label: string; value: string | number; trend?: 'up' | 'down' | 'neutral' }>;
}

export interface Slide {
  id: string;
  type: SlideType;
  title: string;
  order: number;
  content: SlideContent;
  notes?: string;
  layout?: 'full' | 'split' | 'grid' | 'image-focus';
}

export interface DeckTheme {
  primaryColor: string;
  accentColor: string;
  fontFamily: string;
  backgroundColor?: string;
  textColor?: string;
}

export interface PitchDeck extends ContentMetadata {
  type: ContentType.PITCH_DECK;
  property: DeckProperty;
  slides: Slide[];
  theme: DeckTheme;
  investmentType?: 'acquisition' | 'development' | 'renovation' | 'flip';
  targetAudience?: string;
  executiveSummary?: string;
}

// =============================================================================
// MARKET REPORT SCHEMA
// =============================================================================

export interface MarketMetric {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  changePercent?: number;
  historicalData?: Array<{ date: string; value: number }>;
}

export interface MarketSegment {
  name: string;
  propertyType: string;
  avgPrice: number;
  priceChange: number;
  volume: number;
  daysOnMarket: number;
}

export interface MarketReport extends ContentMetadata {
  type: ContentType.MARKET_REPORT;
  region: string;
  propertyType: string;
  timePeriod: string;
  metrics: MarketMetric[];
  segments: MarketSegment[];
  insights: string[];
  forecast?: {
    period: string;
    predictions: Array<{ metric: string; value: number; confidence: number }>;
  };
  sections: Section[];
  charts?: ChartData[];
}

// =============================================================================
// NEWSLETTER SCHEMA
// =============================================================================

export interface NewsletterSection {
  id: string;
  type: 'header' | 'article' | 'listing' | 'market-update' | 'cta' | 'footer';
  title?: string;
  content: string;
  order: number;
  images?: ImageAsset[];
  links?: Array<{ text: string; url: string }>;
}

export interface FeaturedListing {
  address: string;
  price: number;
  sqft: number;
  bedrooms: number;
  bathrooms: number;
  imageUrl?: string;
  description: string;
  link?: string;
}

export interface Newsletter extends ContentMetadata {
  type: ContentType.NEWSLETTER;
  topic: string;
  tone: 'professional' | 'casual' | 'friendly' | 'authoritative';
  targetAudience: string;
  sections: NewsletterSection[];
  featuredListings?: FeaturedListing[];
  greeting?: string;
  signature?: string;
  unsubscribeLink?: string;
  previewText?: string;
}

// =============================================================================
// SOCIAL POST SCHEMA
// =============================================================================

export type SocialPlatform = 'instagram' | 'facebook' | 'linkedin' | 'twitter' | 'tiktok';

export interface SocialPost extends ContentMetadata {
  type: ContentType.SOCIAL_POST;
  platform: SocialPlatform;
  topic: string;
  content: string;
  hashtags: string[];
  mentions?: string[];
  images?: ImageAsset[];
  tone: 'engaging' | 'professional' | 'casual' | 'inspirational' | 'urgent';
  characterCount: number;
  characterLimit?: number;
  propertyId?: string;
  callToAction?: string;
  scheduledFor?: string;
}

// =============================================================================
// UNIFIED CONTENT TYPE
// =============================================================================

export type GeneratedContent = 
  | CMAReport 
  | PitchDeck 
  | MarketReport 
  | Newsletter 
  | SocialPost;

// =============================================================================
// VALIDATION & ERROR TYPES
// =============================================================================

export interface ValidationError {
  detail: string;
  missing_fields: string[];
  hints: string[];
  suggested_defaults?: Record<string, any>;
  can_auto_heal: boolean;
}

export interface ValidationResult {
  valid: boolean;
  missing_fields: string[];
  normalized_payload: Record<string, any>;
  tips: string[];
  confidence: number;
}

// =============================================================================
// TASK & SYNC TYPES
// =============================================================================

export interface TaskResponse {
  id: string;
  title: string;
  status: TaskStatus;
  type: ContentType | string; // Allow string for backward compatibility
  timestamp: string;
  created_at: string;
  updated_at: string;
  
  // Content flags
  has_content: boolean;
  content_type?: ContentType;
  
  // Relationships
  parent_id?: string;
  related_tasks: string[];
  
  // Export metadata
  exported_at?: string;
  export_formats: string[];
  
  // Error handling
  error?: string;
  
  // Additional metadata
  metadata: Record<string, any>;
}

export interface TaskSyncResponse {
  tasks: TaskResponse[];
  last_sync: string;
  has_more: boolean;
  cursor?: string;
}

// =============================================================================
// EXPORT TYPES
// =============================================================================

export interface ExportRequest {
  task_id: string;
  content_type: ContentType;
  format: 'pdf' | 'html';
  include_branding?: boolean;
}

export interface ShareLinkResponse {
  success: boolean;
  share_url: string;
  expires_at: string;
  token: string;
  message: string;
}

export interface ExportStatusResponse {
  task_id: string;
  exported: boolean;
  export_count: number;
  last_export?: string;
  formats_available: string[];
}

// =============================================================================
// CONTENT STORE STATE
// =============================================================================

export interface ContentStoreState {
  version: string; // Schema version for migrations
  content: Record<string, GeneratedContent>; // keyed by taskId
  exportStatus: Record<string, ExportStatusResponse>; // keyed by taskId
  lastSync?: string;
}

// =============================================================================
// HELPER TYPE GUARDS
// =============================================================================

export const isCMAReport = (content: GeneratedContent): content is CMAReport => {
  return content.type === ContentType.CMA_REPORT;
};

export const isPitchDeck = (content: GeneratedContent): content is PitchDeck => {
  return content.type === ContentType.PITCH_DECK;
};

export const isMarketReport = (content: GeneratedContent): content is MarketReport => {
  return content.type === ContentType.MARKET_REPORT;
};

export const isNewsletter = (content: GeneratedContent): content is Newsletter => {
  return content.type === ContentType.NEWSLETTER;
};

export const isSocialPost = (content: GeneratedContent): content is SocialPost => {
  return content.type === ContentType.SOCIAL_POST;
};

// =============================================================================
// SCHEMA VERSION & MIGRATION
// =============================================================================

export const CONTENT_SCHEMA_VERSION = '1.0.0';

export interface ContentMigration {
  fromVersion: string;
  toVersion: string;
  migrate: (content: any) => GeneratedContent;
}

// Future migrations will be added here
export const contentMigrations: ContentMigration[] = [];

/**
 * Migrate content to current schema version
 */
export const migrateContent = (content: any): GeneratedContent => {
  const currentVersion = content.version || '0.0.0';
  
  if (currentVersion === CONTENT_SCHEMA_VERSION) {
    return content as GeneratedContent;
  }
  
  // Apply migrations sequentially
  let migratedContent = content;
  for (const migration of contentMigrations) {
    if (migration.fromVersion === currentVersion) {
      migratedContent = migration.migrate(migratedContent);
    }
  }
  
  return migratedContent;
};

/**
 * Validate content structure
 */
export const validateContentStructure = (content: any): boolean => {
  if (!content || typeof content !== 'object') return false;
  if (!content.type || !Object.values(ContentType).includes(content.type)) return false;
  if (!content.taskId || !content.title) return false;
  if (!content.createdAt) return false;
  
  return true;
};

/**
 * Create empty content template
 */
export const createContentTemplate = (
  type: ContentType,
  taskId: string,
  title: string
): Partial<GeneratedContent> => {
  const base: ContentMetadata = {
    taskId,
    title,
    type,
    createdAt: new Date().toISOString(),
    version: CONTENT_SCHEMA_VERSION,
  };
  
  switch (type) {
    case ContentType.CMA_REPORT:
      return {
        ...base,
        type: ContentType.CMA_REPORT,
        property: { address: '' },
        marketAnalysis: {
          avgPrice: 0,
          medianPrice: 0,
          pricePerSqft: 0,
          marketTrend: 'stable',
          daysOnMarket: 0,
          inventory: 0,
        },
        comparables: [],
        valuation: {
          estimatedValue: 0,
          confidenceRange: { min: 0, max: 0 },
          methodology: [],
        },
        insights: [],
        disclaimers: [],
        reportId: taskId,
        sections: [],
      } as Partial<CMAReport>;
      
    case ContentType.PITCH_DECK:
      return {
        ...base,
        type: ContentType.PITCH_DECK,
        property: { address: '', type: 'residential' },
        slides: [],
        theme: {
          primaryColor: '#667eea',
          accentColor: '#764ba2',
          fontFamily: 'Inter, sans-serif',
        },
      } as Partial<PitchDeck>;
      
    case ContentType.MARKET_REPORT:
      return {
        ...base,
        type: ContentType.MARKET_REPORT,
        region: '',
        propertyType: 'mixed',
        timePeriod: '',
        metrics: [],
        segments: [],
        insights: [],
        sections: [],
      } as Partial<MarketReport>;
      
    case ContentType.NEWSLETTER:
      return {
        ...base,
        type: ContentType.NEWSLETTER,
        topic: '',
        tone: 'professional',
        targetAudience: 'clients',
        sections: [],
      } as Partial<Newsletter>;
      
    case ContentType.SOCIAL_POST:
      return {
        ...base,
        type: ContentType.SOCIAL_POST,
        platform: 'instagram',
        topic: '',
        content: '',
        hashtags: [],
        tone: 'engaging',
        characterCount: 0,
      } as Partial<SocialPost>;
      
    default:
      return base;
  }
};
