import { NavLink, useLocation } from 'react-router-dom';
import { Home, ClipboardList, MessageCircle, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { to: '/', icon: Home, label: 'Home' },
  { to: '/tasks', icon: ClipboardList, label: 'Tasks' },
  { to: '/chat', icon: MessageCircle, label: 'Chat' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
];

export default function BottomNav() {
  const { pathname } = useLocation();
  
  return (
    <motion.nav
      initial={{ y: 80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="fixed bottom-0 left-0 w-full bg-white/95 backdrop-blur-md shadow-lg rounded-t-2xl px-6 py-2 z-50 flex justify-around items-center border-t border-gray-200 lg:hidden"
      role="navigation"
      aria-label="Main Navigation"
    >
      {navItems.map(({ to, icon: Icon, label }) => {
        const active = pathname === to;
        return (
          <NavLink 
            key={to} 
            to={to} 
            className="flex flex-col items-center text-xs py-2 px-3 rounded-lg transition-colors hover:bg-gray-50"
            aria-current={active ? 'page' : undefined}
          >
            <Icon 
              className={`w-5 h-5 mb-0.5 transition-colors ${
                active ? 'text-blue-600' : 'text-gray-500'
              }`} 
            />
            <span 
              className={`transition-colors ${
                active ? 'text-blue-600 font-medium' : 'text-gray-500'
              }`}
            >
              {label}
            </span>
          </NavLink>
        );
      })}
    </motion.nav>
  );
}
