import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

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

type Props = {
  onBack?: () => void;
};

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

const formatTemplateMeta = (template: MarketingTemplateSummary) => {
  const category = template.category ? template.category.toUpperCase() : 'TEMPLATE';
  const type = template.type ? template.type.replace(/_/g, ' ') : '';
  return type ? `${category} / ${type}` : category;
};

const formatPropertyMeta = (property: Property) => {
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
};

const normalizeNumericId = (value: Property['id']): number | null => {
  const maybeNumber = Number.parseInt(String(value), 10);
  return Number.isNaN(maybeNumber) ? null : maybeNumber;
};

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
      const message = error instanceof Error ? error.message : 'Failed to load marketing templates';
      setTemplatesError(message);
    } finally {
      setTemplatesLoading(false);
    }
  }, []);

  useEffect(() => {
    if (propertyFetchStatus === 'idle') {
      void fetchProperties().catch(() => {
        // fetch errors reported through store state
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
      Alert.alert('Demo listing failed', message);
    } finally {
      setIsSeedingProperty(false);
    }
  };

  const handleLaunchFullPackage = async () => {
    if (!selectedProperty) {
      const message = 'Select a property to launch a package.';
      setPackageError(message);
      Alert.alert('Property required', message);
      return;
    }
    const propertyIdValue = normalizeNumericId(selectedProperty.id);
    if (propertyIdValue === null) {
      const message = 'Property identifier is invalid. Refresh properties and try again.';
      setPackageError(message);
      Alert.alert('Property invalid', message);
      return;
    }

    setCreatingPackage(true);
    setPackageError(null);
    setPackageResult(null);

    try {
      const result = await createFullMarketingPackage({ propertyId: propertyIdValue });
      setPackageResult(result);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create marketing package';
      setPackageError(message);
      Alert.alert('Launch failed', message);
    } finally {
      setCreatingPackage(false);
    }
  };

  const handleLaunchTemplateCampaign = async () => {
    if (!selectedProperty) {
      const message = 'Select a property to create a campaign.';
      setCampaignError(message);
      Alert.alert('Property required', message);
      return;
    }
    if (!selectedTemplate) {
      const message = 'Choose a template to continue.';
      setCampaignError(message);
      Alert.alert('Template required', message);
      return;
    }

    const campaignType = campaignTypeByCategory[selectedTemplate.category?.toLowerCase() ?? ''];
    if (!campaignType) {
      const message = 'This template category is not supported yet.';
      setCampaignError(message);
      Alert.alert('Unsupported template', message);
      return;
    }

    const propertyIdValue = normalizeNumericId(selectedProperty.id);
    if (propertyIdValue === null) {
      const message = 'Property identifier is invalid. Refresh properties and try again.';
      setCampaignError(message);
      Alert.alert('Property invalid', message);
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
      const message = error instanceof Error ? error.message : 'Failed to create campaign';
      setCampaignError(message);
      Alert.alert('Campaign failed', message);
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

  const renderTemplate = ({ item }: { item: MarketingTemplateSummary }) => {
    const active = item.id === selectedTemplateId;
    return (
      <TouchableOpacity
        style={[styles.templateCard, active && styles.templateCardActive]}
        onPress={() => setSelectedTemplateId(item.id)}
      >
        <View style={styles.templateHeader}>
          <Text style={styles.templateTitle}>{item.name}</Text>
          {item.dubai_specific ? <Text style={styles.templateTag}>Dubai</Text> : null}
        </View>
        <Text style={styles.templateMeta}>{formatTemplateMeta(item)}</Text>
        <Text numberOfLines={2} style={styles.templateDescription}>
          {item.description || 'Description coming soon.'}
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        {onBack ? (
          <TouchableOpacity style={styles.backButton} onPress={onBack}>
            <Text style={styles.backText}>&lt; Back</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.backPlaceholder} />
        )}
        <Text style={styles.headerTitle}>Marketing Automation</Text>
        <View style={styles.backPlaceholder} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.card}>
          <View style={styles.sectionHeader}>
            <View>
              <Text style={styles.sectionTitle}>Select Property</Text>
              <Text style={styles.sectionSubtitle}>Choose a listing to tailor generated content.</Text>
            </View>
            <TouchableOpacity
              style={[
                styles.refreshButton,
                (isRefreshingProperties || propertyFetchStatus === 'loading') && styles.refreshButtonDisabled,
              ]}
              disabled={isRefreshingProperties || propertyFetchStatus === 'loading'}
              onPress={handleRefreshProperties}
            >
              <Text style={styles.refreshButtonText}>
                {isRefreshingProperties || propertyFetchStatus === 'loading' ? 'Refreshing...' : 'Refresh'}
              </Text>
            </TouchableOpacity>
          </View>
          {propertyFetchError ? <Text style={styles.errorText}>{propertyFetchError}</Text> : null}

          {hasProperties ? (
            <View style={styles.propertyGrid}>
              {properties.map((property) => {
                const id = String(property.id);
                const active = id === selectedPropertyId;
                return (
                  <TouchableOpacity
                    key={id}
                    style={[styles.propertyCard, active && styles.propertyCardActive]}
                    onPress={() => handleSelectProperty(property.id)}
                  >
                    <Text style={styles.propertyTitle}>{property.title || property.address || 'Untitled property'}</Text>
                    <Text style={styles.propertyMeta}>{property.location || 'Location pending'}</Text>
                    <Text style={styles.propertyMeta}>{formatPropertyMeta(property)}</Text>
                    {active ? <Text style={styles.propertySelected}>Selected</Text> : null}
                  </TouchableOpacity>
                );
              })}
            </View>
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateText}>
                No properties available yet. Create a sample listing to exercise the marketing workflow.
              </Text>
              <TouchableOpacity
                style={[styles.primaryAction, styles.emptyStateAction, isSeedingProperty && styles.actionDisabled]}
                onPress={handleCreateSampleProperty}
                disabled={isSeedingProperty}
              >
                <Text style={styles.primaryActionText}>
                  {isSeedingProperty ? 'Creating sample listing...' : 'Create sample listing'}
                </Text>
              </TouchableOpacity>
              {seedError ? <Text style={styles.errorText}>{seedError}</Text> : null}
            </View>
          )}
        </View>

        <View style={styles.card}>
          <View style={styles.sectionHeader}>
            <View>
              <Text style={styles.sectionTitle}>Templates</Text>
              <Text style={styles.sectionSubtitle}>Select the campaign focus for your listing.</Text>
            </View>
            <TouchableOpacity
              style={[styles.refreshButton, templatesLoading && styles.refreshButtonDisabled]}
              disabled={templatesLoading}
              onPress={loadTemplates}
            >
              <Text style={styles.refreshButtonText}>{templatesLoading ? 'Refreshing...' : 'Reload'}</Text>
            </TouchableOpacity>
          </View>
          {templatesError ? <Text style={styles.errorText}>{templatesError}</Text> : null}

          {templatesLoading ? (
            <ActivityIndicator size='small' color='#ea580c' style={styles.templatesLoader} />
          ) : templates.length ? (
            <FlatList
              data={templates}
              keyExtractor={(item) => String(item.id)}
              renderItem={renderTemplate}
              ItemSeparatorComponent={() => <View style={styles.templateSeparator} />}
              scrollEnabled={false}
            />
          ) : (
            <Text style={styles.helperText}>No templates available right now. Try refreshing shortly.</Text>
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Launch Campaigns</Text>
          <Text style={styles.sectionSubtitle}>
            Generate a complete package or trigger a single campaign from the selected template.
          </Text>

          <View style={styles.actionRow}>
            <TouchableOpacity
              style={[
                styles.secondaryAction,
                (creatingCampaign || !hasProperties || !selectedTemplate) && styles.actionDisabled,
              ]}
              onPress={handleLaunchTemplateCampaign}
              disabled={creatingCampaign || !hasProperties || !selectedTemplate}
            >
              <Text style={styles.secondaryActionText}>
                {creatingCampaign ? 'Creating campaign...' : 'Create template campaign'}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.primaryAction, (creatingPackage || !hasProperties) && styles.actionDisabled]}
              onPress={handleLaunchFullPackage}
              disabled={creatingPackage || !hasProperties}
            >
              <Text style={styles.primaryActionText}>
                {creatingPackage ? 'Launching package...' : 'Launch full package'}
              </Text>
            </TouchableOpacity>
          </View>

          {packageError ? <Text style={styles.errorText}>{packageError}</Text> : null}
          {campaignError ? <Text style={styles.errorText}>{campaignError}</Text> : null}

          {packageResult ? (
            <View style={[styles.resultCard, styles.packageResult]}>
              <View style={styles.resultHeader}>
                <View>
                  <Text style={styles.resultTitle}>Full package scheduled</Text>
                  <Text style={styles.resultMeta}>Created {new Date(packageResult.createdAt).toLocaleString()}</Text>
                  <Text style={styles.resultMeta}>Status: {packageResult.status}</Text>
                </View>
                <View style={styles.resultBadge}>
                  <Text style={styles.resultBadgeText}>{packageResult.packageId}</Text>
                </View>
              </View>
              {Object.entries(packageResult.campaigns).map(([channel, campaignId]) => (
                <Text key={channel} style={styles.resultRow}>
                  {channel.replace(/_/g, ' ')} - Campaign #{campaignId}
                </Text>
              ))}
              {packageResult.nextSteps ? (
                <Text style={styles.resultNextSteps}>{packageResult.nextSteps}</Text>
              ) : null}
            </View>
          ) : null}

          {campaignResult ? (
            <View style={[styles.resultCard, styles.campaignResult]}>
              <View style={styles.resultHeader}>
                <View>
                  <Text style={styles.resultTitle}>Template campaign created</Text>
                  <Text style={styles.resultMeta}>Status: {campaignResult.status}</Text>
                  {campaignDetails?.type ? (
                    <Text style={styles.resultMeta}>Type: {campaignDetails.type.replace(/_/g, ' ')}</Text>
                  ) : null}
                </View>
                <View style={styles.resultBadge}>
                  <Text style={styles.resultBadgeText}>
                    {campaignDetails?.id ? `ID ${campaignDetails.id}` : `Campaign ${campaignResult.campaignId}`}
                  </Text>
                </View>
              </View>
              {campaignDetails?.propertyTitle ? (
                <Text style={styles.resultRow}>Property: {campaignDetails.propertyTitle}</Text>
              ) : null}
              <Text style={styles.resultNextSteps}>
                The campaign enters the approval workflow automatically. Review assets in the Requests board.
              </Text>
            </View>
          ) : null}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#e2e8f0',
  },
  backButton: {
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderRadius: 8,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: '#cbd5f5',
  },
  backText: {
    color: '#475569',
    fontSize: 13,
  },
  backPlaceholder: {
    width: 64,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0f172a',
  },
  content: {
    paddingHorizontal: 16,
    paddingBottom: 24,
    gap: 16,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginBottom: 16,
    shadowColor: '#000000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 2,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0f172a',
  },
  sectionSubtitle: {
    fontSize: 13,
    color: '#475569',
    marginTop: 4,
  },
  refreshButton: {
    borderWidth: 1,
    borderColor: '#cbd5f5',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#ffffff',
  },
  refreshButtonDisabled: {
    opacity: 0.6,
  },
  refreshButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1e40af',
  },
  propertyGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
    marginHorizontal: -4,
  },
  propertyCard: {
    width: '48%',
    marginHorizontal: 4,
    marginBottom: 12,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'transparent',
    backgroundColor: '#f8fafc',
  },
  propertyCardActive: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
  },
  propertyTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0f172a',
  },
  propertyMeta: {
    fontSize: 12,
    color: '#475569',
    marginTop: 4,
  },
  propertySelected: {
    marginTop: 8,
    fontSize: 11,
    fontWeight: '600',
    color: '#2563eb',
  },
  emptyState: {
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: '#cbd5f5',
    borderRadius: 12,
    padding: 16,
    backgroundColor: '#f1f5f9',
    gap: 12,
  },
  emptyStateText: {
    fontSize: 13,
    color: '#475569',
  },
  emptyStateAction: {
    marginTop: 4,
  },
  helperText: {
    fontSize: 13,
    color: '#475569',
  },
  templatesLoader: {
    marginTop: 8,
  },
  templateSeparator: {
    height: 12,
  },
  templateCard: {
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'transparent',
    backgroundColor: '#f8fafc',
    padding: 12,
  },
  templateCardActive: {
    borderColor: '#fb923c',
    backgroundColor: '#fff7ed',
  },
  templateHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  templateTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0f172a',
  },
  templateTag: {
    fontSize: 11,
    fontWeight: '600',
    color: '#047857',
    backgroundColor: '#d1fae5',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  templateMeta: {
    fontSize: 11,
    color: '#475569',
    marginTop: 4,
  },
  templateDescription: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 6,
  },
  actionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
    gap: 12,
  },
  primaryAction: {
    flex: 1,
    backgroundColor: '#ea580c',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  primaryActionText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  secondaryAction: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  secondaryActionText: {
    color: '#1d4ed8',
    fontSize: 14,
    fontWeight: '600',
  },
  actionDisabled: {
    opacity: 0.6,
  },
  errorText: {
    color: '#dc2626',
    fontSize: 12,
    marginTop: 8,
  },
  resultCard: {
    marginTop: 16,
    borderRadius: 12,
    padding: 14,
  },
  packageResult: {
    backgroundColor: '#fff7ed',
    borderWidth: 1,
    borderColor: '#fed7aa',
  },
  campaignResult: {
    backgroundColor: '#eff6ff',
    borderWidth: 1,
    borderColor: '#bfdbfe',
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  resultTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#0f172a',
  },
  resultMeta: {
    fontSize: 12,
    color: '#475569',
    marginTop: 2,
  },
  resultBadge: {
    backgroundColor: '#ffffff',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: '#fed7aa',
  },
  resultBadgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#c2410c',
  },
  resultRow: {
    fontSize: 12,
    color: '#0f172a',
    marginTop: 4,
  },
  resultNextSteps: {
    fontSize: 12,
    color: '#475569',
    marginTop: 8,
  },
});

export default MarketingView;