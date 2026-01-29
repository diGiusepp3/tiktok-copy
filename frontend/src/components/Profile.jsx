import React, { useState } from 'react';
import { ArrowLeft, Share2, MoreHorizontal, CheckCircle, Lock } from 'lucide-react';
import { mockUser, mockVideos } from '../mockData';
import './Profile.css';

const Profile = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState('videos');
  const userVideos = mockVideos.slice(0, 3);

  const formatCount = (count) => {
    if (count >= 1000000) {
      return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
      return (count / 1000).toFixed(1) + 'K';
    }
    return count.toString();
  };

  return (
    <div className="profile-page">
      {/* Header */}
      <div className="profile-header">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft size={24} />
        </button>
        <div className="header-title">
          <span className="header-username">{mockUser.username}</span>
        </div>
        <div className="header-actions">
          <button className="header-action-btn">
            <Share2 size={24} />
          </button>
          <button className="header-action-btn">
            <MoreHorizontal size={24} />
          </button>
        </div>
      </div>

      {/* Profile Info */}
      <div className="profile-info">
        <img src={mockUser.avatar} alt={mockUser.username} className="profile-avatar-large" />
        <div className="profile-username-container">
          <h2 className="profile-username">@{mockUser.username}</h2>
          {mockUser.verified && (
            <CheckCircle className="verified-badge-large" size={20} fill="#20D5EC" stroke="white" />
          )}
        </div>
        
        {/* Stats */}
        <div className="profile-stats">
          <div className="stat-item">
            <span className="stat-number">{formatCount(mockUser.following)}</span>
            <span className="stat-label">Following</span>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <span className="stat-number">{formatCount(mockUser.followers)}</span>
            <span className="stat-label">Followers</span>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <span className="stat-number">{formatCount(mockUser.likes)}</span>
            <span className="stat-label">Likes</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="profile-actions">
          <button className="edit-profile-btn">Edit profile</button>
          <button className="share-profile-btn">
            <Share2 size={20} />
          </button>
        </div>

        {/* Bio */}
        <div className="profile-bio">
          {mockUser.bio.split('\n').map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="profile-tabs">
        <button 
          className={`tab-button ${activeTab === 'videos' ? 'active' : ''}`}
          onClick={() => setActiveTab('videos')}
        >
          Videos
        </button>
        <button 
          className={`tab-button ${activeTab === 'liked' ? 'active' : ''}`}
          onClick={() => setActiveTab('liked')}
        >
          <Lock size={14} className="lock-icon" />
          Liked
        </button>
      </div>

      {/* Video Grid */}
      <div className="video-grid">
        {activeTab === 'videos' ? (
          userVideos.map((video) => (
            <div 
              key={video.id} 
              className="grid-video-item"
              style={{ backgroundImage: `url(${video.thumbnailUrl})`, backgroundSize: 'cover', backgroundPosition: 'center' }}
            >
              <div className="grid-video-overlay">
                <span className="video-views">👁️ {formatCount(video.likes * 10)}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <Lock size={48} className="empty-icon" />
            <p className="empty-text">This content is private</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;