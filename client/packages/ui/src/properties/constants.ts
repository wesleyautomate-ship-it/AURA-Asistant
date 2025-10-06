/**
 * Property List Constants
 * =======================
 * 
 * Constants for property list components.
 */

import type { PropertyViewMode, PropertySortMode, ListingStatus } from '@propertypro/store';

/**
 * Quick filter options
 */
export interface QuickFilter {
  id: string;
  label: string;
  value: ListingStatus | 'all';
  count?: number;
}

export const DEFAULT_QUICK_FILTERS: QuickFilter[] = [
  { id: 'all', label: 'All Properties', value: 'all' },
  { id: 'live', label: 'Live', value: 'live' },
  { id: 'draft', label: 'Drafts', value: 'draft' },
  { id: 'pending', label: 'Pending', value: 'pending' },
  { id: 'sold', label: 'Sold', value: 'sold' },
];

/**
 * Sort options
 */
export interface SortOption {
  id: PropertySortMode;
  label: string;
  icon?: string;
}

export const SORT_OPTIONS: SortOption[] = [
  { id: 'newest', label: 'Newest First', icon: '🕐' },
  { id: 'oldest', label: 'Oldest First', icon: '🕑' },
  { id: 'price_desc', label: 'Price: High to Low', icon: '💰' },
  { id: 'price_asc', label: 'Price: Low to High', icon: '💵' },
  { id: 'area_desc', label: 'Area: Largest First', icon: '📐' },
  { id: 'area_asc', label: 'Area: Smallest First', icon: '📏' },
];

/**
 * Bulk action options
 */
export interface BulkAction {
  id: string;
  label: string;
  icon: string;
  confirmMessage?: string;
  variant?: 'default' | 'danger';
}

export const BULK_ACTIONS: BulkAction[] = [
  { id: 'publish', label: 'Publish Selected', icon: '🚀' },
  { id: 'unpublish', label: 'Unpublish Selected', icon: '⏸️' },
  { id: 'mark_sold', label: 'Mark as Sold', icon: '✅' },
  { id: 'duplicate', label: 'Duplicate Selected', icon: '📋' },
  { 
    id: 'delete', 
    label: 'Delete Selected', 
    icon: '🗑️',
    confirmMessage: 'Are you sure you want to delete the selected properties?',
    variant: 'danger',
  },
];

/**
 * View mode options
 */
export interface ViewModeOption {
  id: PropertyViewMode;
  label: string;
  icon: string;
}

export const VIEW_MODES: ViewModeOption[] = [
  { id: 'grid', label: 'Grid View', icon: '▦' },
  { id: 'table', label: 'Table View', icon: '☰' },
  { id: 'map', label: 'Map View', icon: '🗺️' },
];

/**
 * Calculate grid columns based on container width
 */
export function getGridColumns(width: number): number {
  if (width < 640) return 1;      // Mobile
  if (width < 1024) return 2;     // Tablet
  if (width < 1536) return 3;     // Desktop
  return 4;                        // Large desktop
}

/**
 * Get empty state message based on filters
 */
export function getEmptyStateMessage(hasFilters: boolean, searchQuery: string): string {
  if (searchQuery) {
    return `No properties found matching "${searchQuery}"`;
  }
  if (hasFilters) {
    return 'No properties match your filters. Try adjusting your search criteria.';
  }
  return 'No properties yet. Create your first property to get started!';
}

/**
 * Format bulk action confirmation message
 */
export function getBulkActionMessage(action: string, count: number): string {
  const messages: Record<string, string> = {
    publish: `Publish ${count} propert${count === 1 ? 'y' : 'ies'}?`,
    unpublish: `Unpublish ${count} propert${count === 1 ? 'y' : 'ies'}?`,
    mark_sold: `Mark ${count} propert${count === 1 ? 'y' : 'ies'} as sold?`,
    duplicate: `Duplicate ${count} propert${count === 1 ? 'y' : 'ies'}?`,
    delete: `Delete ${count} propert${count === 1 ? 'y' : 'ies'}? This action cannot be undone.`,
  };
  return messages[action] || `Perform action on ${count} propert${count === 1 ? 'y' : 'ies'}?`;
}