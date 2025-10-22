import { useChatStore } from '../../store/chatStore';

export default function ContextPanel() {
  const { retrievalItems } = useChatStore();
  if (!retrievalItems.length) return (
    <div className="p-3 text-sm text-gray-500">No context loaded yet</div>
  );
  return (
    <div className="p-3">
      <div className="text-xs uppercase text-gray-500 mb-2">Using context from</div>
      <div className="flex flex-col gap-2">
        {retrievalItems.map((it, idx) => (
          <div key={idx} className="border rounded-lg p-2 bg-white">
            <div className="text-xs text-gray-700">{it.source}</div>
            <div className="text-sm text-gray-900 line-clamp-3">{it.snippet}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

