import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Terminal as TerminalIcon, Send, Trash2, Copy, Check, ChevronRight } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { ScrollArea } from '../components/ui/scroll-area';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Terminal() {
  const { user } = useAuth();
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState([
    { type: 'system', content: 'Welcome to Clone Terminal. Type commands to interact with your server.' },
    { type: 'system', content: 'Warning: Commands execute with full privileges. Be careful!' }
  ]);
  const [loading, setLoading] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [cwd, setCwd] = useState('/mnt/sata_m2');
  const [copied, setCopied] = useState(null);
  const inputRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [history]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const executeCommand = async (e) => {
    e?.preventDefault();
    
    if (!command.trim()) return;
    
    if (!user) {
      toast.error('Please login to use the terminal');
      return;
    }

    // Add command to history
    setHistory(prev => [...prev, { type: 'command', content: command, cwd }]);
    setCommandHistory(prev => [command, ...prev]);
    setHistoryIndex(-1);

    // Handle built-in commands
    if (command.trim() === 'clear') {
      setHistory([]);
      setCommand('');
      return;
    }

    if (command.trim().startsWith('cd ')) {
      const newPath = command.trim().substring(3);
      setCwd(newPath.startsWith('/') ? newPath : `${cwd}/${newPath}`);
      setHistory(prev => [...prev, { type: 'output', content: '' }]);
      setCommand('');
      return;
    }

    setLoading(true);
    setCommand('');

    try {
      const response = await axios.post(`${API}/cli/execute`, {
        command: command,
        cwd: cwd
      });

      const output = [];
      if (response.data.stdout) {
        output.push({ type: 'output', content: response.data.stdout });
      }
      if (response.data.stderr) {
        output.push({ type: 'error', content: response.data.stderr });
      }
      if (response.data.error) {
        output.push({ type: 'error', content: response.data.error });
      }
      if (output.length === 0) {
        output.push({ type: 'output', content: '(no output)' });
      }

      setHistory(prev => [...prev, ...output]);
    } catch (error) {
      setHistory(prev => [...prev, { 
        type: 'error', 
        content: error.response?.data?.detail || 'Command execution failed' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIndex < commandHistory.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setCommand(commandHistory[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setCommand(commandHistory[newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setCommand('');
      }
    }
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopied(index);
    setTimeout(() => setCopied(null), 2000);
  };

  const quickCommands = [
    { label: 'List Files', cmd: 'ls -la' },
    { label: 'Disk Usage', cmd: 'df -h' },
    { label: 'Processes', cmd: 'ps aux | head -20' },
    { label: 'Memory', cmd: 'free -h' },
  ];

  return (
    <div className="min-h-screen bg-[#050505] pb-24 flex flex-col" data-testid="terminal-page">
      {/* Header */}
      <div className="bg-[#0a0a0a] border-b border-[#222] px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TerminalIcon className="w-5 h-5 text-[#00F0FF]" />
            <h1 className="text-lg font-bold text-white">Server Terminal</h1>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setHistory([])}
            className="text-gray-400 hover:text-white"
            data-testid="clear-terminal"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
        
        {/* Quick commands */}
        <div className="flex gap-2 mt-3 overflow-x-auto hide-scrollbar pb-1">
          {quickCommands.map((qc, i) => (
            <Button
              key={i}
              variant="outline"
              size="sm"
              className="border-[#333] text-gray-300 hover:bg-[#1a1a1a] whitespace-nowrap text-xs"
              onClick={() => setCommand(qc.cmd)}
              data-testid={`quick-cmd-${i}`}
            >
              {qc.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Terminal Output */}
      <ScrollArea 
        ref={scrollRef}
        className="flex-1 bg-[#0a0a0a]"
        data-testid="terminal-output"
      >
        <div className="p-4 font-mono text-sm space-y-1">
          {history.map((entry, index) => (
            <div key={index} className="group relative">
              {entry.type === 'system' && (
                <div className="text-gray-500 italic">{entry.content}</div>
              )}
              {entry.type === 'command' && (
                <div className="flex items-start gap-2 text-white">
                  <span className="text-[#E91E63] select-none">{entry.cwd}$</span>
                  <span className="text-[#00F0FF]">{entry.content}</span>
                </div>
              )}
              {entry.type === 'output' && (
                <div className="text-gray-300 whitespace-pre-wrap pl-4 terminal-output">
                  {entry.content}
                  {entry.content && (
                    <button
                      onClick={() => copyToClipboard(entry.content, index)}
                      className="absolute right-2 top-0 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      {copied === index ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4 text-gray-500 hover:text-white" />
                      )}
                    </button>
                  )}
                </div>
              )}
              {entry.type === 'error' && (
                <div className="text-red-400 whitespace-pre-wrap pl-4">{entry.content}</div>
              )}
            </div>
          ))}
          
          {loading && (
            <div className="flex items-center gap-2 text-gray-500">
              <div className="animate-pulse">●</div>
              <span>Executing...</span>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="bg-[#0a0a0a] border-t border-[#222] p-4">
        <form onSubmit={executeCommand} className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-[#E91E63] font-mono text-sm whitespace-nowrap">
            <ChevronRight className="w-4 h-4" />
            <span className="hidden sm:inline">{cwd}$</span>
          </div>
          <Input
            ref={inputRef}
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter command..."
            className="flex-1 bg-transparent border-none focus:ring-0 text-[#00F0FF] font-mono placeholder:text-gray-600"
            disabled={loading}
            data-testid="terminal-input"
          />
          <Button
            type="submit"
            disabled={loading || !command.trim()}
            className="bg-[#E91E63] hover:bg-[#C2185B]"
            data-testid="execute-button"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
