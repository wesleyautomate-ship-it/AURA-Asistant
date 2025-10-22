import { useChatStore } from '../../store/chatStore';

export default function ThreadList() {
  const { threads, currentThreadId, setCurrentThread, createThread } = useChatStore();

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b">
        <button
          onClick={createThread}
          className="w-full bg-purple-600 text-white rounded-lg py-2 text-sm font-medium"
        >
          New Thread
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {threads.map((t) => (
          <div
            key={t.id}
            className={`px-3 py-2 cursor-pointer ${currentThreadId === t.id ? 'bg-purple-50' : ''}`}
            onClick={() => setCurrentThread(t.id)}
          >
            <div className="text-sm font-medium text-gray-900 truncate">
              {t.title || 'Untitled session'}
            </div>
            <div className="text-xs text-gray-500">{t.id.slice(0, 8)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

