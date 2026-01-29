import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Download, Search, Link2, Play, Image, Film, Loader2, 
  CheckCircle, XCircle, Clock, Trash2, FolderOpen, ExternalLink,
  AlertTriangle
} from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const StatusBadge = ({ status }) => {
  const config = {
    pending: { icon: Clock, color: 'bg-yellow-500/20 text-yellow-400', label: 'Pending' },
    running: { icon: Loader2, color: 'bg-blue-500/20 text-blue-400', label: 'Running' },
    completed: { icon: CheckCircle, color: 'bg-green-500/20 text-green-400', label: 'Completed' },
    failed: { icon: XCircle, color: 'bg-red-500/20 text-red-400', label: 'Failed' }
  };

  const { icon: Icon, color, label } = config[status] || config.pending;

  return (
    <Badge className={`${color} gap-1`}>
      <Icon className={`w-3 h-3 ${status === 'running' ? 'animate-spin' : ''}`} />
      {label}
    </Badge>
  );
};

export default function Scraper() {
  const { user } = useAuth();
  const [url, setUrl] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [outputPath, setOutputPath] = useState('/mnt/sata_m2/downloads');
  const [activeTab, setActiveTab] = useState('scraper');

  // OFScraper params
  const [ofParams, setOfParams] = useState({
    posts: 'ALL',
    usernames: 'ALL',
    scrape_paid: true,
    scrape_labels: true
  });

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API}/scraper/tasks?limit=20`);
      setTasks(response.data.tasks || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const analyzeUrl = async () => {
    if (!url.trim()) {
      toast.error('Please enter a URL');
      return;
    }

    setAnalyzing(true);
    setAnalysisResult(null);

    try {
      const response = await axios.post(`${API}/scraper/analyze`, { url });
      setAnalysisResult(response.data);
      
      if (response.data.error) {
        toast.error(response.data.error);
      } else {
        toast.success('Analysis complete!');
      }
    } catch (error) {
      toast.error('Failed to analyze URL');
      console.error(error);
    } finally {
      setAnalyzing(false);
    }
  };

  const startDownload = async (downloadUrl = url) => {
    if (!user) {
      toast.error('Please login to download');
      return;
    }

    setDownloading(true);

    try {
      const response = await axios.post(`${API}/scraper/download`, {
        url: downloadUrl,
        output_path: outputPath
      });
      
      toast.success(`Download started: ${response.data.task_id}`);
      fetchTasks();
    } catch (error) {
      toast.error('Failed to start download');
      console.error(error);
    } finally {
      setDownloading(false);
    }
  };

  const runOFScraper = async () => {
    if (!user) {
      toast.error('Please login to use OFScraper');
      return;
    }

    try {
      const response = await axios.post(`${API}/cli/ofscraper`, ofParams);
      toast.success(`OFScraper started: ${response.data.task_id}`);
      fetchTasks();
    } catch (error) {
      toast.error('Failed to start OFScraper');
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] pb-24 px-4 pt-4" data-testid="scraper-page">
      <h1 className="text-2xl font-bold text-white mb-6">Media Scraper</h1>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-[#121212] border border-[#222] mb-6">
          <TabsTrigger 
            value="scraper" 
            className="data-[state=active]:bg-[#E91E63] data-[state=active]:text-white"
            data-testid="scraper-tab"
          >
            <Download className="w-4 h-4 mr-2" />
            URL Scraper
          </TabsTrigger>
          <TabsTrigger 
            value="ofscraper"
            className="data-[state=active]:bg-[#E91E63] data-[state=active]:text-white"
            data-testid="ofscraper-tab"
          >
            <FolderOpen className="w-4 h-4 mr-2" />
            OFScraper
          </TabsTrigger>
          <TabsTrigger 
            value="history"
            className="data-[state=active]:bg-[#E91E63] data-[state=active]:text-white"
            data-testid="history-tab"
          >
            <Clock className="w-4 h-4 mr-2" />
            History
          </TabsTrigger>
        </TabsList>

        {/* URL Scraper Tab */}
        <TabsContent value="scraper" className="space-y-4">
          <Card className="bg-[#121212] border-[#222]">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Link2 className="w-5 h-5 text-[#E91E63]" />
                Download from URL
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter URL (fikfap.com, tiktok, etc.)"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1 bg-[#1a1a1a] border-[#333] focus:border-[#E91E63] text-white font-mono text-sm"
                  data-testid="url-input"
                />
                <Button
                  onClick={analyzeUrl}
                  disabled={analyzing}
                  className="bg-[#00F0FF] hover:bg-[#00D4E0] text-black font-semibold"
                  data-testid="analyze-button"
                >
                  {analyzing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                  <span className="ml-2">Analyze</span>
                </Button>
              </div>

              <div className="flex gap-2">
                <Input
                  placeholder="Output path"
                  value={outputPath}
                  onChange={(e) => setOutputPath(e.target.value)}
                  className="flex-1 bg-[#1a1a1a] border-[#333] focus:border-[#E91E63] text-white font-mono text-sm"
                  data-testid="output-path-input"
                />
                <Button
                  onClick={() => startDownload()}
                  disabled={downloading || !url}
                  className="bg-[#E91E63] hover:bg-[#C2185B] text-white font-semibold"
                  data-testid="download-button"
                >
                  {downloading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                  <span className="ml-2">Download</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Results */}
          <AnimatePresence>
            {analysisResult && !analysisResult.error && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Card className="bg-[#121212] border-[#222]">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg text-white">
                      {analysisResult.title || 'Media Found'}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {/* Thumbnail */}
                    {analysisResult.thumbnail && (
                      <img 
                        src={analysisResult.thumbnail} 
                        alt="" 
                        className="w-full max-w-md rounded-lg mb-4"
                      />
                    )}

                    {/* Formats */}
                    {analysisResult.formats?.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-gray-400 mb-2">Available Formats</h4>
                        <div className="flex flex-wrap gap-2">
                          {analysisResult.formats.map((fmt, i) => (
                            <Badge key={i} className="bg-[#1a1a1a] text-gray-300">
                              {fmt.resolution || fmt.ext} {fmt.filesize ? `(${(fmt.filesize / 1024 / 1024).toFixed(1)}MB)` : ''}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Playlist entries */}
                    {analysisResult.entries?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-400 mb-2">
                          Found {analysisResult.entries.length} items
                        </h4>
                        <ScrollArea className="h-64">
                          <div className="space-y-2">
                            {analysisResult.entries.map((entry, i) => (
                              <div 
                                key={i}
                                className="flex items-center gap-3 p-2 rounded-lg bg-[#1a1a1a] hover:bg-[#252525] cursor-pointer"
                                onClick={() => startDownload(entry.url)}
                                data-testid={`entry-${i}`}
                              >
                                {entry.thumbnail && (
                                  <img src={entry.thumbnail} alt="" className="w-16 h-12 rounded object-cover" />
                                )}
                                <div className="flex-1 min-w-0">
                                  <p className="text-white text-sm truncate">{entry.title || `Item ${i + 1}`}</p>
                                  {entry.duration && (
                                    <p className="text-gray-500 text-xs">{Math.floor(entry.duration / 60)}:{String(entry.duration % 60).padStart(2, '0')}</p>
                                  )}
                                </div>
                                <Download className="w-4 h-4 text-[#E91E63]" />
                              </div>
                            ))}
                          </div>
                        </ScrollArea>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </TabsContent>

        {/* OFScraper Tab */}
        <TabsContent value="ofscraper" className="space-y-4">
          <Card className="bg-[#121212] border-[#222]">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <FolderOpen className="w-5 h-5 text-[#00F0FF]" />
                OFScraper Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Posts</label>
                  <Input
                    value={ofParams.posts}
                    onChange={(e) => setOfParams({ ...ofParams, posts: e.target.value })}
                    className="bg-[#1a1a1a] border-[#333] focus:border-[#E91E63] text-white font-mono"
                    placeholder="ALL"
                    data-testid="of-posts-input"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Usernames</label>
                  <Input
                    value={ofParams.usernames}
                    onChange={(e) => setOfParams({ ...ofParams, usernames: e.target.value })}
                    className="bg-[#1a1a1a] border-[#333] focus:border-[#E91E63] text-white font-mono"
                    placeholder="ALL"
                    data-testid="of-usernames-input"
                  />
                </div>
              </div>

              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={ofParams.scrape_paid}
                    onChange={(e) => setOfParams({ ...ofParams, scrape_paid: e.target.checked })}
                    className="rounded border-[#333] bg-[#1a1a1a] text-[#E91E63] focus:ring-[#E91E63]"
                  />
                  Scrape Paid
                </label>
                <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={ofParams.scrape_labels}
                    onChange={(e) => setOfParams({ ...ofParams, scrape_labels: e.target.checked })}
                    className="rounded border-[#333] bg-[#1a1a1a] text-[#E91E63] focus:ring-[#E91E63]"
                  />
                  Scrape Labels
                </label>
              </div>

              <div className="bg-[#0a0a0a] rounded-lg p-3 font-mono text-sm">
                <span className="text-[#E91E63]">$</span>
                <span className="text-[#00F0FF]"> python -m ofscraper</span>
                <span className="text-gray-400"> --posts {ofParams.posts} --usernames {ofParams.usernames}</span>
                {ofParams.scrape_paid && <span className="text-gray-400"> --scrape-paid</span>}
                {ofParams.scrape_labels && <span className="text-gray-400"> --scrape-labels</span>}
              </div>

              <Button
                onClick={runOFScraper}
                className="w-full bg-[#E91E63] hover:bg-[#C2185B] text-white font-semibold"
                data-testid="run-ofscraper-button"
              >
                <Play className="w-4 h-4 mr-2" />
                Run OFScraper
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history">
          <Card className="bg-[#121212] border-[#222]">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white">Download History</CardTitle>
            </CardHeader>
            <CardContent>
              {tasks.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No download history yet</p>
                </div>
              ) : (
                <ScrollArea className="h-96">
                  <div className="space-y-2">
                    {tasks.map((task) => (
                      <div 
                        key={task.id}
                        className="flex items-center gap-3 p-3 rounded-lg bg-[#1a1a1a] hover:bg-[#252525]"
                        data-testid={`task-${task.id}`}
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-white text-sm truncate font-mono">{task.url}</p>
                          <p className="text-gray-500 text-xs">
                            {task.created_at && new Date(task.created_at).toLocaleString()}
                          </p>
                        </div>
                        <StatusBadge status={task.status} />
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
