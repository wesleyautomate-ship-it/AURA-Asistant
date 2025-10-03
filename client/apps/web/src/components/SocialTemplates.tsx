import React from 'react';

export type SocialCategory = 'just-listed' | 'open-house' | 'in-contract' | 'just-sold' | 'feature-post' | 'custom';

export interface SocialTemplate {
  id: string;
  name: string;
  category: SocialCategory;
  aspect: 'square' | 'portrait' | 'landscape';
  previewUrl: string;
  brandColor?: string;
}

interface Props {
  onSelect?: (t: SocialTemplate) => void;
  brandColor?: string;
}

const templates: SocialTemplate[] = [
  { id: 'jl-1', name: 'Just Listed (Square)', category: 'just-listed', aspect: 'square', previewUrl: 'https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=600&q=80&auto=format&fit=crop' },
  { id: 'oh-1', name: 'Open House (Portrait)', category: 'open-house', aspect: 'portrait', previewUrl: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&q=80&auto=format&fit=crop' },
  { id: 'ic-1', name: 'In-Contract (Square)', category: 'in-contract', aspect: 'square', previewUrl: 'https://images.unsplash.com/photo-1501183638710-841dd1904471?w=600&q=80&auto=format&fit=crop' },
  { id: 'js-1', name: 'Just Sold (Landscape)', category: 'just-sold', aspect: 'landscape', previewUrl: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600&q=80&auto=format&fit=crop' },
  { id: 'fp-1', name: 'Feature Post (Square)', category: 'feature-post', aspect: 'square', previewUrl: 'https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?w=600&q=80&auto=format&fit=crop' },
];

const SocialTemplates: React.FC<Props> = ({ onSelect, brandColor = '#7c3aed' }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      <div className="p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">Social Template Gallery</h3>
        <div className="text-xs font-medium" style={{color: brandColor}}>Purple Theme</div>
      </div>
      <div className="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map(t => (
          <button key={t.id} onClick={() => onSelect?.(t)} className="group text-left border rounded-xl overflow-hidden hover:shadow-lg transition-shadow">
            <div className="aspect-video bg-gray-100 overflow-hidden">
              <img src={t.previewUrl} alt={t.name} className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform" />
            </div>
            <div className="p-3">
              <div className="text-sm font-semibold text-gray-800">{t.name}</div>
              <div className="text-xs text-gray-500 capitalize">{t.category.replace('-', ' ')}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SocialTemplates;
