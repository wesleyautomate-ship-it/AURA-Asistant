/**
 * AURA API Integration Layer
 * ============================
 * 
 * Comprehensive API service for all AURA endpoints:
 * - Marketing Automation
 * - CMA Reports  
 * - Social Media Automation
 * - Analytics & Reporting
 * - Workflow Orchestration
 * 
 * Provides type-safe, error-handled integration with PropertyPro AI's AURA backend.
 */

import { apiGet, apiPost } from './api';
import { CONFIG } from '../config';

// =============================================================================
// TYPES & INTERFACES
// =============================================================================

// Marketing Types
export interface MarketingTemplate {
  id: number;
  name: string;
  category: string;
  type: string;
  description?: string;
  dubai_specific: boolean;
}

export interface CampaignRequest {
  property_id: number;
  campaign_type: 'postcard' | 'email_blast' | 'social_campaign' | 'flyer';
  template_id?: number;
  custom_content?: Record<string, any>;
  auto_generate_content?: boolean;
}

export interface FullMarketingPackageRequest {
  property_id: number;
  include_postcards?: boolean;
  include_email?: boolean;
  include_social?: boolean;
  include_flyers?: boolean;
  custom_message?: string;
}

export interface CampaignResponse {
  id: number;
  title: string;
  property_id: number;
  property_title?: string;
  campaign_type: string;
  status: string;
  content: Record<string, any>;
  approved_by?: number;
  approved_at?: string;
  created_at: string;
  assets: Array<Record<string, any>>;
}

// CMA Types
export interface CMAReportRequest {
  property_id: number;
  analysis_type: 'listing' | 'buying' | 'investment';
  include_market_trends?: boolean;
  include_price_history?: boolean;
  include_neighborhood_analysis?: boolean;
  comp_radius_km?: number;
  comp_time_months?: number;
}

export interface QuickValuationRequest {
  property_type: 'apartment' | 'villa' | 'townhouse' | 'penthouse' | 'office' | 'retail';
  location: string;
  area_sqft: number;
  bedrooms?: number;
  bathrooms?: number;
  amenities?: string[];
  building_age?: number;
}

export interface CMAReportResponse {
  id: number;
  property_id: number;
  analysis_type: string;
  estimated_value: {
    min: number;
    max: number;
    recommended: number;
  };
  comparable_properties: Array<Record<string, any>>;
  market_analysis: Record<string, any>;
  pricing_recommendation: Record<string, any>;
  confidence_score: number;
  generated_at: string;
  report_url?: string;
}

export interface QuickValuationResponse {
  estimated_value: {
    min: number;
    max: number;
    recommended: number;
  };
  confidence_level: string;
  market_context: Record<string, any>;
  comparable_count: number;
  generated_at: string;
}

// Social Media Types
export interface SocialPostRequest {
  property_id?: number;
  platforms: string[];
  content_type: 'listing' | 'sold' | 'open_house' | 'market_update' | 'tips' | 'success_story';
  custom_message?: string;
  include_images?: boolean;
  schedule_time?: string;
  hashtags?: string[];
}

export interface SocialCampaignRequest {
  campaign_name: string;
  property_id?: number;
  campaign_type: 'property_launch' | 'market_series' | 'brand_awareness';
  platforms: string[];
  post_frequency?: 'hourly' | 'daily' | 'weekly';
  duration_days?: number;
  start_date?: string;
}

export interface HashtagResearchRequest {
  property_type?: string;
  location?: string;
  target_audience?: 'buyers' | 'investors' | 'renters' | 'sellers';
  max_hashtags?: number;
}

export interface SocialPostResponse {
  id: number;
  property_id?: number;
  platforms: string[];
  content_type: string;
  content: Record<string, any>;
  status: string;
  scheduled_time?: string;
  published_time?: string;
  created_at: string;
  assets: Array<Record<string, any>>;
}

export interface HashtagRecommendations {
  recommended_hashtags: Array<Record<string, any>>;
  trending_hashtags: string[];
  location_specific: string[];
  property_specific: string[];
  audience_targeted: string[];
}

