import { Bell, Search, User } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function GlobalHeader() {
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  
  return (
    <header className="hidden lg:flex items-center justify-between px-6 py-3 bg-white shadow-sm border-b border-gray-100 sticky top-0 z-40">
      {/* Left: Logo + Title */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">A</span>
        </div>
        <h1 className="text-lg font-semibold text-gray-800">Aura Assistant</h1>
      </div>
      
      {/* Center: Search Bar */}
      <div className="flex items-center gap-3 w-1/2 max-w-md bg-gray-50 rounded-lg px-4 py-2 border border-gray-200 hover:border-blue-300 transition-colors">
        <Search className="text-gray-400 w-5 h-5" />
        <input
          type="search"
          placeholder="Search (⌘ + K)"
          className="w-full outline-none text-sm text-gray-700 bg-transparent placeholder:text-gray-400"
          aria-label="Global search"
        />
      </div>
      
      {/* Right: Notifications + Avatar */}
      <div className="flex items-center gap-4 relative">
        <button 
          onClick={() => setNotificationsOpen(!notificationsOpen)}
          aria-label="Notifications"
          className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Bell className="text-gray-600 hover:text-blue-600 w-5 h-5 transition-colors" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" aria-hidden="true"></span>
        </button>
        
        <button 
          className="flex items-center gap-2 hover:bg-gray-100 rounded-lg p-1.5 pr-3 transition-colors"
          aria-label="User menu"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center border-2 border-white shadow-sm">
            <User className="text-white w-4 h-4" />
          </div>
          <span className="text-sm font-medium text-gray-700">Agent</span>
        </button>
        
        {/* Notifications Panel */}
        <AnimatePresence>
          {notificationsOpen && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/10 z-40"
                onClick={() => setNotificationsOpen(false)}
              />
              
              {/* Panel */}
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="absolute right-0 top-14 bg-white shadow-xl rounded-xl p-4 w-80 border border-gray-200 z-50"
              >
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm font-semibold text-gray-800">Notifications</p>
                  <button 
                    className="text-xs text-blue-600 hover:text-blue-700"
                    onClick={() => setNotificationsOpen(false)}
                  >
                    Mark all read
                  </button>
                </div>
                
                <ul className="space-y-2">
                  {[
                    { text: 'New AI report ready', time: '5m ago', unread: true },
                    { text: '3 properties updated', time: '1h ago', unread: true },
                    { text: 'Marketing post approved', time: '2h ago', unread: false },
                    { text: 'CMA analysis completed', time: '3h ago', unread: false },
                  ].map((notification, idx) => (
                    <li 
                      key={idx}
                      className={`p-3 rounded-lg border transition-colors hover:bg-gray-50 cursor-pointer ${
                        notification.unread ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <p className="text-sm text-gray-700">{notification.text}</p>
                        {notification.unread && (
                          <span className="w-2 h-2 bg-blue-500 rounded-full mt-1" aria-label="Unread"></span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{notification.time}</p>
                    </li>
                  ))}
                </ul>
                
                <button className="w-full mt-3 text-center text-sm text-blue-600 hover:text-blue-700 font-medium py-2">
                  View all notifications
                </button>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>
    </header>
  );
}
