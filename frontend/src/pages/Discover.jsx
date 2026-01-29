import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Search, TrendingUp, Star, Users, Filter, X } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Demo creators
const demoCreators = [
  {
    id: '1',
    username: 'neon_dreams',
    display_name: 'Neon Dreams',
    avatar_url: 'https://images.unsplash.com/photo-1618698937393-8d7bb5f2d341?w=200',
    subscriber_count: 15234,
    media_count: 423,
    is_verified: true
  },
  {
    id: '2',
    username: 'cyber_queen',
    display_name: 'Cyber Queen',
    avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
    subscriber_count: 8921,
    media_count: 156,
    is_verified: true
  },
  {
    id: '3',
    username: 'midnight_star',
    display_name: 'Midnight Star',
    avatar_url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200',
    subscriber_count: 22456,
    media_count: 789,
    is_verified: false
  },
  {
    id: '4',
    username: 'velvet_rose',
    display_name: 'Velvet Rose',
    avatar_url: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200',
    subscriber_count: 5678,
    media_count: 234,
    is_verified: true
  }
];

const trendingTags = ['#trending', '#newcreator', '#exclusive', '#viral', '#hot'];

const CreatorCard = ({ creator, onClick }) => {
  const formatCount = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className="bg-[#121212] border border-[#222] rounded-xl p-4 cursor-pointer card-hover"
      onClick={onClick}
      data-testid={`creator-card-${creator.id}`}
    >
      <div className="flex items-center gap-3">
        <Avatar className="w-14 h-14 border-2 border-[#E91E63]">
          <AvatarImage src={creator.avatar_url} />
          <AvatarFallback className="bg-[#E91E63]">
            {creator.display_name?.charAt(0)}
          </AvatarFallback>
        </Avatar>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-white truncate">{creator.display_name}</h3>
            {creator.is_verified && (
              <Badge className="bg-[#00F0FF] text-black text-xs px-1.5">
                <Star className="w-3 h-3" />
              </Badge>
            )}
          </div>
          <p className="text-gray-400 text-sm">@{creator.username}</p>
        </div>
      </div>

      <div className="flex justify-between mt-4 pt-3 border-t border-[#222]">
        <div className="text-center">
          <div className="text-white font-medium">{formatCount(creator.subscriber_count)}</div>
          <div className="text-gray-500 text-xs">Subscribers</div>
        </div>
        <div className="text-center">
          <div className="text-white font-medium">{formatCount(creator.media_count)}</div>
          <div className="text-gray-500 text-xs">Media</div>
        </div>
      </div>
    </motion.div>
  );
};

export default function Discover() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [creators, setCreators] = useState(demoCreators);
  const [loading, setLoading] = useState(false);
  const [activeFilter, setActiveFilter] = useState('all');

  useEffect(() => {
    fetchCreators();
  }, []);

  const fetchCreators = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/creators?limit=20`);
      if (response.data.creators?.length > 0) {
        setCreators(response.data.creators);
      }
    } catch (error) {
      console.error('Error fetching creators:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCreators = creators.filter(creator => {
    if (!search) return true;
    return (
      creator.username.toLowerCase().includes(search.toLowerCase()) ||
      creator.display_name.toLowerCase().includes(search.toLowerCase())
    );
  });

  return (
    <div className="min-h-screen bg-[#050505] pb-24" data-testid="discover-page">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-[#050505]/90 backdrop-blur-lg border-b border-[#222] px-4 py-4">
        <h1 className="text-2xl font-bold text-white mb-4">Discover</h1>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <Input
            placeholder="Search creators..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 bg-[#1a1a1a] border-[#333] focus:border-[#E91E63] text-white h-12"
            data-testid="search-input"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      <div className="px-4 py-4">
        {/* Trending tags */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-5 h-5 text-[#E91E63]" />
            <h2 className="text-lg font-semibold text-white">Trending</h2>
          </div>
          <div className="flex gap-2 overflow-x-auto hide-scrollbar pb-2">
            {trendingTags.map(tag => (
              <Badge
                key={tag}
                className="bg-[#1a1a1a] text-[#E91E63] hover:bg-[#E91E63] hover:text-white cursor-pointer transition-colors duration-200 whitespace-nowrap"
                data-testid={`tag-${tag}`}
              >
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto hide-scrollbar pb-2">
          {['all', 'verified', 'new', 'popular'].map(filter => (
            <Button
              key={filter}
              variant={activeFilter === filter ? 'default' : 'outline'}
              className={`rounded-full capitalize whitespace-nowrap ${
                activeFilter === filter 
                  ? 'bg-[#E91E63] hover:bg-[#C2185B] text-white' 
                  : 'border-[#333] text-gray-300 hover:bg-white/10'
              }`}
              onClick={() => setActiveFilter(filter)}
              data-testid={`filter-${filter}`}
            >
              {filter === 'verified' && <Star className="w-4 h-4 mr-1" />}
              {filter === 'popular' && <Users className="w-4 h-4 mr-1" />}
              {filter}
            </Button>
          ))}
        </div>

        {/* Creators grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCreators.map((creator, index) => (
            <motion.div
              key={creator.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <CreatorCard
                creator={creator}
                onClick={() => navigate(`/profile/${creator.username}`)}
              />
            </motion.div>
          ))}
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#E91E63]" />
          </div>
        )}

        {/* Empty state */}
        {!loading && filteredCreators.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 mx-auto text-gray-600 mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No creators found</h3>
            <p className="text-gray-400">Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </div>
  );
}