// Analytics Types
export interface DashboardOverview {
  period: string;
  date_range: {
    start: string;
    end: string;
  };
  property_performance: {
    total_listings: number;
    active_listings: number;
    sold_listings: number;
    total_revenue: number;
  };
  lead_performance: {
    total_leads: number;
    qualified_leads: number;
    conversion_rate: number;
  };
  recent_activities: Array<{
    activity_type: string;
    description: string;
    created_at: string;
    property_id?: number;
  }>;
}

export interface PerformanceMetrics {
  total_listings: number;
  active_listings: number;
  sold_listings: number;
  total_revenue: number;
  avg_days_on_market: number;
  conversion_rate: number;
  lead_count: number;
  qualified_leads: number;
  period: string;
}

export interface MarketInsights {
  avg_price_psf: number;
  median_price: number;
  total_transactions: number;
  price_trend: number;
  inventory_levels: string;
  hottest_areas: Array<Record<string, any>>;
  market_forecast?: Record<string, any>;
}

export interface ReportGenerationRequest {
  report_type: 'performance' | 'market_analysis' | 'lead_funnel' | 'commission' | 'property_portfolio';
  report_name: string;
  time_period?: '7days' | '30days' | '90days' | '12months' | 'ytd' | 'custom';
  start_date?: string;
  end_date?: string;
  include_charts?: boolean;
  include_forecasting?: boolean;
  recipients?: string[];
}

// Workflows Types
export interface WorkflowPackageRequest {
  package_template: 'new_listing' | 'lead_nurturing' | 'client_onboarding';
  variables: Record<string, any>;
  notify_on_completion?: boolean;
}

export interface WorkflowPackageResponse {
  package_id: string;
  package_name: string;
  description: string;
  category: string;
  estimated_duration_minutes: number;
  required_variables: string[];
  optional_variables: string[];
}

export interface WorkflowExecutionResponse {
  execution_id: string;
  package_name: string;
  status: string;
  progress: number;
  started_at?: string;
  completed_at?: string;
  estimated_completion?: string;
  steps: Array<Record<string, any>>;
}

export interface WorkflowControlRequest {
  action: 'pause' | 'resume' | 'cancel';
  reason?: string;
}

// =============================================================================
// MARKETING AUTOMATION SERVICE
// =============================================================================

export class MarketingService {
  /**
   * Get all available marketing templates
   */
  static async getTemplates(category?: string, template_type?: string): Promise<MarketingTemplate[]> {
    let url = '/api/v1/marketing/templates';
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (template_type) params.append('template_type', template_type);
    if (params.toString()) url += `?${params.toString()}`;
    
    return apiGet<MarketingTemplate[]>(url);
  }

  /**
   * Preview a marketing template
   */
  static async previewTemplate(template_id: number, property_id?: number): Promise<any> {
    let url = `/api/v1/marketing/templates/${template_id}/preview`;
    if (property_id) url += `?property_id=${property_id}`;
    
    return apiGet(url);
  }

  /**
   * Create a single marketing campaign
   */
  static async createCampaign(request: CampaignRequest): Promise<CampaignResponse> {
    return apiPost<CampaignResponse>('/api/v1/marketing/campaigns', request);
  }

  /**
   * Create a full marketing package (AURA's signature feature)
   */
  static async createFullPackage(request: FullMarketingPackageRequest): Promise<any> {
    return apiPost('/api/v1/marketing/campaigns/full-package', request);
  }

  /**
   * Get marketing campaign details
   */
  static async getCampaign(campaign_id: number): Promise<CampaignResponse> {
    return apiGet<CampaignResponse>(`/api/v1/marketing/campaigns/${campaign_id}`);
  }

  /**
   * List marketing campaigns
   */
  static async getCampaigns(status?: string, property_id?: number): Promise<CampaignResponse[]> {
    let url = '/api/v1/marketing/campaigns';
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (property_id) params.append('property_id', property_id.toString());
    if (params.toString()) url += `?${params.toString()}`;
    
    return apiGet<CampaignResponse[]>(url);
  }

