import { AnimatePresence } from "framer-motion"
import AppRoutes from "./routes"
import BottomNav from "./components/layout/BottomNav"
import GlobalHeader from "./components/layout/GlobalHeader"
import CommandFab from "./components/ui/CommandFab"
import CommandCenter from "./components/ui/CommandCenter"
import { useCommandStore } from "./store/commandStore"
import { useAuth } from "./store/authStore"
import { AuthDebugPanel } from "./components/auth"

export default function App() {
  const { isOpen } = useCommandStore()
  const { isAuthenticated } = useAuth()
  const containerClass = isAuthenticated
    ? "min-h-screen bg-gradient-to-b from-gray-50 to-white"
    : "min-h-screen bg-slate-950"

  return (
    <div className={containerClass}>
      {isAuthenticated && <GlobalHeader />}

      <main className={isAuthenticated ? "relative" : "min-h-screen"}>
        <AppRoutes />
      </main>

      {isAuthenticated && (
        <>
          <CommandFab />
          <AnimatePresence>{isOpen && <CommandCenter />}</AnimatePresence>
          <BottomNav />
        </>
      )}

      {import.meta.env.DEV && <AuthDebugPanel />}
    </div>
  )
}
