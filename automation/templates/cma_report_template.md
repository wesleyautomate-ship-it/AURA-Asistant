# 🏘️ CMA Report Template for AI Content Generation

## Template Purpose
This template guides AI content generation for Comparative Market Analysis (CMA) reports in AURA RealtorProAI.

## Content Structure

### Executive Summary
```
Property: [Property Address]
Estimated Value: $[Price Range]
Market Position: [Above/Below/At Market]
Recommendation: [Buy/Sell/Hold Recommendation]
```

### Property Overview
- **Address**: [Full Property Address]
- **Property Type**: [Single Family/Condo/Townhouse/etc.]
- **Bedrooms**: [Number]
- **Bathrooms**: [Number]
- **Square Footage**: [Total Sq Ft]
- **Lot Size**: [Lot Dimensions]
- **Year Built**: [Construction Year]
- **Key Features**: [Notable amenities and features]

### Market Analysis

#### Comparable Properties (3-5 Recent Sales)
For each comparable:
```
Address: [Property Address]
Sale Date: [MM/DD/YYYY]
Sale Price: $[Amount]
Price per Sq Ft: $[Amount]
Days on Market: [Number of days]
Similarities: [How it compares to subject property]
Adjustments: [Price adjustments made and reasoning]
```

#### Active Listings (2-3 Current Competitors)
For each active listing:
```
Address: [Property Address]
List Price: $[Amount]
Days on Market: [Number of days]
Price per Sq Ft: $[Amount]
Competition Level: [High/Medium/Low]
Market Position: [Priced above/below/at market]
```

### Market Conditions
- **Market Trend**: [Rising/Stable/Declining]
- **Inventory Level**: [High/Normal/Low]
- **Average Days on Market**: [Number of days]
- **Price Trends**: [% change over 6-12 months]
- **Buyer Demand**: [High/Moderate/Low]
- **Seasonal Factors**: [Any seasonal considerations]

### Valuation Analysis

#### Price Recommendation
```
Conservative Estimate: $[Amount]
Market Value Estimate: $[Amount]
Optimistic Estimate: $[Amount]

Recommended List Price: $[Amount]
Rationale: [Explanation of pricing strategy]
```

#### Adjustments Made
- **Condition Adjustments**: $[Amount] ([Reason])
- **Feature Adjustments**: $[Amount] ([Reason])
- **Location Adjustments**: $[Amount] ([Reason])
- **Market Timing**: $[Amount] ([Reason])

### Marketing Strategy
- **Target Market**: [First-time buyers/Move-up buyers/Investors/etc.]
- **Key Selling Points**: [Top 3-5 features to highlight]
- **Pricing Strategy**: [Competitive/Aggressive/Premium positioning]
- **Marketing Timeline**: [Recommended timeframe]

### Next Steps
1. **For Sellers**: [Specific recommendations]
2. **For Buyers**: [Offer strategy recommendations]
3. **Market Monitoring**: [What to watch for changes]
4. **Follow-up Actions**: [Timeline for reassessment]

## AI Generation Prompts

### Property Description Prompt
```
Generate a compelling property description for a [property type] with [bedrooms]BR/[bathrooms]BA, [sq ft] sq ft, built in [year], located at [address]. Highlight [key features] and position it as [market position] in the current market.
```

### Market Analysis Prompt
```
Analyze the real estate market for [area/neighborhood] focusing on [property type] properties. Current market conditions show [inventory level] inventory with [trend direction] prices. Provide insights on buyer behavior, competition, and pricing recommendations.
```

### Valuation Prompt
```
Based on comparable sales data: [comp 1: address, sale price, date], [comp 2: details], [comp 3: details], and current active listings, provide a valuation analysis for [subject property details]. Consider market conditions, property features, and location factors.
```

## Quality Checklist

### Content Requirements
- [ ] All property details accurate and complete
- [ ] Minimum 3 comparable sales within 6 months
- [ ] Market conditions clearly explained
- [ ] Pricing recommendation with rationale
- [ ] Professional language and formatting
- [ ] No spelling or grammatical errors

### Data Validation
- [ ] Property details match MLS/public records
- [ ] Comparable properties truly comparable
- [ ] Sale dates and prices accurate
- [ ] Market statistics current and relevant
- [ ] All calculations correct

### Client Communication
- [ ] Language appropriate for client sophistication level
- [ ] Technical terms explained when used
- [ ] Clear actionable recommendations
- [ ] Professional presentation format
- [ ] Contact information and next steps included

## Output Format Specifications

### File Naming Convention
```
CMA_[PropertyAddress]_[MMDDYYYY].pdf
Example: CMA_123MainSt_10112024.pdf
```

### Document Structure
1. **Cover Page**: Property photo, address, date, agent information
2. **Executive Summary**: Key findings and recommendations (1 page)
3. **Property Details**: Complete property information (1 page)
4. **Market Analysis**: Comparables and market conditions (2-3 pages)
5. **Valuation**: Price analysis and recommendations (1 page)
6. **Appendix**: Supporting data and disclaimers (1-2 pages)

## Customization Variables

### Market-Specific Adjustments
- **Urban Markets**: Focus on walkability, transit, amenities
- **Suburban Markets**: Emphasize schools, family features, commute
- **Rural Markets**: Highlight land, privacy, recreational opportunities
- **Luxury Markets**: Focus on unique features, prestige, investment value

### Property Type Variations
- **Single Family**: Neighborhood, schools, yard, parking
- **Condos**: Building amenities, HOA fees, urban lifestyle
- **Townhouses**: Community features, maintenance, value
- **Investment Properties**: Cash flow, cap rates, tenant demand

This template ensures consistent, professional, and comprehensive CMA reports generated through AI assistance while maintaining the flexibility to customize for specific properties and market conditions.