  /**
   * Approve or reject a campaign
   */
  static async approveCampaign(
    campaign_id: number, 
    action: 'approve' | 'reject', 
    approved_content?: Record<string, any>, 
    rejection_reason?: string
  ): Promise<any> {
    return apiPost(`/api/v1/marketing/campaigns/${campaign_id}/approval`, {
      action,
      approved_content,
      rejection_reason
    });
  }

  /**
   * Generate campaign assets
   */
  static async generateAssets(campaign_id: number, asset_types: string[]): Promise<any> {
    return apiPost(`/api/v1/marketing/campaigns/${campaign_id}/assets/generate`, {
      asset_types
    });
  }

  /**
   * Get marketing analytics
   */
  static async getAnalytics(time_period = '30days'): Promise<any> {
    return apiGet(`/api/v1/marketing/analytics/summary?time_period=${time_period}`);
  }
}

// =============================================================================
// CMA REPORTS SERVICE  
// =============================================================================

export class CMAService {
  /**
   * Generate comprehensive CMA report
   */
  static async generateReport(request: CMAReportRequest): Promise<any> {
    return apiPost('/api/v1/cma/reports', request);
  }

  /**
   * Get quick property valuation
   */
  static async getQuickValuation(request: QuickValuationRequest): Promise<QuickValuationResponse> {
    return apiPost<QuickValuationResponse>('/api/v1/cma/valuation/quick', request);
  }

  /**
   * Get market snapshot for area
   */
  static async getMarketSnapshot(area: string, property_type?: string): Promise<any> {
    let url = `/api/v1/cma/market/snapshot?area=${encodeURIComponent(area)}`;
    if (property_type) url += `&property_type=${property_type}`;
    
    return apiGet(url);
  }

  /**
   * Find comparable properties
   */
  static async getComparables(property_id: number): Promise<any> {
    return apiGet(`/api/v1/cma/comparables/${property_id}`);
  }

  /**
   * Generate market analysis
   */
  static async generateMarketAnalysis(area_name: string, property_type?: string, analysis_period = '12months'): Promise<any> {
    return apiPost('/api/v1/cma/market/analysis', {
      area_name,
      property_type,
      analysis_period,
      include_forecasting: false
    });
  }

  /**
   * Get CMA analytics
   */
  static async getAnalytics(time_period = '30days'): Promise<any> {
    return apiGet(`/api/v1/cma/analytics/summary?time_period=${time_period}`);
  }
}

// =============================================================================
// SOCIAL MEDIA SERVICE
// =============================================================================

export class SocialMediaService {
  /**
   * Create social media posts for multiple platforms
   */
  static async createPost(request: SocialPostRequest): Promise<SocialPostResponse> {
    return apiPost<SocialPostResponse>('/api/v1/social/posts', request);
  }

  /**
   * Create social media campaign
   */
  static async createCampaign(request: SocialCampaignRequest): Promise<any> {
    return apiPost('/api/v1/social/campaigns', request);
  }

  /**
   * Research hashtags for Dubai real estate
   */
  static async researchHashtags(request: HashtagResearchRequest): Promise<HashtagRecommendations> {
    return apiPost<HashtagRecommendations>('/api/v1/social/hashtags/research', request);
  }

  /**
   * Get scheduled posts
   */
  static async getScheduledPosts(): Promise<SocialPostResponse[]> {
    return apiGet<SocialPostResponse[]>('/api/v1/social/schedule/upcoming');
  }

  /**
   * Get social media posts
   */
  static async getPosts(status?: string, platform?: string): Promise<SocialPostResponse[]> {
    let url = '/api/v1/social/posts';
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (platform) params.append('platform', platform);
    if (params.toString()) url += `?${params.toString()}`;
    
    return apiGet<SocialPostResponse[]>(url);
  }

  /**
   * Publish a post
   */
  static async publishPost(task_id: string, platforms: string[]): Promise<any> {
    return apiPost(`/api/v1/social/posts/${task_id}/publish`, { platforms });
  }

  /**
   * Get social media analytics
   */
  static async getAnalytics(time_period = '30days'): Promise<any> {
    return apiGet(`/api/v1/social/analytics/summary?time_period=${time_period}`);
  }
}

