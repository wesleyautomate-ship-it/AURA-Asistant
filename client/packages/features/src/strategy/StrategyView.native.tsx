import React, { useEffect, useMemo, useState } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import { usePropertyStore } from '@propertypro/store';
import type { Property } from '@propertypro/store';

type Props = {
  onBack?: () => void;
};

const StrategyView: React.FC<Props> = ({ onBack }) => {
  const propertyStore = usePropertyStore();
  const properties = propertyStore.items as Property[];
  const fetchProperties = usePropertyStore((state) => state.fetchProperties);

  const [selectedPropertyId, setSelectedPropertyId] = useState<string>('');

  useEffect(() => {
    fetchProperties().catch(() => undefined);
  }, [fetchProperties]);

  useEffect(() => {
    if (properties.length > 0 && !selectedPropertyId) {
      setSelectedPropertyId(String(properties[0].id));
    }
  }, [properties, selectedPropertyId]);

  const selectedProperty = useMemo(() => {
    if (!selectedPropertyId) {
      return properties[0] ?? null;
    }
    return properties.find((property) => String(property.id) === selectedPropertyId) ?? null;
  }, [properties, selectedPropertyId]);

  const persona = selectedProperty
    ? `${selectedProperty.beds}-bed ${selectedProperty.propertyType?.toUpperCase?.() || 'HOME'} seekers`
    : 'Lifestyle-focused buyers';

  const marketingTimeline = [
    {
      id: 'prep',
      title: 'Week 1 - Prep Assets',
      detail: 'Book premium photos, capture 3D walkthrough, publish AI brochure with neighborhood proof points.',
    },
    {
      id: 'launch',
      title: 'Week 2 - Launch Campaign',
      detail: 'Trigger email and WhatsApp touchpoints, boost carousel ads, invite concierge network.',
    },
    {
      id: 'events',
      title: 'Week 3 - Live Events',
      detail: 'Host twilight open house with remote co-host, follow up prospects with AI talk tracks.',
    },
    {
      id: 'negotiation',
      title: 'Week 4 - Negotiation',
      detail: 'AI watches offers, drafts counters, and surfaces concessions aligned to buyer priorities.',
    },
  ];

  const audienceSegments = [
    'Upscale renters relocating to Dubai Marina',
    'Remote workers searching for waterfront living',
    'Investors targeting short-let yield with premium finishings',
  ];

  const channelPlan = [
    'Instagram: Reels + Stories showcasing balcony views and marina skyline',
    'Email nurture: Three-part drip sharing ROI stats, concierge perks, and virtual tour link',
    'WhatsApp broadcast: Invite VIP clients with personalised voice memo recorded in Command Center',
  ];

  const negotiationTips = [
    'Anchor price with CMA overlays and rental income models during first viewing.',
    'Use Command Center call summaries to highlight unresolved buyer objections.',
    'Offer smart-home setup credit or furniture staging removal to close premium leads.',
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          {onBack ? (
            <TouchableOpacity accessibilityRole="button" style={styles.backButton} onPress={onBack}>
              <Text style={styles.backText}>{'< Back'}</Text>
            </TouchableOpacity>
          ) : (
            <View style={styles.backPlaceholder} />
          )}
          <View>
            <Text style={styles.title}>Strategy Command</Text>
            <Text style={styles.subtitle}>Listing, audience, and negotiation intel in a single timeline.</Text>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Select Property</Text>
          <View style={styles.propertyRow}>
            {properties.length === 0 ? (
              <Text style={styles.helperText}>No properties available. Add a listing to unlock strategy guidance.</Text>
            ) : (
              properties.map((property) => {
                const active = String(property.id) === selectedPropertyId;
                return (
                  <TouchableOpacity
                    key={property.id}
                    accessibilityRole="button"
                    style={[styles.propertyChip, active && styles.propertyChipActive]}
                    onPress={() => setSelectedPropertyId(String(property.id))}
                  >
                    <Text style={[styles.propertyChipText, active && styles.propertyChipTextActive]}>
                      {property.title || property.address || 'Untitled Property'}
                    </Text>
                  </TouchableOpacity>
                );
              })
            )}
          </View>
          {selectedProperty ? (
            <View style={styles.propertySummary}>
              <Text style={styles.propertySummaryTitle}>{selectedProperty.title || 'Property Overview'}</Text>
              <Text style={styles.helperText}>
                {selectedProperty.location} | {selectedProperty.beds} bd | {selectedProperty.baths} ba |
                {selectedProperty.sqft ? ` ${selectedProperty.sqft} sqft` : ' Size pending'}
              </Text>
            </View>
          ) : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Listing Positioning</Text>
          <Text style={styles.helperText}>Primary persona: {persona}</Text>
          <Text style={styles.bodyText}>
            Lead with immersive lifestyle visuals, highlight marina skyline, and reinforce concierge-style upgrades that resonate
            with {persona.toLowerCase()}.
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Targeting Playbook</Text>
          <View style={styles.row}>
            <View style={styles.column}>
              <Text style={styles.columnTitle}>Audience Segments</Text>
              {audienceSegments.map((item) => (
                <Text key={item} style={styles.bodyBullet}>
                  • {item}
                </Text>
              ))}
            </View>
            <View style={styles.column}>
              <Text style={styles.columnTitle}>Channel Plan</Text>
              {channelPlan.map((item) => (
                <Text key={item} style={styles.bodyBullet}>
                  • {item}
                </Text>
              ))}
            </View>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Marketing Timeline</Text>
          {marketingTimeline.map((entry) => (
            <View key={entry.id} style={styles.timelineRow}>
              <View style={styles.timelineBullet} />
              <View style={styles.timelineContent}>
                <Text style={styles.timelineTitle}>{entry.title}</Text>
                <Text style={styles.bodyText}>{entry.detail}</Text>
              </View>
            </View>
          ))}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Negotiation Moves</Text>
          {negotiationTips.map((tip) => (
            <Text key={tip} style={styles.bodyBullet}>
              • {tip}
            </Text>
          ))}
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
  content: {
    paddingHorizontal: 16,
    paddingBottom: 48,
    gap: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  backButton: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    backgroundColor: '#e2e8f0',
  },
  backPlaceholder: {
    width: 60,
  },
  backText: {
    fontWeight: '600',
    color: '#0f172a',
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0f172a',
  },
  subtitle: {
    fontSize: 13,
    color: '#475569',
    marginTop: 4,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 18,
    shadowColor: '#000000',
    shadowOpacity: 0.06,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 12,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: 10,
  },
  helperText: {
    fontSize: 13,
    color: '#475569',
  },
  bodyText: {
    fontSize: 14,
    color: '#1f2937',
    marginTop: 8,
    lineHeight: 20,
  },
  bodyBullet: {
    fontSize: 14,
    color: '#1f2937',
    marginTop: 6,
    lineHeight: 20,
  },
  propertyRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  propertyChip: {
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    paddingVertical: 6,
    paddingHorizontal: 12,
    backgroundColor: '#f8fafc',
  },
  propertyChipActive: {
    backgroundColor: '#e0f2fe',
    borderColor: '#38bdf8',
  },
  propertyChipText: {
    fontSize: 12,
    color: '#475569',
  },
  propertyChipTextActive: {
    color: '#0f172a',
    fontWeight: '600',
  },
  propertySummary: {
    marginTop: 12,
  },
  propertySummaryTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: 4,
  },
  row: {
    flexDirection: 'row',
    gap: 16,
  },
  column: {
    flex: 1,
  },
  columnTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: 6,
  },
  timelineRow: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  timelineBullet: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#0ea5e9',
    marginTop: 6,
  },
  timelineContent: {
    flex: 1,
    borderLeftWidth: 1,
    borderLeftColor: '#bae6fd',
    paddingLeft: 12,
  },
  timelineTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0f172a',
  },
});

export default StrategyView;