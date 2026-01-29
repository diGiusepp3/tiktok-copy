import React from 'react';
import { Home, Compass, PlusSquare, User, Terminal } from 'lucide-react';
import './BottomNav.css';

const BottomNav = ({ currentTab, onTabChange, isAdmin }) => {
  return (
    <div className="bottom-nav">
      <button 
        className={`nav-item ${currentTab === 'home' ? 'active' : ''}`}
        onClick={() => onTabChange('home')}
      >
        <Home size={28} strokeWidth={currentTab === 'home' ? 2.5 : 2} />
        <span className="nav-label">Home</span>
      </button>

      <button 
        className={`nav-item ${currentTab === 'discover' ? 'active' : ''}`}
        onClick={() => onTabChange('discover')}
      >
        <Compass size={28} strokeWidth={currentTab === 'discover' ? 2.5 : 2} />
        <span className="nav-label">Discover</span>
      </button>

      <button 
        className="nav-item create-button"
        onClick={() => onTabChange('upload')}
      >
        <div className="create-icon">
          <PlusSquare size={24} />
        </div>
      </button>

      {isAdmin && (
        <button 
          className={`nav-item ${currentTab === 'admin' ? 'active' : ''}`}
          onClick={() => onTabChange('admin')}
        >
          <Terminal size={28} strokeWidth={currentTab === 'admin' ? 2.5 : 2} />
          <span className="nav-label">Admin</span>
        </button>
      )}

      <button 
        className={`nav-item ${currentTab === 'profile' ? 'active' : ''}`}
        onClick={() => onTabChange('profile')}
      >
        <User size={28} strokeWidth={currentTab === 'profile' ? 2.5 : 2} />
        <span className="nav-label">Profile</span>
      </button>
    </div>
  );
};

export default BottomNav;