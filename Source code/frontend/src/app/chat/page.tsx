"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Sparkles,
  PanelLeft,
  SquarePen,
  Search,
  Mic,
  ChevronDown,
  MessageSquare,
  Plus,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Copy,
  MoreHorizontal,
  X,
  ChevronLeft,
  ChevronRight,
  Square,
  LogOut,
} from 'lucide-react';
import { getSession, useSession, signOut } from "next-auth/react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const STREAMLIT_BASE_URL = process.env.NEXT_PUBLIC_STREAMLIT_URL || 'http://localhost:8501';

export default function ChatPage() {
  const { data: session } = useSession();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const scannerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
      if (scannerRef.current && !scannerRef.current.contains(event.target as Node)) {
        setIsScannerOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);
  const [sidebarWidth, setSidebarWidth] = useState(200); // Set default to minimum allowed width (200px)
  const [isResizing, setIsResizing] = useState(false);
  const [scannerWidth, setScannerWidth] = useState(950); // Default increased by 200px (from 750px to 950px)
  const [isScannerResizing, setIsScannerResizing] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'model', content: string }[]>([]);
  const [scannedPrompts, setScannedPrompts] = useState<string[]>([]);
  const [isScannerOpen, setIsScannerOpen] = useState(false);
  const [currentScanIndex, setCurrentScanIndex] = useState(0);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const currentPrompt = inputValue.trim();
    // Add user message
    const newMessages = [...messages, { role: 'user' as const, content: currentPrompt }];
    setMessages(newMessages);

    // Save prompt to scannedPrompts list
    setScannedPrompts(prev => {
      const updated = [...prev, currentPrompt];
      // Automatically focus on the newly scanned prompt
      setCurrentScanIndex(updated.length - 1);
      return updated;
    });

    setInputValue('');
    setIsLoading(true);

    const controller = new AbortController();
    setAbortController(controller);

    try {
      const session = await getSession();
      const token = (session as any)?.accessToken;

      if (!token) {
        window.location.href = '/';
        return;
      }
      const response = await fetch(`${API_BASE_URL}/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt: currentPrompt }),
        signal: controller.signal,
      });

      if (response.status === 401) {
        window.location.href = '/';
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const data = await response.json();

      // Update messages with the model response
      setMessages(prev => [...prev, {
        role: 'model',
        content: data.generated_text
      }]);

      // Refresh recent chats list
      fetchRecentChats();
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Scan aborted by user');
      } else {
        console.warn("Backend connection failed. Is the server running on port 8000?", error);
        setMessages(prev => [...prev, {
          role: 'model',
          content: "Sorry, I encountered an error while trying to generate a response. Please make sure the backend server is running on port 8000."
        }]);
      }
    } finally {
      setIsLoading(false);
      setAbortController(null);
    }
  };

  const handleStop = () => {
    if (abortController) {
      abortController.abort();
    }
  };

  const startResizing = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    if (isSidebarOpen) {
      setIsResizing(true);
    }
  }, [isSidebarOpen]);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback((e: MouseEvent) => {
    if (isResizing && isSidebarOpen) {
      const newWidth = e.clientX;
      if (newWidth > 200 && newWidth < 600) {
        setSidebarWidth(newWidth);
      }
    }
  }, [isResizing, isSidebarOpen]);

  useEffect(() => {
    if (isResizing) {
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    }
    window.addEventListener('mousemove', resize);
    window.addEventListener('mouseup', stopResizing);
    return () => {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
    };
  }, [resize, stopResizing, isResizing]);

  const startScannerResizing = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    if (isScannerOpen) {
      setIsScannerResizing(true);
    }
  }, [isScannerOpen]);

  const stopScannerResizing = useCallback(() => {
    setIsScannerResizing(false);
  }, []);

  const resizeScanner = useCallback((e: MouseEvent) => {
    if (isScannerResizing && isScannerOpen) {
      const newWidth = window.innerWidth - e.clientX;
      if (newWidth > 350 && newWidth < 1400) {
        setScannerWidth(newWidth);
      }
    }
  }, [isScannerResizing, isScannerOpen]);

  useEffect(() => {
    if (isScannerResizing) {
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    }
    window.addEventListener('mousemove', resizeScanner);
    window.addEventListener('mouseup', stopScannerResizing);
    return () => {
      window.removeEventListener('mousemove', resizeScanner);
      window.removeEventListener('mouseup', stopScannerResizing);
    };
  }, [resizeScanner, stopScannerResizing, isScannerResizing]);

  const [recentChats, setRecentChats] = useState<{ id: string, prompt: string, response: string, timestamp: string }[]>([]);
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);

  const fetchRecentChats = useCallback(async () => {
    const token = (session as any)?.accessToken;
    if (!token) return;
    try {
      const response = await fetch(`${API_BASE_URL}/recent-chats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      if (response.ok) {
        const data = await response.json();
        setRecentChats(data);
      }
    } catch (err) {
      console.warn("Failed to fetch recent chats", err);
    }
  }, [session]);

  const deleteChat = async (chatId: string) => {
    const token = (session as any)?.accessToken;
    if (!token) return;
    try {
      const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      if (response.ok) {
        const chatToDelete = recentChats.find(c => c.id === chatId);
        setRecentChats(prev => prev.filter(c => c.id !== chatId));
        if (chatToDelete && messages.length > 0 && messages[0].content === chatToDelete.prompt) {
          setMessages([]);
          setScannedPrompts([]);
          setCurrentScanIndex(0);
          setIsScannerOpen(false);
        }
      } else {
        console.warn("Failed to delete chat", await response.text());
      }
    } catch (err) {
      console.warn("Error deleting chat", err);
    }
    setActiveMenuId(null);
  };

  useEffect(() => {
    fetchRecentChats();
  }, [fetchRecentChats]);

  const inputForm = (
    <div className="w-full flex flex-col items-center">
      <form onSubmit={handleSubmit} className="w-full relative flex items-center bg-[#1e1f22] rounded-full p-2 pl-4 pr-3 shadow-lg border border-white/5">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading}
          placeholder={isLoading ? "Thinking..." : "Ask Mistral 7B"}
          className="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-400 px-3 py-3 text-[15px] disabled:opacity-50"
        />

        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          <button type="button" className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-white/5 rounded-full transition-colors text-sm font-medium text-gray-300">
            Mistral 7B
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </button>

          {isLoading ? (
            <button
              type="button"
              onClick={handleStop}
              className="flex items-center justify-center w-8 h-8 hover:bg-white/5 rounded-[10px] transition-colors text-gray-400 hover:text-white border border-gray-600 hover:border-gray-400 ml-1"
            >
              <Square className="w-3 h-3 fill-current" />
            </button>
          ) : (
            <button type="button" className="p-2.5 hover:bg-white/5 rounded-full transition-colors text-gray-400 hover:text-white">
              <Mic className="w-5 h-5" />
            </button>
          )}
        </div>
      </form>
      <div className="text-center mt-3 text-xs text-gray-500 font-medium">
        Mistral 7b is AI and can make mistakes.
      </div>
    </div>
  );

  return (
    <div className="flex h-screen w-full bg-[#131314] text-gray-200 font-sans">
      {/* Sidebar */}
      <aside
        className={`flex flex-col justify-between relative flex-shrink-0 transition-all duration-300 ease-in-out ${isSidebarOpen ? 'bg-[#1e1f22]' : 'bg-transparent'} z-30`}
        style={{ width: isSidebarOpen ? sidebarWidth : 68 }}
      >
        <div className="flex-1 overflow-y-auto overflow-x-hidden flex flex-col">
          {/* Header */}
          <div
            className={`p-4 flex items-center ${isSidebarOpen ? 'justify-between' : 'justify-center cursor-pointer mt-2 mb-2'}`}
            onClick={() => !isSidebarOpen && setIsSidebarOpen(true)}
          >
            {isSidebarOpen ? (
              <>
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-400" />
                  <span className="text-lg font-semibold tracking-wide text-white whitespace-nowrap">LLM Scan</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsSidebarOpen(false);
                  }}
                  className="p-2 hover:bg-white/10 rounded-full transition-colors"
                >
                  <PanelLeft className="w-5 h-5 text-gray-400" />
                </button>
              </>
            ) : (
              <div className="relative">
                <Sparkles className="w-6 h-6 text-blue-400 fill-blue-400/20" />
              </div>
            )}
          </div>

          <div className={`${isSidebarOpen ? 'px-3 py-2' : 'flex justify-center mb-6'}`}>
            <button
              onClick={() => {
                setMessages([]);
                setInputValue('');
                setScannedPrompts([]);
                setCurrentScanIndex(0);
                setIsScannerOpen(false);
              }}
              className={`flex items-center justify-center ${isSidebarOpen ? 'gap-3 w-full px-4 rounded-full' : 'w-10 h-10 rounded-full'} py-2.5 bg-[#282a2d] hover:bg-[#34373a] text-sm font-medium transition-colors text-white whitespace-nowrap`}
            >
              <SquarePen className={`${isSidebarOpen ? 'w-4 h-4' : 'w-5 h-5 text-gray-100'} flex-shrink-0`} />
              {isSidebarOpen && <span className="truncate">New chat</span>}
            </button>
          </div>

          {/* Top Navigation */}
          <nav className={`${isSidebarOpen ? 'mt-2 px-3 space-y-0.5' : 'flex flex-col items-center space-y-6'}`}>
            <a href="#" className={`flex items-center ${isSidebarOpen ? 'gap-3 px-3 w-full py-2 rounded-xl hover:bg-white/5' : 'justify-center text-gray-200 hover:text-white'} text-sm font-medium text-gray-300 whitespace-nowrap`}>
              <Search className={`${isSidebarOpen ? 'w-4 h-4' : 'w-5 h-5'} flex-shrink-0`} />
              {isSidebarOpen && <span className="truncate">Search chats</span>}
            </a>
          </nav>

          {/* Recent Section */}
          <div className={`mt-6 px-3 mb-6 transition-all duration-300 ${isSidebarOpen ? 'opacity-100' : 'opacity-0 h-0 overflow-hidden m-0 p-0'}`}>
            <h3 className="px-3 text-xs font-semibold text-gray-500 mb-2">Recent</h3>
            <div className="space-y-0.5">
              {recentChats.map((chat) => (
                <div
                  key={chat.id}
                  onMouseLeave={() => setActiveMenuId(null)}
                  className="group relative flex items-center justify-between rounded-xl hover:bg-white/5 pr-2"
                >
                  <button
                    onClick={() => {
                      setMessages([
                        { role: 'user', content: chat.prompt },
                        { role: 'model', content: chat.response }
                      ]);
                      setScannedPrompts([chat.prompt]);
                      setCurrentScanIndex(0);
                      setIsScannerOpen(true);
                    }}
                    onMouseDown={(e) => e.stopPropagation()}
                    className="flex items-center gap-3 pl-3 pr-8 py-2 w-full text-sm text-gray-300 text-left transition-colors truncate"
                    title={chat.prompt}
                  >
                    <MessageSquare className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    <span className="truncate">{chat.prompt}</span>
                  </button>

                  <div className="absolute right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveMenuId(prev => prev === chat.id ? null : chat.id);
                      }}
                      className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>

                    {activeMenuId === chat.id && (
                      <div className="absolute right-0 mt-1 w-24 bg-[#282a2d] border border-white/10 rounded-lg shadow-xl py-1 z-50">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteChat(chat.id);
                          }}
                          className="w-full text-left px-3 py-1.5 text-xs text-red-400 hover:bg-red-400/10 transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {recentChats.length === 0 && (
                <p className="px-3 py-2 text-xs text-gray-500 italic">No recent chats</p>
              )}
            </div>
          </div>
        </div>

        {/* User Footer */}
        <div className={`p-4 mt-auto flex ${isSidebarOpen ? 'items-center justify-between border-t border-white/5' : 'flex-col items-center gap-6 pb-6'}`}>
          <div className="flex items-center gap-3 overflow-visible" ref={dropdownRef}>
            <div
              className="relative group cursor-pointer flex-shrink-0"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              {/* Outer colorful ring (Rainbow Colors) */}
              <div
                className={`${isSidebarOpen ? 'w-9 h-9' : 'w-10 h-10'} rounded-full flex items-center justify-center p-[2px]`}
                style={{ background: "conic-gradient(from 0deg, #ff0000, #ff8000, #ffff00, #00ff00, #00ffff, #0000ff, #8000ff, #ff00ff, #ff0000)" }}
              >
                {/* Gap between ring and avatar */}
                <div className="w-full h-full bg-[#1e1f22] rounded-full flex items-center justify-center p-[2px]">
                  {/* Avatar */}
                  <div className="w-full h-full bg-[#7B1FA2] rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">
                      {session?.user?.name?.charAt(0).toUpperCase() || session?.user?.email?.charAt(0).toUpperCase() || 'U'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Dropdown Menu */}
              <AnimatePresence>
                {isDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className={`absolute bottom-full mb-3 w-64 bg-[#282a2d] rounded-xl shadow-2xl border border-white/10 overflow-hidden z-50 cursor-default ${isSidebarOpen ? 'left-0' : 'left-1/2 -translate-x-1/2'}`}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="p-4 border-b border-white/5">
                      <p className="text-sm font-medium text-white truncate">
                        {session?.user?.name || session?.user?.email?.split('@')[0] || 'User'}
                      </p>
                      <p className="text-xs text-gray-400 truncate mt-1">
                        {session?.user?.email || 'No email available'}
                      </p>
                    </div>
                    <div className="p-2">
                      <button
                        onClick={() => signOut({ callbackUrl: '/' })}
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded-lg transition-colors font-medium"
                      >
                        <LogOut className="w-4 h-4" />
                        Sign out
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {isSidebarOpen && (
              <div className="flex flex-col overflow-hidden">
                <span className="text-sm font-medium text-white leading-tight truncate">
                  {session?.user?.name || session?.user?.email?.split('@')[0] || 'User'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Resizer Handle */}
        {isSidebarOpen && (
          <div
            className="absolute right-0 top-0 bottom-0 w-1.5 cursor-col-resize hover:bg-blue-500/50 active:bg-blue-500 transition-colors z-10"
            onMouseDown={startResizing}
          />
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative bg-gradient-to-b from-[#131314] to-[#0f1218] overflow-hidden min-h-0">

        {/* Scanner Button (Top Left of Main Content) */}
        <div className="absolute top-4 left-4 z-20">
          <button
            onClick={() => setIsScannerOpen(prev => !prev)}
            onMouseDown={(e) => e.stopPropagation()}
            className="group flex items-center p-3 hover:bg-white/10 rounded-full transition-all duration-300 hover:scale-110 active:scale-95 overflow-hidden"
          >
            <img src="/scanner.png" alt="Scanner" className="w-8 h-8 object-contain flex-shrink-0" />
            <span className="max-w-0 opacity-0 group-hover:max-w-xs group-hover:opacity-100 group-hover:ml-3 transition-all duration-300 text-base font-medium text-white whitespace-nowrap overflow-hidden">
              LLM Scanner
            </span>
          </button>
        </div>

        {/* Top Right Edit Button */}
        <div className="absolute top-4 right-4">
          <button className="p-2 hover:bg-white/5 rounded-full transition-colors text-gray-400 hover:text-white">
            <SquarePen className="w-5 h-5" />
          </button>
        </div>

        {/* Chat Area */}
        <div className="flex-1 w-full flex justify-center overflow-y-auto min-h-0">
          {messages.length === 0 ? (
            /* Center Welcome Text */
            <div className="w-full max-w-3xl px-4 flex flex-col items-center justify-center h-full -mt-20">
              <h1 className="text-4xl md:text-5xl font-medium text-white mb-10 text-center tracking-tight">
                LLM Scan For Misbehaviour Detection
              </h1>
              {inputForm}
            </div>
          ) : (
            /* Chat History */
            <div className="w-full max-w-3xl px-4 py-8 flex flex-col gap-8">
              {messages.map((msg, index) => (
                <div key={index} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {msg.role === 'user' ? (
                    <div className="bg-[#282a2d] text-white px-5 py-3 rounded-[1.5rem] max-w-[85%] text-[15px] leading-relaxed">
                      {msg.content}
                    </div>
                  ) : (
                    <div className="flex flex-col gap-3 w-full">
                      <div className="text-gray-100 text-[15px] leading-relaxed whitespace-pre-wrap">
                        {msg.content}
                      </div>
                      {/* Action Icons Removed */}
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex flex-col items-start mt-2">
                  <div className="text-gray-400 italic text-[15px] animate-pulse">
                    Scanning and generating response...
                  </div>
                </div>
              )}
              <div className="h-40 flex-shrink-0 w-full" ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        {messages.length > 0 && (
          <div className="w-full max-w-3xl px-4 pb-6 pt-2 bg-gradient-to-t from-[#0f1218] via-[#0f1218] to-transparent absolute bottom-0 left-1/2 -translate-x-1/2">
            {inputForm}
          </div>
        )}
      </main>

      {/* Sliding Scanner Drawer */}
      <div
        ref={scannerRef}
        className={`fixed top-0 right-0 h-full bg-[#18191b] border-l border-white/10 shadow-2xl z-50 flex flex-col ${isScannerResizing ? '' : 'transition-all duration-300 ease-in-out'
          } ${isScannerOpen ? 'translate-x-0' : 'translate-x-full pointer-events-none'}`}
        style={{ width: isScannerOpen ? scannerWidth : 0 }}
      >
        {/* Resizer Handle */}
        {isScannerOpen && (
          <div
            className="absolute left-0 top-0 bottom-0 w-1.5 cursor-col-resize hover:bg-blue-500/50 active:bg-blue-500 transition-colors z-50"
            onMouseDown={startScannerResizing}
          />
        )}
        {/* Drawer Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-[#1e1f22] flex-shrink-0">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">LLM Scan Analysis</h2>
          </div>
          <button
            onClick={() => setIsScannerOpen(false)}
            className="p-1.5 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Content */}
        {scannedPrompts.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-[#131314]">
            <img src="/scanner.png" alt="Scanner" className="w-16 h-16 object-contain mb-4 opacity-40 animate-pulse" />
            <p className="text-lg font-medium text-gray-300">No Prompts Scanned Yet</p>
            <p className="text-sm text-gray-500 max-w-sm mt-2">
              Send a prompt to Mistral 7B in the chat window, then open the scanner to view its causal importance graphs.
            </p>
          </div>
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Sliding Sideways Selector */}
            <div className="flex items-center justify-between px-6 py-3 bg-[#1e1f22] border-b border-white/5 flex-shrink-0">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                Analysis Carousel
              </span>
              <div className="flex items-center gap-3">
                <button
                  disabled={currentScanIndex === 0}
                  onClick={() => setCurrentScanIndex(prev => Math.max(0, prev - 1))}
                  className="flex items-center gap-1 px-3 py-1 rounded bg-[#282a2d] hover:bg-[#34373a] disabled:opacity-20 disabled:hover:bg-[#282a2d] text-xs font-medium text-gray-300 transition-colors"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  Prev
                </button>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  {currentScanIndex + 1} of {scannedPrompts.length}
                </span>
                <button
                  disabled={currentScanIndex === scannedPrompts.length - 1}
                  onClick={() => setCurrentScanIndex(prev => Math.min(scannedPrompts.length - 1, prev + 1))}
                  className="flex items-center gap-1 px-3 py-1 rounded bg-[#282a2d] hover:bg-[#34373a] disabled:opacity-20 disabled:hover:bg-[#282a2d] text-xs font-medium text-gray-300 transition-colors"
                >
                  Next
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Prompt details */}
            <div className="px-6 py-4 bg-[#1b1c1e] border-b border-white/5 flex-shrink-0">
              <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Scanned Prompt</p>
              <p className="text-sm font-medium text-white italic line-clamp-2">
                "{scannedPrompts[currentScanIndex]}"
              </p>
            </div>

            {/* Streamlit Graph iFrame Container */}
            <div className="flex-1 w-full bg-[#131314] overflow-hidden relative">
              <iframe
                key={currentScanIndex}
                src={`${STREAMLIT_BASE_URL}/?prompt=${encodeURIComponent(scannedPrompts[currentScanIndex])}&token=${encodeURIComponent((session as any)?.accessToken || '')}`}
                className="w-full h-full border-none bg-[#131314]"
                title="LLM Scan Graph Dashboard"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
