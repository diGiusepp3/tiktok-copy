import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { Heart, MessageCircle, Share2, Music2, User, Play, Pause, Volume2, VolumeX } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Placeholder content for demo
const demoContent = [
  {
    id: '1',
    creator_id: '1',
    username: 'neon_dreams',
    display_name: 'Neon Dreams',
    creator_avatar: 'https://images.unsplash.com/photo-1618698937393-8d7bb5f2d341?w=100',
    file_type: 'image',
    file_path: 'https://images.unsplash.com/photo-1653256170871-d0a26c41f49c?w=600',
    thumbnail_url: 'https://images.unsplash.com/photo-1653256170871-d0a26c41f49c?w=600',
    likes: 12453,
    views: 89234,
    caption: 'Late night vibes ✨'
  },
  {
    id: '2',
    creator_id: '2',
    username: 'cyber_queen',
    display_name: 'Cyber Queen',
    creator_avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100',
    file_type: 'image',
    file_path: 'https://images.unsplash.com/photo-1756664722134-0fd018cc2259?w=600',
    thumbnail_url: 'https://images.unsplash.com/photo-1756664722134-0fd018cc2259?w=600',
    likes: 8921,
    views: 45678,
    caption: 'In my element 🔥'
  },
  {
    id: '3',
    creator_id: '3',
    username: 'midnight_star',
    display_name: 'Midnight Star',
    creator_avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100',
    file_type: 'image',
    file_path: 'https://images.unsplash.com/photo-1696694138288-d3c14bdd35f1?w=600',
    thumbnail_url: 'https://images.unsplash.com/photo-1696694138288-d3c14bdd35f1?w=600',
    likes: 15678,
    views: 123456,
    caption: 'New drop coming soon 💫'
  }
];

const FeedItem = ({ item, isActive, onLike }) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(item.likes || 0);
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);

  useEffect(() => {
    if (videoRef.current) {
      if (isActive) {
        videoRef.current.play().catch(() => {});
        setIsPlaying(true);
      } else {
        videoRef.current.pause();
        setIsPlaying(false);
      }
    }
  }, [isActive]);

  const handleLike = async () => {
    if (!user) {
      toast.error('Please login to like');
      return;
    }
    
    setLiked(!liked);
    setLikeCount(prev => liked ? prev - 1 : prev + 1);
    
    try {
      await axios.post(`${API}/media/${item.id}/like`);
    } catch (error) {
      // Revert on error
      setLiked(liked);
      setLikeCount(item.likes || 0);
    }
  };

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatCount = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  return (
    <div className="feed-item relative bg-black" data-testid={`feed-item-${item.id}`}>
      {/* Media Content */}
      <div className="absolute inset-0 flex items-center justify-center">
        {item.file_type === 'video' ? (
          <video
            ref={videoRef}
            src={item.file_path}
            className="w-full h-full object-cover"
            loop
            muted={isMuted}
            playsInline
            onClick={togglePlay}
          />
        ) : (
          <img
            src={item.file_path || item.thumbnail_url}
            alt=""
            className="w-full h-full object-cover"
          />
        )}
      </div>

      {/* Overlay gradient */}
      <div className="video-overlay absolute inset-0 pointer-events-none" />

      {/* Video controls */}
      {item.file_type === 'video' && (
        <div className="absolute top-4 right-4 flex gap-2 z-20">
          <button
            onClick={togglePlay}
            className="btn-icon"
            data-testid="play-pause-button"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          <button
            onClick={toggleMute}
            className="btn-icon"
            data-testid="mute-button"
          >
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>
        </div>
      )}

      {/* Right side actions */}
      <div className="absolute right-4 bottom-32 flex flex-col items-center gap-6 z-20">
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={handleLike}
          className="flex flex-col items-center gap-1"
          data-testid="like-button"
        >
          <div className={`btn-icon ${liked ? 'bg-[#E91E63]' : ''}`}>
            <Heart className={`w-6 h-6 ${liked ? 'fill-white' : ''}`} />
          </div>
          <span className="text-xs text-white font-medium">{formatCount(likeCount)}</span>
        </motion.button>

        <button className="flex flex-col items-center gap-1" data-testid="comment-button">
          <div className="btn-icon">
            <MessageCircle className="w-6 h-6" />
          </div>
          <span className="text-xs text-white font-medium">Comment</span>
        </button>

        <button className="flex flex-col items-center gap-1" data-testid="share-button">
          <div className="btn-icon">
            <Share2 className="w-6 h-6" />
          </div>
          <span className="text-xs text-white font-medium">Share</span>
        </button>
      </div>

      {/* Bottom info */}
      <div className="absolute bottom-24 left-4 right-20 z-20">
        <div 
          className="flex items-center gap-3 mb-3 cursor-pointer"
          onClick={() => navigate(`/profile/${item.username}`)}
          data-testid="creator-info"
        >
          <Avatar className="w-12 h-12 border-2 border-[#E91E63]">
            <AvatarImage src={item.creator_avatar} />
            <AvatarFallback className="bg-[#E91E63]">
              <User className="w-6 h-6" />
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 className="text-white font-bold text-base">@{item.username}</h3>
            <p className="text-gray-300 text-sm">{item.display_name}</p>
          </div>
          <Button 
            size="sm" 
            className="ml-2 bg-[#E91E63] hover:bg-[#C2185B] rounded-full px-4"
            data-testid="follow-button"
          >
            Follow
          </Button>
        </div>

        {item.caption && (
          <p className="text-white text-sm mb-2 line-clamp-2">{item.caption}</p>
        )}

        {/* Music/Audio indicator */}
        <div className="flex items-center gap-2 text-white/80">
          <Music2 className="w-4 h-4" />
          <span className="text-xs">Original Sound - {item.display_name}</span>
        </div>
      </div>
    </div>
  );
};

export default function VideoFeed() {
  const [items, setItems] = useState(demoContent);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/feed?limit=20`);
      if (response.data.items?.length > 0) {
        setItems(response.data.items);
      }
    } catch (error) {
      console.error('Error fetching feed:', error);
      // Keep demo content on error
    } finally {
      setLoading(false);
    }
  };

  const handleScroll = useCallback((e) => {
    const container = e.target;
    const scrollTop = container.scrollTop;
    const itemHeight = container.clientHeight;
    const newIndex = Math.round(scrollTop / itemHeight);
    
    if (newIndex !== activeIndex && newIndex >= 0 && newIndex < items.length) {
      setActiveIndex(newIndex);
    }
  }, [activeIndex, items.length]);

  return (
    <div 
      ref={containerRef}
      className="feed-container hide-scrollbar"
      onScroll={handleScroll}
      data-testid="video-feed"
    >
      <AnimatePresence>
        {items.map((item, index) => (
          <FeedItem
            key={item.id}
            item={item}
            isActive={index === activeIndex}
          />
        ))}
      </AnimatePresence>

      {/* Loading indicator */}
      {loading && items.length === 0 && (
        <div className="feed-item flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#E91E63]" />
        </div>
      )}
    </div>
  );
}
