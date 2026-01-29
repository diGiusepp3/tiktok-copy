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

  return (
    <div className="video-container">
      {/* Thumbnail Image (placeholder for video) */}
      <div 
        className="video-thumbnail"
        style={{ backgroundImage: `url(${video.thumbnailUrl})` }}
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
            <img src={video.userAvatar} alt={video.username} className="profile-avatar" />
            {!video.isFollowing && (
              <button className="follow-button" onClick={() => onFollow(video.id)}>
                +
              </button>
            )}
          </div>
        </div>

        {/* Like Button */}
        <div className="sidebar-item" onClick={() => onLike(video.id)}>
          <div className={`action-button ${video.isLiked ? 'liked' : ''}`}>
            <Heart 
              className="action-icon" 
              fill={video.isLiked ? '#FE2C55' : 'none'}
              stroke={video.isLiked ? '#FE2C55' : 'white'}
            />
          </div>
          <span className="action-count">{formatCount(video.likes)}</span>
        </div>

        {/* Comment Button */}
        <div className="sidebar-item">
          <div className="action-button">
            <MessageCircle className="action-icon" />
          </div>
          <span className="action-count">{formatCount(video.comments)}</span>
        </div>

        {/* Share Button */}
        <div className="sidebar-item">
          <div className="action-button">
            <Share2 className="action-icon" />
          </div>
          <span className="action-count">{formatCount(video.shares)}</span>
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
          <span className="username">@{video.username}</span>
          {video.verified && (
            <CheckCircle className="verified-badge" size={16} fill="#20D5EC" stroke="white" />
          )}
        </div>
        <p className="caption">{video.caption}</p>
        <div className="music-info">
          <Music size={14} className="music-note" />
          <span className="music-text">original sound - {video.username}</span>
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