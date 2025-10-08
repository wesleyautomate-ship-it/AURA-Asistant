import { AnimatePresence } from "framer-motion";
import AppRoutes from "./routes";
import BottomNav from "./components/layout/BottomNav";
import GlobalHeader from "./components/layout/GlobalHeader";
import CommandFab from "./components/ui/CommandFab";
import CommandCenter from "./components/ui/CommandCenter";
import { useCommandStore } from "./store/commandStore";

export default function App() {
  const { isOpen } = useCommandStore();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Global Header - Desktop Only */}
      <GlobalHeader />
      
      {/* Main Content Area */}
      <main className="relative">
        <AppRoutes />
      </main>
      
      {/* Floating Command Button */}
      <CommandFab />
      
      {/* AI Command Center Panel */}
      <AnimatePresence>
        {isOpen && <CommandCenter />}
      </AnimatePresence>
      
      {/* Bottom Navigation - Mobile Only */}
      <BottomNav />
    </div>
  );
}
