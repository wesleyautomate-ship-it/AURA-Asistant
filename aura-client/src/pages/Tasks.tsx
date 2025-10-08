import { ClipboardList, Calendar, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Tasks() {
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
          <div className="p-3 bg-blue-100 rounded-xl">
            <ClipboardList className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
            <p className="text-sm text-gray-500">AI-generated reminders and follow-ups</p>
          </div>
        </div>

        {/* Coming Soon Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Calendar className="w-8 h-8 text-blue-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Tasks Module</h2>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            AI-powered task management with smart reminders, follow-ups, and workflow automation coming in v2.6.
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium">
            <AlertCircle className="w-4 h-4" />
            Scheduled for v2.6
          </div>
        </div>

        {/* Preview Features */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { title: 'Smart Reminders', desc: 'AI-generated follow-ups' },
            { title: 'Task Automation', desc: 'Workflow orchestration' },
            { title: 'Priority Queue', desc: 'Intelligent scheduling' },
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
