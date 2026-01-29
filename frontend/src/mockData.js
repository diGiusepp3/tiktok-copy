// Mock video data for TikTok clone
// Note: Using placeholder images until actual video upload is implemented
export const mockVideos = [
  {
    id: '1',
    videoUrl: '',
    thumbnailUrl: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=700&fit=crop',
    username: 'creative_artist',
    userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
    caption: 'Amazing sunset vibes 🌅 #nature #sunset #peaceful',
    likes: 125400,
    comments: 1203,
    shares: 567,
    isLiked: false,
    isFollowing: false,
    verified: true
  },
  {
    id: '2',
    videoUrl: '',
    thumbnailUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=700&fit=crop',
    username: 'dance_master',
    userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
    caption: 'New dance challenge! Can you do this? 💃 #dance #trending #viral',
    likes: 456700,
    comments: 3420,
    shares: 1234,
    isLiked: false,
    isFollowing: false,
    verified: false
  },
  {
    id: '3',
    videoUrl: '',
    thumbnailUrl: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400&h=700&fit=crop',
    username: 'foodie_heaven',
    userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
    caption: 'Delicious recipe you must try! 🍕 #food #cooking #recipe',
    likes: 234500,
    comments: 890,
    shares: 445,
    isLiked: false,
    isFollowing: false,
    verified: true
  },
  {
    id: '4',
    videoUrl: '',
    thumbnailUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=700&fit=crop',
    username: 'travel_vibes',
    userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
    caption: 'Paradise found! 🏝️ #travel #adventure #paradise',
    likes: 567800,
    comments: 2340,
    shares: 890,
    isLiked: false,
    isFollowing: false,
    verified: true
  },
  {
    id: '5',
    videoUrl: '',
    thumbnailUrl: 'https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=400&h=700&fit=crop',
    username: 'comedy_king',
    userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=5',
    caption: 'Wait for it... 😂 #funny #comedy #viral',
    likes: 890000,
    comments: 4567,
    shares: 2340,
    isLiked: false,
    isFollowing: false,
    verified: false
  },
  {
    id: '6',
    videoUrl: '',
    thumbnailUrl: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=400&h=700&fit=crop',
    username: 'car_enthusiast',
    userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=6',
    caption: 'Dream car goals 🚗 #cars #luxury #speed',
    likes: 345600,
    comments: 1567,
    shares: 678,
    isLiked: false,
    isFollowing: false,
    verified: true
  }
];

export const mockComments = [
  {
    id: 'c1',
    username: 'user_one',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=comment1',
    comment: 'This is amazing! 😍',
    likes: 234,
    timestamp: '2h ago'
  },
  {
    id: 'c2',
    username: 'cool_user',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=comment2',
    comment: 'Can you teach me how to do this?',
    likes: 89,
    timestamp: '5h ago'
  },
  {
    id: 'c3',
    username: 'awesome_person',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=comment3',
    comment: 'Best video ever! 🔥🔥🔥',
    likes: 456,
    timestamp: '1d ago'
  }
];

export const mockUser = {
  username: 'my_username',
  displayName: 'My Display Name',
  avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=currentuser',
  followers: 12400,
  following: 567,
  likes: 345600,
  bio: 'Living my best life 🌟\nContent creator 🎥\nDM for collabs',
  verified: true
};