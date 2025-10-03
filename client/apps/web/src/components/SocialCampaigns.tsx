import React from 'react';
import type { SocialTemplate } from './SocialTemplates';

interface Props {
  selectedTemplate?: SocialTemplate | null;
  property?: {
    title?: string;
    address?: string;
    price?: number | string;
    beds?: number;
    baths?: number;
    sqft?: number;
    imageUrl?: string;
  } | null;
}

const SocialCampaigns: React.FC<Props> = ({ selectedTemplate, property }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      <div className="p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">Multi-Platform Coordination</h3>
        <div className="text-xs text-gray-500">Coordinate with Marketing</div>
      </div>
      <div className="px-4 pb-4 space-y-2 text-sm text-gray-700">
        <div>
          <span className="font-semibold">Template:</span> {selectedTemplate ? selectedTemplate.name : 'None selected'}
        </div>
        <div>
          <span className="font-semibold">Property:</span> {property?.title || property?.address || 'No property selected'}
        </div>
        <div className="text-xs text-gray-500">This section will coordinate campaigns across social, email, and print using your marketing assets.</div>
      </div>
    </div>
  );
};

export default SocialCampaigns;
