import React from 'react';

export default function ToolChips() {
  // Placeholder for future tool suggestions
  return (
    <div className="flex gap-2 flex-wrap">
      {['Brochure', 'CMA', 'Social Post', 'Email Draft'].map((t) => (
        <span key={t} className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full">{t}</span>
      ))}
    </div>
  );
}

