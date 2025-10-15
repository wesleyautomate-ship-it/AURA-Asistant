// Routes configuration
// This file contains the routing setup for the application
// BrowserRouter is wrapped at the main.tsx level, so we only use Routes here

import { Routes, Route } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import Tasks from '../pages/Tasks';
import Chat from '../pages/Chat';
import ChatConsole from '../pages/ChatConsole';
import Analytics from '../pages/Analytics';
import Requests from '../pages/Requests';
import CMAReport from '../pages/CMAReport';
import DeckBuilder from '../pages/DeckBuilder';
import ContentViewer from '../pages/ContentViewer';
import Marketing from '../pages/Marketing';
import Contacts from '../pages/Contacts';
import Properties from '../pages/Properties';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/tasks" element={<Tasks />} />
      <Route path="/chat" element={<Chat />} />
      {import.meta.env.VITE_CHAT_CONSOLE_ENABLED !== 'false' && (
        <Route path="/chat/console" element={<ChatConsole />} />
      )}
      <Route path="/analytics" element={<Analytics />} />
      <Route path="/requests" element={<Requests />} />
      <Route path="/marketing" element={<Marketing />} />
      <Route path="/contacts" element={<Contacts />} />
      <Route path="/properties" element={<Properties />} />
      <Route path="/cma/:id" element={<CMAReport />} />
      <Route path="/deck/:id" element={<DeckBuilder />} />
      <Route path="/content/:contentId" element={<ContentViewer />} />
      {/* Additional routes will be added in future versions:
          /properties (v2.9), /contacts (v2.9), /settings (v2.8) */}
    </Routes>
  );
}
