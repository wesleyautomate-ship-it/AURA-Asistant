import React from 'react';

export interface TemplateItem {
  id: string;
  name: string;
  category: 'postcard' | 'email' | 'social' | 'print';
  previewUrl: string;
  brandColor?: string;
}

interface Props {
  onSelect?: (template: TemplateItem) => void;
}

const templates: TemplateItem[] = [
  { id: 't1', name: 'Just Listed (Purple)', category: 'postcard', previewUrl: 'https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=600&q=80&auto=format&fit=crop' },
  { id: 't2', name: 'Open House Invite', category: 'email', previewUrl: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&q=80&auto=format&fit=crop' },
  { id: 't3', name: 'Market Update', category: 'email', previewUrl: 'https://images.unsplash.com/photo-1501183638710-841dd1904471?w=600&q=80&auto=format&fit=crop' },
  { id: 't4', name: 'Price Reduced', category: 'social', previewUrl: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600&q=80&auto=format&fit=crop' },
  { id: 't5', name: 'Just Sold (A4)', category: 'print', previewUrl: 'https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?w=600&q=80&auto=format&fit=crop' },
];

const MarketingTemplates: React.FC<Props> = ({ onSelect }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      <div className="p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">Template Gallery</h3>
        <div className="text-xs font-medium" style={{color:'#7c3aed'}}>Purple Theme</div>
      </div>
      <div className="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map(t => (
          <button key={t.id} onClick={() => onSelect?.(t)} className="group text-left border rounded-xl overflow-hidden hover:shadow-lg transition-shadow">
            <div className="aspect-video bg-gray-100 overflow-hidden">
              <img src={t.previewUrl} alt={t.name} className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform" />
            </div>
            <div className="p-3">
              <div className="text-sm font-semibold text-gray-800">{t.name}</div>
              <div className="text-xs text-gray-500 capitalize">{t.category}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default MarketingTemplates;
