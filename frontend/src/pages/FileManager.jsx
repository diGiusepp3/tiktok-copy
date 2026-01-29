import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Folder, File, Image, Film, ChevronRight, ChevronLeft, Home,
  Search, Grid, List, Upload, Download, Trash2, Move, Copy,
  Check, X, RefreshCw, HardDrive, FolderPlus, MoreVertical
} from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { ScrollArea } from '../components/ui/scroll-area';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '../components/ui/dropdown-menu';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const FileIcon = ({ type, isDir }) => {
  if (isDir) return <Folder className="w-5 h-5 text-[#00F0FF]" />;
  if (type === 'image') return <Image className="w-5 h-5 text-[#E91E63]" />;
  if (type === 'video') return <Film className="w-5 h-5 text-purple-400" />;
  return <File className="w-5 h-5 text-gray-400" />;
};

const formatSize = (bytes) => {
  if (bytes === 0) return '—';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

export default function FileManager() {
  const { user } = useAuth();
  const [currentPath, setCurrentPath] = useState('/mnt/sata_m2');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('list');
  const [selectedItems, setSelectedItems] = useState([]);
  const [search, setSearch] = useState('');
  const [diskStats, setDiskStats] = useState(null);

  useEffect(() => {
    fetchFiles();
    fetchDiskStats();
  }, [currentPath]);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/files/browse?path=${encodeURIComponent(currentPath)}`);
      setItems(response.data.items || []);
    } catch (error) {
      toast.error('Failed to load files');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDiskStats = async () => {
    try {
      const response = await axios.get(`${API}/system/stats`);
      setDiskStats(response.data.disk);
    } catch (error) {
      console.error('Error fetching disk stats:', error);
    }
  };

  const navigateTo = (path) => {
    setCurrentPath(path);
    setSelectedItems([]);
  };

  const goUp = () => {
    const parts = currentPath.split('/').filter(Boolean);
    if (parts.length > 1) {
      parts.pop();
      navigateTo('/' + parts.join('/'));
    }
  };

  const handleItemClick = (item) => {
    if (item.is_dir) {
      navigateTo(item.path);
    } else {
      // Toggle selection
      setSelectedItems(prev => 
        prev.includes(item.path)
          ? prev.filter(p => p !== item.path)
          : [...prev, item.path]
      );
    }
  };

  const handleDelete = async () => {
    if (!user) {
      toast.error('Please login');
      return;
    }

    if (selectedItems.length === 0) return;

    const confirm = window.confirm(`Delete ${selectedItems.length} item(s)?`);
    if (!confirm) return;

    try {
      for (const path of selectedItems) {
        await axios.post(`${API}/files/move`, {
          source: path,
          destination: '',
          operation: 'delete'
        });
      }
      toast.success('Deleted successfully');
      setSelectedItems([]);
      fetchFiles();
    } catch (error) {
      toast.error('Delete failed');
    }
  };

  const filteredItems = items.filter(item => 
    !search || item.name.toLowerCase().includes(search.toLowerCase())
  );

  const pathParts = currentPath.split('/').filter(Boolean);

  return (
    <div className="min-h-screen bg-[#050505] pb-24" data-testid="file-manager-page">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-[#050505]/90 backdrop-blur-lg border-b border-[#222]">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-xl font-bold text-white">File Manager</h1>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setViewMode(viewMode === 'list' ? 'grid' : 'list')}
                className="text-gray-400"
                data-testid="toggle-view"
              >
                {viewMode === 'list' ? <Grid className="w-4 h-4" /> : <List className="w-4 h-4" />}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={fetchFiles}
                className="text-gray-400"
                data-testid="refresh-button"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>

          {/* Breadcrumb */}
          <div className="flex items-center gap-1 text-sm overflow-x-auto hide-scrollbar pb-2">
            <button
              onClick={() => navigateTo('/')}
              className="text-gray-400 hover:text-white p-1"
              data-testid="home-button"
            >
              <Home className="w-4 h-4" />
            </button>
            {pathParts.map((part, index) => (
              <div key={index} className="flex items-center">
                <ChevronRight className="w-4 h-4 text-gray-600" />
                <button
                  onClick={() => navigateTo('/' + pathParts.slice(0, index + 1).join('/'))}
                  className="text-gray-400 hover:text-white px-1 whitespace-nowrap"
                >
                  {part}
                </button>
              </div>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search files..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-[#1a1a1a] border-[#333] focus:border-[#E91E63] text-white h-10"
              data-testid="search-files"
            />
          </div>
        </div>

        {/* Selection toolbar */}
        <AnimatePresence>
          {selectedItems.length > 0 && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="bg-[#1a1a1a] border-t border-[#222] px-4 py-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">
                  {selectedItems.length} selected
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedItems([])}
                    className="text-gray-400"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDelete}
                    className="text-red-400 hover:text-red-300"
                    data-testid="delete-selected"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Disk Stats */}
      {diskStats && (
        <div className="px-4 py-3 border-b border-[#222]">
          <div className="flex gap-4 overflow-x-auto hide-scrollbar">
            {Object.entries(diskStats).map(([mount, stats]) => (
              <div key={mount} className="flex items-center gap-2 text-sm whitespace-nowrap">
                <HardDrive className="w-4 h-4 text-[#00F0FF]" />
                <span className="text-gray-400">{mount}:</span>
                {stats.error ? (
                  <span className="text-red-400">{stats.error}</span>
                ) : (
                  <span className="text-white">
                    {formatSize(stats.free)} free ({stats.percent}% used)
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* File List */}
      <ScrollArea className="h-[calc(100vh-280px)]">
        {loading && items.length === 0 ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#E91E63]" />
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <Folder className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p>No files found</p>
          </div>
        ) : viewMode === 'list' ? (
          <div className="divide-y divide-[#222]">
            {/* Go up button */}
            {pathParts.length > 0 && (
              <button
                onClick={goUp}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors"
                data-testid="go-up"
              >
                <ChevronLeft className="w-5 h-5 text-gray-500" />
                <span className="text-gray-400">..</span>
              </button>
            )}
            
            {filteredItems.map((item) => (
              <div
                key={item.path}
                onClick={() => handleItemClick(item)}
                className={`flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors ${
                  selectedItems.includes(item.path) 
                    ? 'bg-[#E91E63]/20' 
                    : 'hover:bg-white/5'
                }`}
                data-testid={`file-item-${item.name}`}
              >
                <FileIcon type={item.type} isDir={item.is_dir} />
                <div className="flex-1 min-w-0">
                  <p className="text-white truncate">{item.name}</p>
                  <p className="text-gray-500 text-xs">
                    {item.modified && new Date(item.modified).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-gray-500 text-sm">
                  {!item.is_dir && formatSize(item.size)}
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-gray-400">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-[#1a1a1a] border-[#333]">
                    <DropdownMenuItem className="text-gray-300">
                      <Copy className="w-4 h-4 mr-2" />
                      Copy
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-gray-300">
                      <Move className="w-4 h-4 mr-2" />
                      Move
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-red-400">
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 p-4">
            {filteredItems.map((item) => (
              <motion.div
                key={item.path}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                onClick={() => handleItemClick(item)}
                className={`flex flex-col items-center p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedItems.includes(item.path)
                    ? 'bg-[#E91E63]/20'
                    : 'hover:bg-white/5'
                }`}
                data-testid={`file-grid-${item.name}`}
              >
                {item.type === 'image' ? (
                  <div className="w-16 h-16 rounded-lg overflow-hidden bg-[#1a1a1a] mb-2">
                    <img 
                      src={`file://${item.path}`} 
                      alt="" 
                      className="w-full h-full object-cover"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                  </div>
                ) : (
                  <div className="w-16 h-16 flex items-center justify-center mb-2">
                    <FileIcon type={item.type} isDir={item.is_dir} />
                  </div>
                )}
                <p className="text-white text-xs text-center truncate w-full">{item.name}</p>
              </motion.div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
