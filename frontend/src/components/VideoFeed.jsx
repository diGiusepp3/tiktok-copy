import React, { useRef, useEffect, useState, useCallback } from 'react';
import VideoPlayer from './VideoPlayer';
import { mockVideos } from '../mockData';
import './VideoFeed.css';

const VideoFeed = () => {
  const containerRef = useRef(null);
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [videos, setVideos] = useState(mockVideos);
  const touchStartY = useRef(0);

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return;

    const scrollTop = containerRef.current.scrollTop;
    const videoHeight = window.innerHeight;
    const index = Math.round(scrollTop / videoHeight);
    
    if (index !== currentVideoIndex && index >= 0 && index < videos.length) {
      setCurrentVideoIndex(index);
    }
  }, [currentVideoIndex, videos.length]);

  const handleTouchStart = (e) => {
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e) => {
    const touchEndY = e.changedTouches[0].clientY;
    const deltaY = touchStartY.current - touchEndY;

    if (Math.abs(deltaY) > 50) {
      if (deltaY > 0 && currentVideoIndex < videos.length - 1) {
        // Swipe up
        scrollToVideo(currentVideoIndex + 1);
      } else if (deltaY < 0 && currentVideoIndex > 0) {
        // Swipe down
        scrollToVideo(currentVideoIndex - 1);
      }
    }
  };

  const scrollToVideo = (index) => {
    if (!containerRef.current) return;
    const videoHeight = window.innerHeight;
    containerRef.current.scrollTo({
      top: index * videoHeight,
      behavior: 'smooth'
    });
  };

  const handleLike = (videoId) => {
    setVideos(prevVideos => 
      prevVideos.map(video => {
        if (video.id === videoId) {
          return {
            ...video,
            isLiked: !video.isLiked,
            likes: video.isLiked ? video.likes - 1 : video.likes + 1
          };
        }
        return video;
      })
    );
  };

  const handleFollow = (videoId) => {
    setVideos(prevVideos => 
      prevVideos.map(video => {
        if (video.id === videoId) {
          return {
            ...video,
            isFollowing: !video.isFollowing
          };
        }
        return video;
      })
    );
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  return (
    <div 
      className="video-feed"
      ref={containerRef}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      {videos.map((video, index) => (
        <VideoPlayer
          key={video.id}
          video={video}
          isActive={index === currentVideoIndex}
          onLike={handleLike}
          onFollow={handleFollow}
        />
      ))}
    </div>
  );
};

export default VideoFeed;