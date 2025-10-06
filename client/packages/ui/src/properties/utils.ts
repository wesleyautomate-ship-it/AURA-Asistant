/**
 * Property Utils
 * ==============
 * 
 * Shared utility functions for property components.
 */

import type { Property, ListingStatus } from '@propertypro/store';

/**
 * Format price in AED
 */
export function formatPrice(price: number): string {
  if (price >= 1000000) {
    return `AED ${(price / 1000000).toFixed(2)}M`;
  }
  if (price >= 1000) {
    return `AED ${(price / 1000).toFixed(0)}K`;
  }
  return `AED ${price.toLocaleString()}`;
}

/**
 * Format area in sqft
 */
export function formatArea(area: number | null): string {
  if (area === null) return 'N/A';
  return `${area.toLocaleString()} sqft`;
}

/**
 * Get status badge color
 */
export function getStatusColor(status: ListingStatus): string {
  const colors: Record<ListingStatus, string> = {
    draft: '#6B7280',      // gray
    live: '#10B981',       // green
    sold: '#3B82F6',       // blue
    withdrawn: '#F59E0B',  // orange
    pending: '#FCD34D',    // yellow
    pocket: '#8B5CF6',     // purple
    archived: '#9CA3AF',   // light gray
  };
  return colors[status] || colors.draft;
}

/**
 * Get status label
 */
export function getStatusLabel(status: ListingStatus): string {
  const labels: Record<ListingStatus, string> = {
    draft: 'Draft',
    live: 'Live',
    sold: 'Sold',
    withdrawn: 'Withdrawn',
    pending: 'Pending',
    pocket: 'Pocket',
    archived: 'Archived',
  };
  return labels[status] || status;
}

/**
 * Get property type display label
 */
export function getPropertyTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    apartment: 'Apartment',
    villa: 'Villa',
    townhouse: 'Townhouse',
    penthouse: 'Penthouse',
    duplex: 'Duplex',
    studio: 'Studio',
  };
  return labels[type] || type;
}

/**
 * Get primary image URL
 */
export function getPrimaryImage(property: Property): string | null {
  if (property.images && property.images.length > 0) {
    return property.images[0];
  }
  return null;
}

/**
 * Generate property metrics
 */
export function getPropertyMetrics(property: Property) {
  return {
    beds: property.beds,
    baths: property.baths,
    area: property.areaSqft,
    hasFloorPlan: !!property.floorPlanUrl,
    hasVirtualTour: !!property.virtualTourUrl,
  };
}

/**
 * Check if property has AI insights
 */
export function hasAIInsights(property: Property): boolean {
  return !!(property.marketData && Object.keys(property.marketData).length > 0);
}

/**
 * Get quick actions based on status
 */
export function getQuickActions(property: Property): Array<{ id: string; label: string; icon: string }> {
  const actions: Array<{ id: string; label: string; icon: string }> = [
    { id: 'view', label: 'View Details', icon: '👁️' },
    { id: 'edit', label: 'Edit', icon: '✏️' },
  ];

  if (property.listingStatus === 'draft') {
    actions.push({ id: 'publish', label: 'Publish', icon: '🚀' });
  } else if (property.listingStatus === 'live') {
    actions.push({ id: 'unpublish', label: 'Unpublish', icon: '⏸️' });
  }

  actions.push({ id: 'duplicate', label: 'Duplicate', icon: '📋' });
  actions.push({ id: 'share', label: 'Share', icon: '🔗' });
  actions.push({ id: 'delete', label: 'Delete', icon: '🗑️' });

  return actions;
}