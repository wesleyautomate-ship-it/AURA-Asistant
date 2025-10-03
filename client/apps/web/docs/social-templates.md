# Social Templates for Strategy Packages (Beta-4)

This document enumerates the branded social templates available for coordination with Strategy/Packages.

## Categories

- Just Listed
- Open House
- In-Contract
- Just Sold
- Feature Post
- Custom Campaign

## Template Metadata

Each template (see `src/components/SocialTemplates.tsx`) provides:

- id: string
- name: string
- category: 'just-listed' | 'open-house' | 'in-contract' | 'just-sold' | 'feature-post' | 'custom'
- aspect: 'square' | 'portrait' | 'landscape'
- previewUrl: string
- brandColor: defaults to purple `#7c3aed`

## Auto-Population

Templates and posts can auto-populate fields from property data (Beta-1):

- address, price, beds, baths, sqft, imageUrl

## Usage by Packages (Beta-4)

- Packages can select a category template and merge with property + marketing assets
- Coordinate with `SocialCampaigns` and `PostScheduler` to plan multi-platform posting

## File References

- `frontend/src/components/SocialTemplates.tsx`
- `frontend/src/components/SocialCampaigns.tsx`
- `frontend/src/components/PostScheduler.tsx`
- `frontend/src/components/PlatformConnections.tsx`
- `frontend/src/services/socialMediaApi.ts`
