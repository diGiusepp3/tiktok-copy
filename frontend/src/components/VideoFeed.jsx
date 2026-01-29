import React, { useRef, useEffect, useState, useCallback } from 'react';
import VideoPlayer from './VideoPlayer';
import { mockVideos } from '../mockData';
import './VideoFeed.css';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const VideoFeed = () => {
  const containerRef = useRef(null);
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const touchStartY = useRef(0);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = token ? {
        headers: { Authorization: `Bearer ${token}` }
      } : {};
      
      const res = await axios.get(`${API}/posts/feed`, config);
      
      if (res.data.length === 0) {
        // If no posts, use mock data for demo
        setVideos(mockVideos);
      } else {
        setVideos(res.data);
      }
    } catch (error) {
      console.error('Failed to fetch posts:', error);
      // Use mock data as fallback
      setVideos(mockVideos);
      toast.error('Using demo content');
    } finally {
      setLoading(false);
    }
  };

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

  const handleLike = async (videoId) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast.error('Please login to like posts');
        return;
      }

      await axios.post(`${API}/posts/${videoId}/like`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setVideos(prevVideos => 
        prevVideos.map(video => {
          if (video.id === videoId) {
            return {
              ...video,
              is_liked: !video.is_liked,
              likes_count: video.is_liked ? video.likes_count - 1 : video.likes_count + 1
            };
          }
          return video;
        })
      );
    } catch (error) {
      toast.error('Failed to like post');
    }
  };

  const handleFollow = async (videoId) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast.error('Please login to follow users');
        return;
      }

      const video = videos.find(v => v.id === videoId);
      if (!video) return;

      await axios.post(`${API}/users/${video.user_id}/follow`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setVideos(prevVideos => 
        prevVideos.map(v => {
          if (v.id === videoId) {
            return {
              ...v,
              is_following: !v.is_following
            };
          }
          return v;
        })
      );
    } catch (error) {
      toast.error('Failed to follow user');
    }
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  if (loading) {
    return (
      <div className="video-feed flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

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