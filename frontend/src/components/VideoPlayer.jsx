import React, { useRef, useEffect, useState } from 'react';
import { Heart, MessageCircle, Share2, MoreHorizontal, Music, CheckCircle, Play } from 'lucide-react';

const VideoPlayer = ({ video, isActive, onLike, onFollow }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const formatCount = (count) => {
    if (count >= 1000000) {
      return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
      return (count / 1000).toFixed(1) + 'K';
    }
    return count.toString();
  };

  // Handle both API data and mock data
  const username = video.username || video.user_id;
  const thumbnailUrl = video.thumbnail_url || video.thumbnailUrl;
  const userAvatar = video.user_avatar || video.userAvatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + username;
  const likes = video.likes_count || video.likes || 0;
  const comments = video.comments_count || video.comments || 0;
  const shares = video.shares_count || video.shares || 0;
  const isLiked = video.is_liked || video.isLiked || false;
  const isFollowing = video.is_following || video.isFollowing || false;
  const isVerified = video.is_verified || video.verified || false;
  const caption = video.caption || '';

  return (
    <div className="video-container">
      {/* Thumbnail Image (placeholder for video) */}
      <div 
        className="video-thumbnail"
        style={{ backgroundImage: `url(${thumbnailUrl})` }}
        onClick={togglePlayPause}
      >
        {!isPlaying && (
          <div className="play-overlay">
            <Play className="play-icon" size={64} fill="white" />
          </div>
        )}
      </div>

      {/* Top gradient overlay */}
      <div className="video-gradient-top" />
      
      {/* Bottom gradient overlay */}
      <div className="video-gradient-bottom" />

      {/* Right sidebar actions */}
      <div className="video-sidebar">
        {/* Profile Avatar */}
        <div className="sidebar-item">
          <div className="profile-avatar-container">
            <img src={userAvatar} alt={username} className="profile-avatar" />
            {!isFollowing && (
              <button className="follow-button" onClick={() => onFollow(video.id)}>
                +
              </button>
            )}
          </div>
        </div>

        {/* Like Button */}
        <div className="sidebar-item" onClick={() => onLike(video.id)}>
          <div className={`action-button ${isLiked ? 'liked' : ''}`}>
            <Heart 
              className="action-icon" 
              fill={isLiked ? '#FE2C55' : 'none'}
              stroke={isLiked ? '#FE2C55' : 'white'}
            />
          </div>
          <span className="action-count">{formatCount(likes)}</span>
        </div>

        {/* Comment Button */}
        <div className="sidebar-item">
          <div className="action-button">
            <MessageCircle className="action-icon" />
          </div>
          <span className="action-count">{formatCount(comments)}</span>
        </div>

        {/* Share Button */}
        <div className="sidebar-item">
          <div className="action-button">
            <Share2 className="action-icon" />
          </div>
          <span className="action-count">{formatCount(shares)}</span>
        </div>

        {/* Music Disc */}
        <div className="sidebar-item">
          <div className="music-disc">
            <Music className="music-icon" size={16} />
          </div>
        </div>
      </div>

      {/* Bottom info overlay */}
      <div className="video-info">
        <div className="username-container">
          <span className="username">@{username}</span>
          {isVerified && (
            <CheckCircle className="verified-badge" size={16} fill="#20D5EC" stroke="white" />
          )}
        </div>
        <p className="caption">{caption}</p>
        <div className="music-info">
          <Music size={14} className="music-note" />
          <span className="music-text">original sound - {username}</span>
        </div>
      </div>

      {/* Mute/Unmute indicator */}
      <button className="mute-button" onClick={toggleMute}>
        {isMuted ? '🔇' : '🔊'}
      </button>
    </div>
  );
};

export default VideoPlayer;