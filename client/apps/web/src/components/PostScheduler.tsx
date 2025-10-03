import React, { useMemo, useState } from 'react';
import type { Platform } from '../services/socialMediaApi';

interface Props {
  defaultCaption?: string;
  defaultImageUrl?: string;
  onPostNow?: (payload: { caption: string; imageUrl?: string; platforms: Platform[] }) => void;
  onSchedule?: (payload: { caption: string; imageUrl?: string; platforms: Platform[]; scheduledAt: string }) => void;
}

const PostScheduler: React.FC<Props> = ({ defaultCaption = '', defaultImageUrl, onPostNow, onSchedule }) => {
  const [caption, setCaption] = useState(defaultCaption);
  const [imageUrl, setImageUrl] = useState(defaultImageUrl || '');
  const [platforms, setPlatforms] = useState<Platform[]>(['instagram']);
  const [date, setDate] = useState<string>('');
  const [time, setTime] = useState<string>('');

  const scheduledAt = useMemo(() => {
    if (!date || !time) return '';
    const iso = new Date(`${date}T${time}:00`).toISOString();
    return iso;
  }, [date, time]);

  const togglePlatform = (p: Platform) => {
    setPlatforms(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      <div className="p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">Posting & Scheduling</h3>
        <div className="text-xs text-gray-500">Multi-platform</div>
      </div>
      <div className="px-4 pb-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <textarea value={caption} onChange={e=>setCaption(e.target.value)} className="border rounded-md px-3 py-2 text-sm h-24" placeholder="Write caption..." />
          <div className="space-y-2">
            <input value={imageUrl} onChange={e=>setImageUrl(e.target.value)} className="border rounded-md px-3 py-2 text-sm w-full" placeholder="Image URL (optional)" />
            {imageUrl && <img src={imageUrl} alt="preview" className="w-full h-28 object-cover rounded-md border" />}
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <label className={`px-3 py-1 rounded-md border ${platforms.includes('instagram')?'bg-purple-600 text-white border-purple-600':'bg-white text-gray-800'}`}>
            <input type="checkbox" className="mr-1" checked={platforms.includes('instagram')} onChange={()=>togglePlatform('instagram')} /> Instagram
          </label>
          <label className={`px-3 py-1 rounded-md border ${platforms.includes('facebook')?'bg-purple-600 text-white border-purple-600':'bg-white text-gray-800'}`}>
            <input type="checkbox" className="mr-1" checked={platforms.includes('facebook')} onChange={()=>togglePlatform('facebook')} /> Facebook
          </label>
          <label className={`px-3 py-1 rounded-md border ${platforms.includes('linkedin')?'bg-purple-600 text-white border-purple-600':'bg-white text-gray-800'}`}>
            <input type="checkbox" className="mr-1" checked={platforms.includes('linkedin')} onChange={()=>togglePlatform('linkedin')} /> LinkedIn
          </label>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <input type="date" value={date} onChange={e=>setDate(e.target.value)} className="border rounded-md px-3 py-2 text-sm" />
          <input type="time" value={time} onChange={e=>setTime(e.target.value)} className="border rounded-md px-3 py-2 text-sm" />
          <button onClick={()=>onPostNow?.({ caption, imageUrl: imageUrl || undefined, platforms })} className="px-3 py-2 rounded-md text-sm font-medium bg-purple-600 text-white hover:bg-purple-700">Post Now</button>
          <button disabled={!scheduledAt} onClick={()=>scheduledAt && onSchedule?.({ caption, imageUrl: imageUrl || undefined, platforms, scheduledAt })} className="px-3 py-2 rounded-md text-sm font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 disabled:opacity-50">Schedule</button>
        </div>
      </div>
    </div>
  );
};

export default PostScheduler;
