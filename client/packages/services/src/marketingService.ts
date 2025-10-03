import { apiGet, apiPost } from './api';

export interface MarketingTemplateSummary {
  id: number;
  name: string;
  category: string;
  type: string;
  description?: string;
  dubai_specific: boolean;
}

export type CampaignType = 'postcard' | 'email_blast' | 'social_campaign' | 'flyer';

interface RawMarketingCampaignResponse {
  campaign_id: number;
  status: string;
  message: string;
  campaign: Record<string, unknown>;
}

export interface MarketingCampaignResponse {
  campaignId: number;
  status: string;
  message: string;
  campaign: Record<string, unknown>;
}

export interface CreateMarketingCampaignPayload {
  propertyId: number;
  campaignType: CampaignType;
  templateId?: number;
  customContent?: Record<string, unknown>;
  autoGenerateContent?: boolean;
}

interface RawMarketingPackageResponse {
  package_id: string;
  message: string;
  package: {
    package_type: string;
    property_id: number;
    campaigns: Record<string, number>;
    created_at: string;
    status: string;
  };
  next_steps?: string;
}

export interface MarketingPackageResult {
  packageId: string;
  propertyId: number;
  message: string;
  campaigns: Record<string, number>;
  createdAt: string;
  status: string;
  nextSteps?: string;
}

export interface CreateFullMarketingPackagePayload {
  propertyId: number;
  includePostcards?: boolean;
  includeEmail?: boolean;
  includeSocial?: boolean;
  includeFlyers?: boolean;
  customMessage?: string;
}

export async function fetchMarketingTemplates(category?: string) {
  const params = new URLSearchParams();
  if (category) {
    params.append('category', category);
  }
  const path = params.toString()
    ? `/api/v1/marketing/templates?${params.toString()}`
    : '/api/v1/marketing/templates';
  return apiGet<MarketingTemplateSummary[]>(path);
}

export async function createMarketingCampaign(
  payload: CreateMarketingCampaignPayload,
): Promise<MarketingCampaignResponse> {
  const response = await apiPost<RawMarketingCampaignResponse>('/api/v1/marketing/campaigns', {
    property_id: payload.propertyId,
    campaign_type: payload.campaignType,
    template_id: payload.templateId,
    custom_content: payload.customContent,
    auto_generate_content: payload.autoGenerateContent ?? true,
  });

  return {
    campaignId: response.campaign_id,
    status: response.status,
    message: response.message,
    campaign: response.campaign ?? {},
  };
}

export async function createFullMarketingPackage(
  payload: CreateFullMarketingPackagePayload,
): Promise<MarketingPackageResult> {
  const response = await apiPost<RawMarketingPackageResponse>('/api/v1/marketing/campaigns/full-package', {
    property_id: payload.propertyId,
    include_postcards: payload.includePostcards ?? true,
    include_email: payload.includeEmail ?? true,
    include_social: payload.includeSocial ?? true,
    include_flyers: payload.includeFlyers ?? false,
    custom_message: payload.customMessage,
  });

  return {
    packageId: response.package_id,
    propertyId: response.package.property_id,
    message: response.message,
    campaigns: response.package.campaigns ?? {},
    createdAt: response.package.created_at,
    status: response.package.status,
    nextSteps: response.next_steps ?? undefined,
  };
}