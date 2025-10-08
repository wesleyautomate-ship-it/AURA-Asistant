import { MessageCircle, Mic, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Chat() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="min-h-screen bg-gradient-to-b from-gray-50 to-white px-4 py-6 pb-24 lg:pb-6"
    >
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-purple-100 rounded-xl">
            <MessageCircle className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Chat</h1>
            <p className="text-sm text-gray-500">Voice + text conversation with Aura</p>
          </div>
        </div>

        {/* Coming Soon Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Mic className="w-8 h-8 text-purple-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">AI Command Center & Chat</h2>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Voice and text interface with streaming AI responses, quick actions for CMA, market updates, and conversation history.
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-lg text-sm font-medium">
            <AlertCircle className="w-4 h-4" />
            Scheduled for v2.6
          </div>
        </div>

        {/* Preview Features */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { title: 'Voice Input', desc: 'Natural language commands' },
            { title: 'Streaming Responses', desc: 'Real-time AI output' },
            { title: 'Quick Actions', desc: 'CMA, listings, market data' },
          ].map((feature, idx) => (
            <div key={idx} className="bg-white rounded-xl border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
              <p className="text-sm text-gray-500">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
