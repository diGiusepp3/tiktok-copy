import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { ArrowLeft, Grid3X3, Play, Heart, Lock, Settings, Share2, MoreHorizontal } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Demo creator data
const demoCreator = {
  id: '1',
  username: 'neon_dreams',
  display_name: 'Neon Dreams',
  avatar_url: 'https://images.unsplash.com/photo-1618698937393-8d7bb5f2d341?w=200',
  cover_url: 'https://images.unsplash.com/photo-1653256170871-d0a26c41f49c?w=800',
  bio: '✨ Creating magic in the digital realm | 🎨 Artist & Content Creator | 💫 DMs open for collabs',
  subscriber_count: 15234,
  post_count: 156,
  media_count: 423
};

const demoMedia = [
  { id: '1', file_type: 'image', thumbnail_url: 'https://images.unsplash.com/photo-1653256170871-d0a26c41f49c?w=300', likes: 1234, is_locked: false },
  { id: '2', file_type: 'video', thumbnail_url: 'https://images.unsplash.com/photo-1756664722134-0fd018cc2259?w=300', likes: 892, is_locked: true },
  { id: '3', file_type: 'image', thumbnail_url: 'https://images.unsplash.com/photo-1696694138288-d3c14bdd35f1?w=300', likes: 2341, is_locked: false },
  { id: '4', file_type: 'image', thumbnail_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300', likes: 567, is_locked: true },
  { id: '5', file_type: 'video', thumbnail_url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300', likes: 3421, is_locked: false },
  { id: '6', file_type: 'image', thumbnail_url: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300', likes: 789, is_locked: false },
];

const MediaGrid = ({ items, onItemClick }) => {
  return (
    <div className="profile-grid p-1">
      {items.map((item, index) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.05 }}
          className="relative aspect-square cursor-pointer group overflow-hidden bg-[#1a1a1a]"
          onClick={() => onItemClick(item)}
          data-testid={`media-item-${item.id}`}
        >
          <img
            src={item.thumbnail_url}
            alt=""
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
          
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center gap-4">
            <div className="flex items-center gap-1 text-white">
              <Heart className="w-5 h-5 fill-white" />
              <span className="font-medium">{item.likes}</span>
            </div>
          </div>

          {/* Video indicator */}
          {item.file_type === 'video' && (
            <div className="absolute top-2 right-2">
              <Play className="w-5 h-5 text-white fill-white drop-shadow-lg" />
            </div>
          )}

          {/* Locked indicator */}
          {item.is_locked && (
            <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
              <Lock className="w-8 h-8 text-white" />
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
};

export default function Profile() {
  const { username } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [creator, setCreator] = useState(demoCreator);
  const [media, setMedia] = useState(demoMedia);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('posts');

  const isOwnProfile = user?.username === username;

  useEffect(() => {
    if (username) {
      fetchCreatorProfile();
      fetchCreatorMedia();
    }
  }, [username]);

  const fetchCreatorProfile = async () => {
    try {
      const response = await axios.get(`${API}/creators/${username}`);
      setCreator(response.data);
    } catch (error) {
      console.error('Error fetching creator:', error);
    }
  };

  const fetchCreatorMedia = async () => {
    try {
      const response = await axios.get(`${API}/creators/${creator.id}/media?category=${activeTab}`);
      if (response.data.items?.length > 0) {
        setMedia(response.data.items);
      }
    } catch (error) {
      console.error('Error fetching media:', error);
    }
  };

  const handleSubscribe = async () => {
    if (!user) {
      toast.error('Please login to subscribe');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/creators/${creator.id}/subscribe`);
      setIsSubscribed(true);
      toast.success('Subscribed!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to subscribe');
    } finally {
      setLoading(false);
    }
  };

  const formatCount = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  return (
    <div className="min-h-screen bg-[#050505] pb-20" data-testid="profile-page">
      {/* Cover Image */}
      <div className="relative h-48 md:h-64">
        <img
          src={creator.cover_url}
          alt=""
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#050505]" />
        
        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="absolute top-4 left-4 btn-icon"
          data-testid="back-button"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>

        {/* More options */}
        <button
          className="absolute top-4 right-4 btn-icon"
          data-testid="more-options"
        >
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      {/* Profile Info */}
      <div className="px-4 -mt-16 relative z-10">
        <div className="flex items-end gap-4 mb-4">
          <Avatar className="w-24 h-24 border-4 border-[#050505] shadow-xl">
            <AvatarImage src={creator.avatar_url} />
            <AvatarFallback className="bg-[#E91E63] text-2xl">
              {creator.display_name?.charAt(0)}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 flex justify-end gap-2 mb-2">
            {isOwnProfile ? (
              <>
                <Button
                  variant="outline"
                  className="border-[#333] text-white hover:bg-white/10"
                  onClick={() => navigate('/settings')}
                  data-testid="edit-profile-button"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  className="border-[#333] text-white hover:bg-white/10"
                  data-testid="share-profile-button"
                >
                  <Share2 className="w-4 h-4" />
                </Button>
              </>
            ) : (
              <>
                <Button
                  className={`${isSubscribed ? 'bg-[#333] hover:bg-[#444]' : 'bg-[#E91E63] hover:bg-[#C2185B]'} text-white font-semibold px-6`}
                  onClick={handleSubscribe}
                  disabled={loading || isSubscribed}
                  data-testid="subscribe-button"
                >
                  {isSubscribed ? 'Subscribed' : 'Subscribe'}
                </Button>
                <Button
                  variant="outline"
                  className="border-[#333] text-white hover:bg-white/10"
                  data-testid="message-button"
                >
                  Message
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Name and username */}
        <h1 className="text-2xl font-bold text-white mb-1">{creator.display_name}</h1>
        <p className="text-gray-400 mb-3">@{creator.username}</p>

        {/* Bio */}
        {creator.bio && (
          <p className="text-gray-300 mb-4 whitespace-pre-line">{creator.bio}</p>
        )}

        {/* Stats */}
        <div className="flex gap-6 mb-6">
          <div className="text-center">
            <div className="text-xl font-bold text-white">{formatCount(creator.post_count)}</div>
            <div className="text-sm text-gray-400">Posts</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{formatCount(creator.media_count)}</div>
            <div className="text-sm text-gray-400">Media</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-white">{formatCount(creator.subscriber_count)}</div>
            <div className="text-sm text-gray-400">Subscribers</div>
          </div>
        </div>
      </div>

      {/* Content Tabs */}
      <Tabs defaultValue="posts" className="w-full" onValueChange={setActiveTab}>
        <TabsList className="w-full justify-start bg-transparent border-b border-[#222] rounded-none px-4">
          <TabsTrigger
            value="posts"
            className="data-[state=active]:text-[#E91E63] data-[state=active]:border-b-2 data-[state=active]:border-[#E91E63] rounded-none"
            data-testid="posts-tab"
          >
            <Grid3X3 className="w-4 h-4 mr-2" />
            Posts
          </TabsTrigger>
          <TabsTrigger
            value="stories"
            className="data-[state=active]:text-[#E91E63] data-[state=active]:border-b-2 data-[state=active]:border-[#E91E63] rounded-none"
            data-testid="stories-tab"
          >
            Stories
          </TabsTrigger>
          <TabsTrigger
            value="messages"
            className="data-[state=active]:text-[#E91E63] data-[state=active]:border-b-2 data-[state=active]:border-[#E91E63] rounded-none"
            data-testid="messages-tab"
          >
            Messages
          </TabsTrigger>
        </TabsList>

        <TabsContent value="posts" className="mt-0">
          <MediaGrid items={media} onItemClick={(item) => console.log('Open media:', item)} />
        </TabsContent>

        <TabsContent value="stories" className="mt-0">
          <MediaGrid items={media.slice(0, 3)} onItemClick={(item) => console.log('Open story:', item)} />
        </TabsContent>

        <TabsContent value="messages" className="mt-0">
          <div className="p-8 text-center text-gray-400">
            <Lock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Subscribe to see private messages</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
