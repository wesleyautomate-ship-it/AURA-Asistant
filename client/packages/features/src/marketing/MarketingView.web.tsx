import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  createFullMarketingPackage,
  createMarketingCampaign,
  fetchMarketingTemplates,
  type CampaignType,
  type MarketingCampaignResponse,
  type MarketingPackageResult,
  type MarketingTemplateSummary,
} from '@propertypro/services';
import { usePropertyStore, selectPropertyFetchStatus } from '@propertypro/store';
import type { Property } from '@propertypro/store';

interface Props {
  onBack?: () => void;
}

const campaignTypeByCategory: Record<string, CampaignType> = {
  postcard: 'postcard',
  email: 'email_blast',
  social: 'social_campaign',
  flyer: 'flyer',
};

const samplePropertyPayload: Omit<Property, 'id'> = {
  title: 'Dubai Marina Launch Suite',
  description:
    'Stylish two-bedroom residence with full marina skyline views, curated interiors, and smart home upgrades.',
  price: 3450000,
  location: 'Dubai Marina',
  propertyType: 'apartment',
  beds: 2,
  baths: 2,
  sqft: 1280,
};

function formatTemplateMeta(template: MarketingTemplateSummary): string {
  const category = template.category ? template.category.toUpperCase() : 'TEMPLATE';
  const type = template.type ? template.type.replace(/_/g, ' ') : '';
  return type ? `${category} / ${type}` : category;
}

function formatPropertyMeta(property: Property): string {
  const parts: string[] = [];
  const priceValue = Number(property.price);
  if (Number.isFinite(priceValue) && priceValue > 0) {
    parts.push(`AED ${priceValue.toLocaleString()}`);
  }
  if (property.beds !== undefined && property.beds !== null) {
    parts.push(`${property.beds} beds`);
  }
  if (property.baths !== undefined && property.baths !== null) {
    parts.push(`${property.baths} baths`);
  }
  const sqftValue = Number(property.sqft);
  if (Number.isFinite(sqftValue) && sqftValue > 0) {
    parts.push(`${sqftValue.toLocaleString()} sqft`);
  }
  return parts.join(' | ') || 'Details pending';
}

function normalizeNumericId(value: Property['id']): number | null {
  const maybeNumber = Number.parseInt(String(value), 10);
  return Number.isNaN(maybeNumber) ? null : maybeNumber;
}

