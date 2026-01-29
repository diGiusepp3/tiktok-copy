import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Toaster } from "./components/ui/sonner";
import { BottomNav, SideNav } from "./components/Navigation";

// Pages
import VideoFeed from "./pages/VideoFeed";
import Discover from "./pages/Discover";
import Profile from "./pages/Profile";
import Scraper from "./pages/Scraper";
import FileManager from "./pages/FileManager";
import Terminal from "./pages/Terminal";
import ChatAssistant from "./pages/ChatAssistant";
import Auth from "./pages/Auth";

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#E91E63]" />
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/auth" replace />;
  }
  
  return children;
};

// Auth redirect
const AuthRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#E91E63]" />
      </div>
    );
  }
  
  if (user) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

function AppContent() {
  return (
    <div className="App">
      <SideNav />
      <main className="lg:ml-60 min-h-screen">
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<VideoFeed />} />
          <Route path="/discover" element={<Discover />} />
          <Route path="/profile/:username" element={<Profile />} />
          <Route path="/chat" element={<ChatAssistant />} />
          
          {/* Auth route */}
          <Route 
            path="/auth" 
            element={
              <AuthRoute>
                <Auth />
              </AuthRoute>
            } 
          />
          
          {/* Protected routes */}
          <Route 
            path="/scraper" 
            element={
              <ProtectedRoute>
                <Scraper />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/files" 
            element={
              <ProtectedRoute>
                <FileManager />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/terminal" 
            element={
              <ProtectedRoute>
                <Terminal />
              </ProtectedRoute>
            } 
          />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <BottomNav />
      <Toaster 
        position="top-center"
        toastOptions={{
          style: {
            background: '#1a1a1a',
            color: '#fff',
            border: '1px solid #333'
          }
        }}
      />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
