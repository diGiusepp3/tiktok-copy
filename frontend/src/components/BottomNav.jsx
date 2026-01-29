import React from 'react';
import { Home, Users, PlusSquare, MessageSquare, User } from 'lucide-react';
import './BottomNav.css';

const BottomNav = ({ activeTab, setActiveTab }) => {
  return (
    <div className="bottom-nav">
      <button 
        className={`nav-item ${activeTab === 'foryou' ? 'active' : ''}`}
        onClick={() => setActiveTab('foryou')}
      >
        <Home size={28} strokeWidth={activeTab === 'foryou' ? 2.5 : 2} />
        <span className="nav-label">Home</span>
      </button>

      <button 
        className={`nav-item ${activeTab === 'following' ? 'active' : ''}`}
        onClick={() => setActiveTab('following')}
      >
        <Users size={28} strokeWidth={activeTab === 'following' ? 2.5 : 2} />
        <span className="nav-label">Friends</span>
      </button>

      <button 
        className="nav-item create-button"
        onClick={() => alert('Create video feature - Available in full version')}
      >
        <div className="create-icon">
          <PlusSquare size={24} />
        </div>
      </button>

      <button 
        className={`nav-item ${activeTab === 'inbox' ? 'active' : ''}`}
        onClick={() => setActiveTab('inbox')}
      >
        <MessageSquare size={28} strokeWidth={activeTab === 'inbox' ? 2.5 : 2} />
        <span className="nav-label">Inbox</span>
      </button>

      <button 
        className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
        onClick={() => setActiveTab('profile')}
      >
        <User size={28} strokeWidth={activeTab === 'profile' ? 2.5 : 2} />
        <span className="nav-label">Profile</span>
      </button>
    </div>
  );
};

export default BottomNav;