// =============================================================================
// ANALYTICS SERVICE
// =============================================================================

export class AnalyticsService {
  /**
   * Get dashboard overview
   */
  static async getDashboardOverview(time_period = '30days'): Promise<DashboardOverview> {
    return apiGet<DashboardOverview>(`/api/v1/analytics/dashboard/overview?time_period=${time_period}`);
  }

  /**
   * Get performance metrics
   */
  static async getPerformanceMetrics(time_period = '30days', include_forecast = false): Promise<PerformanceMetrics> {
    return apiGet<PerformanceMetrics>(`/api/v1/analytics/performance?time_period=${time_period}&include_forecast=${include_forecast}`);
  }

  /**
   * Get market insights
   */
  static async getMarketInsights(area?: string, property_type?: string): Promise<MarketInsights> {
    let url = '/api/v1/analytics/market/insights';
    const params = new URLSearchParams();
    if (area) params.append('area', area);
    if (property_type) params.append('property_type', property_type);
    if (params.toString()) url += `?${params.toString()}`;
    
    return apiGet<MarketInsights>(url);
  }

  /**
   * Get lead analytics
   */
  static async getLeadAnalytics(time_period = '30days'): Promise<any> {
    return apiGet(`/api/v1/analytics/leads?time_period=${time_period}`);
  }

  /**
   * Generate custom report
   */
  static async generateReport(request: ReportGenerationRequest): Promise<any> {
    return apiPost('/api/v1/analytics/reports/generate', request);
  }

  /**
   * Get performance trends
   */
  static async getPerformanceTrends(
    metric = 'revenue', 
    time_period = '90days', 
    granularity = 'weekly'
  ): Promise<any> {
    return apiGet(`/api/v1/analytics/performance/trends?metric=${metric}&time_period=${time_period}&granularity=${granularity}`);
  }

  /**
   * Get performance benchmarks
   */
  static async getBenchmarks(benchmark_type = 'market'): Promise<any> {
    return apiGet(`/api/v1/analytics/benchmarks?benchmark_type=${benchmark_type}`);
  }
}

// =============================================================================
// WORKFLOWS SERVICE
// =============================================================================

export class WorkflowsService {
  /**
   * Get available workflow packages
   */
  static async getPackages(category?: string): Promise<WorkflowPackageResponse[]> {
    let url = '/api/v1/workflows/packages';
    if (category) url += `?category=${category}`;
    
    return apiGet<WorkflowPackageResponse[]>(url);
  }

  /**
   * Get detailed package information
   */
  static async getPackageDetails(package_id: string): Promise<any> {
    return apiGet(`/api/v1/workflows/packages/${package_id}/details`);
  }

  /**
   * Execute a workflow package (AURA's core automation)
   */
  static async executePackage(request: WorkflowPackageRequest): Promise<WorkflowExecutionResponse> {
    return apiPost<WorkflowExecutionResponse>('/api/v1/workflows/execute', request);
  }

  /**
   * Get execution status and progress
   */
  static async getExecutionStatus(execution_id: string): Promise<WorkflowExecutionResponse> {
    return apiGet<WorkflowExecutionResponse>(`/api/v1/workflows/executions/${execution_id}`);
  }

  /**
   * Control execution (pause, resume, cancel)
   */
  static async controlExecution(execution_id: string, request: WorkflowControlRequest): Promise<any> {
    return apiPost(`/api/v1/workflows/executions/${execution_id}/control`, request);
  }

  /**
   * Get execution history
   */
  static async getExecutionHistory(limit = 10, status?: string): Promise<WorkflowExecutionResponse[]> {
    let url = `/api/v1/workflows/executions?limit=${limit}`;
    if (status) url += `&status=${status}`;
    
    return apiGet<WorkflowExecutionResponse[]>(url);
  }

  /**
   * Get workflow analytics
   */
  static async getAnalytics(time_period = '30days'): Promise<any> {
    return apiGet(`/api/v1/workflows/analytics/summary?time_period=${time_period}`);
  }

  /**
   * Get system health for workflows
   */
  static async getHealthStatus(): Promise<any> {
    return apiGet('/api/v1/workflows/health');
  }
}