const MarketingView: React.FC<Props> = ({ onBack }) => {
  const properties = usePropertyStore((state) => state.items as Property[]);
  const fetchProperties = usePropertyStore((state) => state.fetchProperties);
  const addProperty = usePropertyStore((state) => state.addProperty);
  const setSelectedPropertyInStore = usePropertyStore((state) => state.setSelected);
  const propertyFetchStatus = usePropertyStore(selectPropertyFetchStatus);
  const propertyFetchError = usePropertyStore((state) => state.fetch.error);

  const [selectedPropertyId, setSelectedPropertyId] = useState<string>('');
  const [templates, setTemplates] = useState<MarketingTemplateSummary[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [templatesLoading, setTemplatesLoading] = useState(false);
  const [templatesError, setTemplatesError] = useState<string | null>(null);
  const [packageResult, setPackageResult] = useState<MarketingPackageResult | null>(null);
  const [packageError, setPackageError] = useState<string | null>(null);
  const [creatingPackage, setCreatingPackage] = useState(false);
  const [campaignResult, setCampaignResult] = useState<MarketingCampaignResponse | null>(null);
  const [campaignError, setCampaignError] = useState<string | null>(null);
  const [creatingCampaign, setCreatingCampaign] = useState(false);
  const [isRefreshingProperties, setIsRefreshingProperties] = useState(false);
  const [isSeedingProperty, setIsSeedingProperty] = useState(false);
  const [seedError, setSeedError] = useState<string | null>(null);

  const hasProperties = properties.length > 0;

  const loadTemplates = useCallback(async () => {
    setTemplatesLoading(true);
    setTemplatesError(null);
    try {
      const data = await fetchMarketingTemplates();
      setTemplates(data);
      setSelectedTemplateId((current) => {
        if (current && data.some((item) => item.id === current)) {
          return current;
        }
        return data[0]?.id ?? null;
      });
    } catch (error) {
      setTemplatesError(error instanceof Error ? error.message : 'Failed to load marketing templates');
    } finally {
      setTemplatesLoading(false);
    }
  }, []);

  useEffect(() => {
    if (propertyFetchStatus === 'idle') {
      void fetchProperties().catch(() => {
        // store records fetch error state
      });
    }
  }, [propertyFetchStatus, fetchProperties]);

  useEffect(() => {
    void loadTemplates();
  }, [loadTemplates]);

  useEffect(() => {
    if (!properties.length) {
      return;
    }
    setSelectedPropertyId((current) => {
      if (current && properties.some((property) => String(property.id) === current)) {
        return current;
      }
      const firstId = String(properties[0].id);
      setSelectedPropertyInStore(firstId);
      return firstId;
    });
  }, [properties, setSelectedPropertyInStore]);

  const selectedProperty = useMemo(
    () => properties.find((property) => String(property.id) === selectedPropertyId) ?? null,
    [properties, selectedPropertyId],
  );

  const selectedTemplate = useMemo(
    () => (selectedTemplateId ? templates.find((template) => template.id === selectedTemplateId) ?? null : null),
    [templates, selectedTemplateId],
  );

  const handleSelectProperty = (propertyId: Property['id']) => {
    const normalizedId = String(propertyId);
    setSelectedPropertyId(normalizedId);
    setSelectedPropertyInStore(normalizedId);
    setPackageResult(null);
    setCampaignResult(null);
    setPackageError(null);
    setCampaignError(null);
  };

  const handleRefreshProperties = async () => {
    setIsRefreshingProperties(true);
    setPackageError(null);
    setCampaignError(null);
    setSeedError(null);
    try {
      await fetchProperties();
    } finally {
      setIsRefreshingProperties(false);
    }
  };

  const handleRefreshTemplates = async () => {
    await loadTemplates();
  };

  const handleCreateSampleProperty = async () => {
    setIsSeedingProperty(true);
    setSeedError(null);
    setPackageError(null);
    setCampaignError(null);
    try {
      const created = await addProperty(samplePropertyPayload);
      const idString = String(created.id);
      setSelectedPropertyId(idString);
      setSelectedPropertyInStore(idString);
      setPackageResult(null);
      setCampaignResult(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create sample listing';
      setSeedError(message);
    } finally {
      setIsSeedingProperty(false);
    }
  };

  const handleLaunchFullPackage = async () => {
    if (!selectedProperty) {
      setPackageError('Select a property to launch a package.');
      return;
    }
    const propertyIdValue = normalizeNumericId(selectedProperty.id);
    if (propertyIdValue === null) {
      setPackageError('Property identifier is invalid. Refresh properties and try again.');
      return;
    }

    setCreatingPackage(true);
    setPackageError(null);
    setPackageResult(null);

    try {
      const result = await createFullMarketingPackage({ propertyId: propertyIdValue });
      setPackageResult(result);
    } catch (error) {
      setPackageError(error instanceof Error ? error.message : 'Failed to create marketing package');
    } finally {
      setCreatingPackage(false);
    }
  };

  const handleLaunchTemplateCampaign = async () => {
    if (!selectedProperty) {
      setCampaignError('Select a property to create a campaign.');
      return;
    }
    if (!selectedTemplate) {
      setCampaignError('Choose a template to continue.');
      return;
    }

    const campaignType = campaignTypeByCategory[selectedTemplate.category?.toLowerCase() ?? ''];
    if (!campaignType) {
      setCampaignError('This template category is not supported yet.');
      return;
    }

    const propertyIdValue = normalizeNumericId(selectedProperty.id);
    if (propertyIdValue === null) {
      setCampaignError('Property identifier is invalid. Refresh properties and try again.');
      return;
    }

    setCreatingCampaign(true);
    setCampaignError(null);
    setCampaignResult(null);

    try {
      const result = await createMarketingCampaign({
        propertyId: propertyIdValue,
        campaignType,
        templateId: selectedTemplate.id,
        autoGenerateContent: true,
      });
      setCampaignResult(result);
    } catch (error) {
      setCampaignError(error instanceof Error ? error.message : 'Failed to create campaign');
    } finally {
      setCreatingCampaign(false);
    }
  };

  const campaignDetails = useMemo(() => {
    if (!campaignResult?.campaign) {
      return null;
    }
    const campaign = campaignResult.campaign as Record<string, unknown>;
    return {
      id: typeof campaign.id === 'number' || typeof campaign.id === 'string' ? String(campaign.id) : undefined,
      status:
        typeof campaign.status === 'string'
          ? campaign.status
          : typeof campaign.status === 'number'
          ? String(campaign.status)
          : undefined,
      type:
        typeof campaign.campaign_type === 'string'
          ? campaign.campaign_type
          : typeof campaign.campaign_type === 'number'
          ? String(campaign.campaign_type)
          : undefined,
      propertyTitle:
        typeof campaign.property_title === 'string'
          ? campaign.property_title
          : undefined,
    };
  }, [campaignResult]);

  return (
    <div className="flex h-full flex-col bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white/90 px-6 py-4 shadow-sm backdrop-blur">
        <div className="flex items-center gap-3">
          {onBack ? (
            <button
              onClick={onBack}
              className="rounded-xl border border-transparent px-3 py-1.5 text-sm font-medium text-slate-500 transition hover:border-slate-200 hover:text-slate-700"
            >
              &lt; Back
            </button>
          ) : (
            <span className="w-16" />
          )}
          <div>
            <h1 className="text-xl font-semibold text-slate-900">Marketing Automation</h1>
            <p className="text-sm text-slate-500">Launch cross-channel campaigns in a single flow.</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" aria-hidden />
          Live
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-6 pb-12 pt-6">
        <div className="mx-auto flex max-w-6xl flex-col gap-6">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Select Property</h2>
                <p className="text-sm text-slate-500">Choose a listing to tailor generated content.</p>
              </div>
              <div className="flex items-center gap-3">
                {propertyFetchError ? (
                  <span className="text-sm text-rose-600">{propertyFetchError}</span>
                ) : null}
                <button
                  onClick={handleRefreshProperties}
                  disabled={isRefreshingProperties || propertyFetchStatus === 'loading'}
                  className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-slate-300 hover:text-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isRefreshingProperties || propertyFetchStatus === 'loading' ? 'Refreshing...' : 'Refresh'}
                </button>
              </div>
            </div>

            {hasProperties ? (
              <div className="mt-5 grid gap-4 md:grid-cols-2">
                {properties.map((property) => {
                  const id = String(property.id);
                  const active = id === selectedPropertyId;
                  return (
                    <button
                      key={id}
                      onClick={() => handleSelectProperty(property.id)}
                      className={`rounded-xl border p-4 text-left transition ${
                        active
                          ? 'border-blue-400 bg-blue-50/70 shadow-sm'
                          : 'border-slate-200 bg-white hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <h3 className="text-base font-semibold text-slate-900">
                          {property.title || property.address || 'Untitled property'}
                        </h3>
                        {active ? <span className="text-xs font-semibold text-blue-600">SELECTED</span> : null}
                      </div>
                      <p className="mt-2 text-sm text-slate-500">{property.location || 'Location pending'}</p>
                      <p className="mt-3 text-sm text-slate-600">{formatPropertyMeta(property)}</p>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="mt-5 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
                <p>No properties available yet. Create a sample listing to exercise the marketing workflow.</p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <button
                    onClick={handleCreateSampleProperty}
                    disabled={isSeedingProperty}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {isSeedingProperty ? 'Creating sample listing...' : 'Create sample listing'}
                  </button>
                </div>
                {seedError ? <p className="mt-3 text-sm text-rose-600">{seedError}</p> : null}
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Templates</h2>
                <p className="text-sm text-slate-500">Select the campaign focus for your listing.</p>
              </div>
              <div className="flex items-center gap-3">
                {templatesError ? <span className="text-sm text-rose-600">{templatesError}</span> : null}
                <button
                  onClick={handleRefreshTemplates}
                  disabled={templatesLoading}
                  className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-slate-300 hover:text-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {templatesLoading ? 'Refreshing...' : 'Reload'}
                </button>
              </div>
            </div>

            {templatesLoading ? (
              <div className="mt-8 flex items-center justify-center">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-orange-200 border-t-orange-500" />
              </div>
            ) : templates.length ? (
              <ul className="mt-5 grid gap-4 md:grid-cols-3">
                {templates.map((template) => {
                  const active = template.id === selectedTemplateId;
                  return (
                    <li key={template.id}>
                      <button
                        onClick={() => setSelectedTemplateId(template.id)}
                        className={`flex h-full flex-col rounded-xl border p-4 text-left transition ${
                          active
                            ? 'border-orange-400 bg-orange-50 shadow-sm'
                            : 'border-slate-200 bg-white hover:border-slate-300'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <h3 className="text-base font-semibold text-slate-900">{template.name}</h3>
                          {active ? <span className="text-xs font-semibold text-orange-600">ACTIVE</span> : null}
                        </div>
                        <p className="mt-2 text-xs uppercase tracking-wide text-slate-400">
                          {formatTemplateMeta(template)}
                        </p>
                        <p className="mt-3 text-sm text-slate-600">{template.description || 'Description coming soon.'}</p>
                        {template.dubai_specific ? (
                          <span className="mt-3 inline-flex w-fit items-center rounded-full bg-emerald-50 px-2 py-1 text-[11px] font-medium text-emerald-600">
                            Dubai compliant
                          </span>
                        ) : null}
                      </button>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-slate-500">No templates available right now. Try refreshing shortly.</p>
            )}
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Launch Campaigns</h2>
                <p className="text-sm text-slate-500">
                  Generate a complete package or trigger a single campaign from the selected template.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={handleLaunchTemplateCampaign}
                  disabled={creatingCampaign || !hasProperties || !selectedTemplate}
                  className="rounded-lg border border-blue-500 px-5 py-2 text-sm font-semibold text-blue-600 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {creatingCampaign ? 'Creating campaign...' : 'Create template campaign'}
                </button>
                <button
                  onClick={handleLaunchFullPackage}
                  disabled={creatingPackage || !hasProperties}
                  className="rounded-lg bg-orange-600 px-5 py-2 text-sm font-semibold text-white shadow transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {creatingPackage ? 'Launching package...' : 'Launch full package'}
                </button>
              </div>
            </div>

            {packageError ? <p className="mt-4 text-sm text-rose-600">{packageError}</p> : null}
            {campaignError ? <p className="mt-2 text-sm text-rose-600">{campaignError}</p> : null}

            {packageResult ? (
              <div className="mt-6 rounded-xl border border-slate-200 bg-orange-50 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-base font-semibold text-orange-800">Full package scheduled</h3>
                    <p className="text-xs text-orange-700">
                      Created {new Date(packageResult.createdAt).toLocaleString()}
                    </p>
                    <p className="mt-2 text-xs uppercase tracking-wide text-orange-600">Status: {packageResult.status}</p>
                  </div>
                  <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-orange-600">
                    {packageResult.packageId}
                  </span>
                </div>
                <ul className="mt-4 space-y-2 text-sm text-orange-900">
                  {Object.entries(packageResult.campaigns).map(([channel, campaignId]) => (
                    <li key={channel} className="flex items-center justify-between">
                      <span className="capitalize">{channel.replace(/_/g, ' ')}</span>
                      <span className="font-semibold">Campaign #{campaignId}</span>
                    </li>
                  ))}
                </ul>
                {packageResult.nextSteps ? (
                  <p className="mt-3 text-sm text-orange-800">{packageResult.nextSteps}</p>
                ) : null}
              </div>
            ) : null}

            {campaignResult ? (
              <div className="mt-6 rounded-xl border border-slate-200 bg-blue-50 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-base font-semibold text-blue-800">Template campaign created</h3>
                    <p className="text-xs text-blue-700">Status: {campaignResult.status}</p>
                    {campaignDetails?.type ? (
                      <p className="mt-1 text-xs uppercase tracking-wide text-blue-600">
                        Type: {campaignDetails.type.replace(/_/g, ' ')}
                      </p>
                    ) : null}
                  </div>
                  <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-blue-600">
                    {campaignDetails?.id ? `ID ${campaignDetails.id}` : `Campaign ${campaignResult.campaignId}`}
                  </span>
                </div>
                {campaignDetails?.propertyTitle ? (
                  <p className="mt-3 text-sm text-blue-900">Property: {campaignDetails.propertyTitle}</p>
                ) : null}
                <p className="mt-3 text-xs text-blue-700">
                  The campaign enters the approval workflow automatically. Review assets in the Requests board.
                </p>
              </div>
            ) : null}
          </section>
        </div>
      </main>
    </div>
  );
};

export default MarketingView;