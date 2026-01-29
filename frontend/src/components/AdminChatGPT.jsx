import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  Download, 
  Send, 
  Menu, 
  X,
  Terminal,
  ChevronRight,
  Edit2,
  Check
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/chatgpt`;

// Code block component for syntax highlighting
const CodeBlock = ({ language, children }) => {
  return (
    <SyntaxHighlighter
      language={language || 'text'}
      style={atomDark}
      customStyle={{
        margin: '0.5rem 0',
        padding: '1rem',
        background: '#0A0A0A',
        border: '1px solid #333',
        borderRadius: '0',
        fontSize: '0.875rem',
      }}
    >
      {children}
    </SyntaxHighlighter>
  );
};

// Parse message content for code blocks
const MessageContent = ({ content }) => {
  const parts = content.split(/(```[\s\S]*?```)/g);
  
  return (
    <div className="whitespace-pre-wrap break-words">
      {parts.map((part, index) => {
        if (part.startsWith('```') && part.endsWith('```')) {
          const match = part.match(/```(\w+)?\n?([\s\S]*?)```/);
          if (match) {
            const [, language, code] = match;
            return <CodeBlock key={index} language={language}>{code.trim()}</CodeBlock>;
          }
        }
        return <span key={index}>{part}</span>;
      })}
    </div>
  );
};

function AdminChatGPT() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [editingTitle, setEditingTitle] = useState(null);
  const [newTitle, setNewTitle] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Fetch sessions on mount
  useEffect(() => {
    fetchSessions();
  }, []);

  // Fetch messages when session changes
  useEffect(() => {
    if (currentSession) {
      fetchMessages(currentSession.id);
    } else {
      setMessages([]);
    }
  }, [currentSession]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API}/sessions`);
      setSessions(res.data);
    } catch (e) {
      toast.error("Failed to load sessions");
    }
  };

  const fetchMessages = async (sessionId) => {
    try {
      const res = await axios.get(`${API}/sessions/${sessionId}/messages`);
      setMessages(res.data);
    } catch (e) {
      toast.error("Failed to load messages");
    }
  };

  const createNewSession = async () => {
    try {
      const res = await axios.post(`${API}/sessions`, { title: "New Chat" });
      setSessions([res.data, ...sessions]);
      setCurrentSession(res.data);
      setMessages([]);
      toast.success("New chat created");
    } catch (e) {
      toast.error("Failed to create session");
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      await axios.delete(`${API}/sessions/${sessionId}`);
      setSessions(sessions.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
      toast.success("Chat deleted");
    } catch (e) {
      toast.error("Failed to delete session");
    }
  };

  const updateSessionTitle = async (sessionId, title) => {
    try {
      await axios.put(`${API}/sessions/${sessionId}`, { title });
      setSessions(sessions.map(s => s.id === sessionId ? { ...s, title } : s));
      if (currentSession?.id === sessionId) {
        setCurrentSession({ ...currentSession, title });
      }
      setEditingTitle(null);
    } catch (e) {
      toast.error("Failed to update title");
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    if (!currentSession) {
      await createNewSession();
    }
    
    const sessionId = currentSession?.id;
    if (!sessionId) return;

    const userMessage = {
      id: Date.now().toString(),
      session_id: sessionId,
      role: "user",
      content: inputValue,
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const res = await axios.post(`${API}/sessions/${sessionId}/messages`, {
        content: inputValue
      });
      setMessages(prev => [...prev.filter(m => m.id !== userMessage.id), userMessage, res.data]);
      fetchSessions(); // Refresh to get updated title
    } catch (e) {
      toast.error("Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  const exportSession = async (format = "json") => {
    if (!currentSession) return;
    try {
      const res = await axios.get(`${API}/sessions/${currentSession.id}/export?format=${format}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `chat_${currentSession.id}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (e) {
      toast.error("Export failed");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="h-screen flex bg-[#050505] overflow-hidden">
      {/* Mobile menu button */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-card border border-border"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} 
          md:translate-x-0 fixed md:relative z-40 w-[260px] h-full 
          bg-card/80 backdrop-blur-xl border-r border-border 
          transition-transform duration-200 flex flex-col`}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2 mb-4">
            <Terminal className="text-primary" size={24} />
            <span className="font-mono text-lg font-bold tracking-tight neon-text">ADMIN AI</span>
          </div>
          <Button
            onClick={createNewSession}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 
              rounded-none font-mono uppercase tracking-wider text-xs py-3
              transition-all hover:shadow-[0_0_15px_rgba(0,229,255,0.4)]"
          >
            <Plus size={16} className="mr-2" />
            NEW CHAT
          </Button>
        </div>

        {/* Sessions List */}
        <ScrollArea className="flex-1">
          <div className="p-2">
            {sessions.map(session => (
              <div
                key={session.id}
                className={`group flex items-center gap-2 p-3 cursor-pointer 
                  transition-colors border border-transparent hover:bg-white/5
                  ${currentSession?.id === session.id ? 'bg-secondary border-primary/30' : ''}`}
                onClick={() => {
                  setCurrentSession(session);
                  if (window.innerWidth < 768) setSidebarOpen(false);
                }}
              >
                <MessageSquare size={16} className="text-muted-foreground flex-shrink-0" />
                
                {editingTitle === session.id ? (
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') updateSessionTitle(session.id, newTitle);
                      if (e.key === 'Escape') setEditingTitle(null);
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="flex-1 bg-input border border-border px-2 py-1 text-sm font-mono"
                    autoFocus
                  />
                ) : (
                  <span className="flex-1 text-sm font-mono truncate">
                    {session.title}
                  </span>
                )}
                
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {editingTitle === session.id ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        updateSessionTitle(session.id, newTitle);
                      }}
                      className="p-1 hover:text-primary"
                    >
                      <Check size={14} />
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingTitle(session.id);
                        setNewTitle(session.title);
                      }}
                      className="p-1 hover:text-primary"
                    >
                      <Edit2 size={14} />
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                    className="p-1 hover:text-accent"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-border">
          <p className="text-xs text-muted-foreground font-mono">
            ADMIN PANEL // GPT-5 MINI
          </p>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full">
        {/* Chat Header */}
        {currentSession && (
          <header className="p-4 border-b border-border flex items-center justify-between bg-card/50 backdrop-blur">
            <h1 className="font-mono text-lg truncate ml-12 md:ml-0">
              {currentSession.title}
            </h1>
            <div className="flex gap-2">
              <Button
                onClick={() => exportSession("json")}
                variant="outline"
                size="sm"
                className="rounded-none font-mono text-xs border-border hover:border-primary hover:text-primary"
              >
                <Download size={14} className="mr-1" />
                JSON
              </Button>
              <Button
                onClick={() => exportSession("txt")}
                variant="outline"
                size="sm"
                className="rounded-none font-mono text-xs border-border hover:border-primary hover:text-primary"
              >
                <Download size={14} className="mr-1" />
                TXT
              </Button>
            </div>
          </header>
        )}

        {/* Messages Area */}
        <ScrollArea className="flex-1">
          <div className="max-w-3xl mx-auto w-full p-4 md:p-6">
            {messages.length === 0 && !currentSession ? (
              <div className="flex flex-col items-center justify-center h-[60vh] text-center">
                <Terminal className="text-primary mb-4" size={64} />
                <h2 className="font-mono text-2xl md:text-3xl font-bold mb-2 neon-text">
                  ADMIN AI ASSISTANT
                </h2>
                <p className="text-muted-foreground font-mono text-sm max-w-md">
                  No filters. No limits. Ask anything.
                </p>
                <Button
                  onClick={createNewSession}
                  className="mt-6 bg-primary text-primary-foreground hover:bg-primary/90 
                    rounded-none font-mono uppercase tracking-wider text-xs px-8 py-4
                    transition-all hover:shadow-[0_0_20px_rgba(0,229,255,0.5)]"
                >
                  START CHATTING
                </Button>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-[60vh] text-center">
                <p className="text-muted-foreground font-mono">
                  Type your message below to begin...
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg, idx) => (
                  <div
                    key={msg.id || idx}
                    className={`animate-fade-in flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] p-4 ${
                        msg.role === 'user'
                          ? 'bg-secondary text-secondary-foreground rounded-tl-lg rounded-bl-lg rounded-br-lg'
                          : 'bg-transparent border border-border text-foreground rounded-tr-lg rounded-br-lg rounded-bl-lg font-mono text-sm'
                      }`}
                    >
                      <MessageContent content={msg.content} />
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start animate-fade-in">
                    <div className="bg-transparent border border-border p-4 rounded-tr-lg rounded-br-lg rounded-bl-lg">
                      <span className="font-mono text-primary">
                        PROCESSING<span className="typing-cursor">_</span>
                      </span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="p-4 border-t border-border bg-card/50 backdrop-blur">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center gap-2 bg-background border border-border p-2 focus-within:border-primary focus-within:shadow-[0_0_10px_rgba(0,229,255,0.2)] transition-all">
              <ChevronRight className="text-primary ml-2" size={20} />
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Enter command..."
                rows={1}
                className="flex-1 bg-transparent border-none focus:outline-none focus:ring-0 
                  font-mono text-sm placeholder:text-muted-foreground/50 resize-none py-2"
                disabled={isLoading}
              />
              <Button
                onClick={sendMessage}
                disabled={isLoading || !inputValue.trim()}
                className="bg-primary text-primary-foreground hover:bg-primary/90 
                  rounded-none p-2 h-10 w-10 transition-all hover:shadow-[0_0_15px_rgba(0,229,255,0.4)]"
              >
                <Send size={18} />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground font-mono mt-2 text-center">
              Press Enter to send • Shift+Enter for new line
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default AdminChatGPT;