// =============================================================================
// COMBINED AURA SERVICE
// =============================================================================

/**
 * Main AURA service that combines all functionality
 * Provides high-level methods for common AURA operations
 */
export class AURAService {
  // Service instances
  static marketing = MarketingService;
  static cma = CMAService;
  static social = SocialMediaService;
  static analytics = AnalyticsService;
  static workflows = WorkflowsService;

  /**
   * Execute complete New Listing workflow package
   * This is AURA's signature one-click automation
   */
  static async executeNewListingPackage(property_id: number, priority = 'medium'): Promise<WorkflowExecutionResponse> {
    return WorkflowsService.executePackage({
      package_template: 'new_listing',
      variables: {
        property_id,
        priority
      },
      notify_on_completion: true
    });
  }

  /**
   * Execute Lead Nurturing workflow package
   */
  static async executeLeadNurturingPackage(lead_id: number, nurturing_type = 'standard'): Promise<WorkflowExecutionResponse> {
    return WorkflowsService.executePackage({
      package_template: 'lead_nurturing',
      variables: {
        lead_id,
        nurturing_type
      },
      notify_on_completion: true
    });
  }

  /**
   * Execute Client Onboarding workflow package
   */
  static async executeClientOnboardingPackage(client_id: number, onboarding_type = 'full'): Promise<WorkflowExecutionResponse> {
    return WorkflowsService.executePackage({
      package_template: 'client_onboarding',
      variables: {
        client_id,
        onboarding_type
      },
      notify_on_completion: true
    });
  }

  /**
   * Get comprehensive dashboard data for AURA
   */
  static async getDashboard(time_period = '30days'): Promise<{
    overview: DashboardOverview;
    performance: PerformanceMetrics;
    market_insights: MarketInsights;
    recent_executions: WorkflowExecutionResponse[];
  }> {
    const [overview, performance, market_insights, recent_executions] = await Promise.all([
      AnalyticsService.getDashboardOverview(time_period),
      AnalyticsService.getPerformanceMetrics(time_period),
      AnalyticsService.getMarketInsights('Dubai Marina'), // Default to Dubai Marina
      WorkflowsService.getExecutionHistory(5)
    ]);

    return {
      overview,
      performance,
      market_insights,
      recent_executions
    };
  }

  /**
   * Get quick property insights (combines CMA and market data)
   */
  static async getQuickPropertyInsights(property_id: number): Promise<{
    valuation: QuickValuationResponse;
    market_snapshot: any;
    comparable_properties: any;
  }> {
    // Note: This would need property details to work properly
    // For now, return structure for type safety
    const [valuation] = await Promise.all([
      // CMAService.getQuickValuation(...) - needs property details
      // CMAService.getMarketSnapshot(...) - needs location
      // CMAService.getComparables(property_id)
    ]);

    return {
      valuation: {} as QuickValuationResponse,
      market_snapshot: {},
      comparable_properties: {}
    };
  }

  /**
   * Health check for all AURA services
   */
  static async healthCheck(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    services: Record<string, boolean>;
    timestamp: string;
  }> {
    try {
      // Test each service endpoint
      const checks = await Promise.allSettled([
        MarketingService.getTemplates(),
        AnalyticsService.getDashboardOverview(),
        WorkflowsService.getPackages(),
        WorkflowsService.getHealthStatus()
      ]);

      const services = {
        marketing: checks[0].status === 'fulfilled',
        analytics: checks[1].status === 'fulfilled', 
        workflows: checks[2].status === 'fulfilled',
        system: checks[3].status === 'fulfilled'
      };

      const healthyCount = Object.values(services).filter(Boolean).length;
      const status = healthyCount === 4 ? 'healthy' : 
                   healthyCount >= 2 ? 'degraded' : 'unhealthy';

      return {
        status,
        services,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        services: {
          marketing: false,
          analytics: false,
          workflows: false,
          system: false
        },
        timestamp: new Date().toISOString()
      };
    }
  }
}

// Export all services
export default AURAService;
export {
  MarketingService,
  CMAService, 
  SocialMediaService,
  AnalyticsService,
  WorkflowsService
};
