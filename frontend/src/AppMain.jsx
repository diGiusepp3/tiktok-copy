import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import VideoFeed from './components/VideoFeed';
import BottomNav from './components/BottomNav';
import Discover from './components/Discover';
import Profile from './components/Profile';
import AdminChatGPT from './components/AdminChatGPT';
import AuthScreen from './components/AuthScreen';
import Upload from './components/Upload';
import { Toaster } from 'sonner';
import './App.css';

const AppContent = () => {
  const { user, loading, logout } = useAuth();
  const [currentTab, setCurrentTab] = useState('home');

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  const renderContent = () => {
    switch (currentTab) {
      case 'home':
        return <VideoFeed />;
      case 'discover':
        return <Discover />;
      case 'upload':
        return <Upload />;
      case 'profile':
        return <Profile user={user} onLogout={logout} />;
      case 'admin':
        // Only show to admins
        if (user.is_admin) {
          return <AdminChatGPT />;
        }
        return <VideoFeed />;
      default:
        return <VideoFeed />;
    }
  };

  return (
    <div className="app-container">
      <div className="main-content">
        {renderContent()}
      </div>
      <BottomNav 
        currentTab={currentTab} 
        onTabChange={setCurrentTab}
        isAdmin={user?.is_admin}
      />
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Toaster 
        position="top-center" 
        toastOptions={{
          style: {
            background: '#18181b',
            border: '1px solid #27272a',
            color: '#fff',
          }
        }}
      />
      <AppContent />
    </AuthProvider>
  );
}

export default App;
