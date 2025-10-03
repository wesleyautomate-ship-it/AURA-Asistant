# Analytics Features (Beta-1)

## CMA Generator
- Select a subject property from current inventory
- Auto-identify comparable properties based on beds/baths/sqft tolerances
- Compute average/median price and price-per-sqft
- Recommend pricing strategy (aggressive vs standard) with rationale
- Export comps to CSV for sharing

## Performance Metrics
- Active vs Sold counts
- Median sold price-per-sqft
- Designed for quick briefing widgets

## Market Insights
- Insights cards (top neighborhoods, inventory change, avg DOM)
- Extendable to Alpha-2 analytics APIs

## UI/UX
- Teal palette `#0891b2` for analytics
- Date range filters: 7d, 30d, 90d, YTD
- Card-based layout; mobile-friendly

## Integration
- Data source: `src/store/propertyStore.ts`
- Utilities: `src/utils/analyticsUtils.ts`
- Components:
  - `src/components/analytics/CMAGenerator.tsx`
  - `src/components/analytics/PerformanceMetrics.tsx`
  - `src/components/analytics/MarketInsights.tsx`
