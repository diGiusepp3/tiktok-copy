import { NavLink, useLocation } from 'react-router-dom';
import { Home, Compass, Download, FolderOpen, Terminal, MessageSquare, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { path: '/', icon: Home, label: 'Feed' },
  { path: '/discover', icon: Compass, label: 'Discover' },
  { path: '/scraper', icon: Download, label: 'Scraper' },
  { path: '/files', icon: FolderOpen, label: 'Files' },
  { path: '/terminal', icon: Terminal, label: 'CLI' },
];

export const BottomNav = () => {
  const location = useLocation();
  const { user } = useAuth();

  // Hide nav on auth page
  if (location.pathname === '/auth') return null;

  return (
    <nav className="bottom-nav" data-testid="bottom-nav">
      <div className="flex items-center justify-around max-w-lg mx-auto">
        {navItems.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => 
              `bottom-nav-item ${isActive ? 'active' : ''}`
            }
            data-testid={`nav-${label.toLowerCase()}`}
          >
            <Icon className="w-6 h-6" />
            <span className="text-xs mt-1">{label}</span>
          </NavLink>
        ))}
        
        <NavLink
          to={user ? `/profile/${user.username}` : '/auth'}
          className={({ isActive }) => 
            `bottom-nav-item ${isActive ? 'active' : ''}`
          }
          data-testid="nav-profile"
        >
          <User className="w-6 h-6" />
          <span className="text-xs mt-1">Profile</span>
        </NavLink>
      </div>
    </nav>
  );
};

export const SideNav = () => {
  const { user, logout } = useAuth();

  return (
    <aside className="hidden lg:flex fixed left-0 top-0 bottom-0 w-60 bg-[#0a0a0a] border-r border-[#222] flex-col z-50">
      {/* Logo */}
      <div className="p-6 border-b border-[#222]">
        <h1 className="text-2xl font-bold gradient-text">Clone</h1>
      </div>

      {/* Nav items */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => 
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-[#E91E63] text-white' 
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            <span className="font-medium">{label}</span>
          </NavLink>
        ))}
        
        <NavLink
          to="/chat"
          className={({ isActive }) => 
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive 
                ? 'bg-[#E91E63] text-white' 
                : 'text-gray-400 hover:bg-white/5 hover:text-white'
            }`
          }
        >
          <MessageSquare className="w-5 h-5" />
          <span className="font-medium">Assistant</span>
        </NavLink>
      </nav>

      {/* User section */}
      <div className="p-4 border-t border-[#222]">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#E91E63] flex items-center justify-center text-white font-bold">
              {user.display_name?.charAt(0) || user.username?.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">{user.display_name || user.username}</p>
              <button 
                onClick={logout}
                className="text-xs text-gray-400 hover:text-[#E91E63]"
              >
                Sign out
              </button>
            </div>
          </div>
        ) : (
          <NavLink
            to="/auth"
            className="flex items-center justify-center gap-2 px-4 py-3 bg-[#E91E63] hover:bg-[#C2185B] text-white rounded-lg font-medium transition-colors"
          >
            Sign In
          </NavLink>
        )}
      </div>
    </aside>
  );
};
