"use client";

import { useState, useRef, useEffect } from "react";
import { Search, Loader2, Sparkles, BookOpen, ExternalLink, User, MessageSquare, Send, X, ArrowRight, Code, ArrowUpRight, Clock, Award } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Paper {
  id: string;
  title: string;
  publication_year: number;
  publication_date: string;
  doi: string;
  authors: string[];
  abstract: string | null;
  journal: string | null;
  cited_by_count: number;
  pdf_url: string | null;
  topics: string[];
  is_open_access: boolean;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [summarizingId, setSummarizingId] = useState<string | null>(null);
  const [summaries, setSummaries] = useState<Record<string, string>>({});
  
  // Chat state
  const [activeChat, setActiveChat] = useState<Paper | null>(null);
  const [chatHistory, setChatHistory] = useState<{role: string, content: string}[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isProcessingPdf, setIsProcessingPdf] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    
    setHasSearched(true);
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_API_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${apiUrl}/papers/?query=${encodeURIComponent(query)}&limit=10`);
      const data = await res.json();
      setPapers(data.papers || []);
    } catch (error) {
      console.error("Error fetching papers:", error);
    }
    setLoading(false);
  };

  const handleSummarize = async (paper: Paper) => {
    if (!paper.abstract) return;
    
    setSummarizingId(paper.id);
    try {
      const apiUrl = process.env.NEXT_API_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${apiUrl}/papers/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: paper.title, abstract: paper.abstract }),
      });
      const data = await res.json();
      setSummaries((prev) => ({ ...prev, [paper.id]: data.summary }));
    } catch (error) {
      console.error("Error summarizing paper:", error);
    }
    setSummarizingId(null);
  };

  const handleOpenChat = async (paper: Paper) => {
    setActiveChat(paper);
    setChatHistory([{
      role: "assistant",
      content: `Hi! I'm your AI Research Assistant. I'm ready to answer questions about "${paper.title}". What would you like to know?`
    }]);

    if (!paper.pdf_url) {
        setChatHistory(prev => [...prev, {role: "assistant", content: "I cannot chat with this paper because there is no open-access PDF available."}]);
        return;
    }

    setIsProcessingPdf(true);
    try {
      const apiUrl = process.env.NEXT_API_URL || 'http://127.0.0.1:8000';
      await fetch(`${apiUrl}/process_pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paper_id: paper.id, pdf_url: paper.pdf_url }),
      });
    } catch (error) {
      console.error("Error processing PDF:", error);
      setChatHistory(prev => [...prev, {role: "assistant", content: "There was an error processing the PDF. Please try again later."}]);
    }
    setIsProcessingPdf(false);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || !activeChat || isProcessingPdf || isChatting) return;

    const question = chatInput.trim();
    setChatInput("");
    setChatHistory(prev => [...prev, { role: "user", content: question }]);
    setIsChatting(true);

    try {
      const apiUrl = process.env.NEXT_API_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paper_id: activeChat.id, question }),
      });
      const data = await res.json();
      setChatHistory(prev => [...prev, { role: "assistant", content: data.answer }]);
    } catch (error) {
      console.error("Error chatting:", error);
      setChatHistory(prev => [...prev, { role: "assistant", content: "Sorry, I encountered an error answering your question." }]);
    }
    setIsChatting(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 overflow-x-hidden">
      {/* Enhanced background effects */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-blue-600/5 rounded-full blur-[120px]" />
      </div>

      <div className="relative z-10">
        {/* Navigation Header */}
        <nav className="border-b border-slate-800/50 backdrop-blur-md bg-slate-900/30">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-2"
            >
              <div className="p-2 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg text-white">ResearchAI</span>
            </motion.div>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors text-sm text-slate-300"
            >
              <Code className="w-4 h-4" />
              View on GitHub
            </a>
          </div>
        </nav>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto px-6 py-16">
          
          {/* Header Section */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-sm font-medium text-indigo-300 backdrop-blur-sm">
              <Sparkles size={16} />
              <span>Powered by Groq AI</span>
              <ArrowRight size={14} />
            </div>
            <h1 className="text-6xl md:text-7xl font-bold tracking-tighter mb-6 leading-tight">
              <span className="bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">
                Explore Research Papers
              </span>
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
                with AI Insights
              </span>
            </h1>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed">
              Discover, analyze, and chat with academic papers. Get instant AI-powered summaries and deep insights from research documents with natural language conversations.
            </p>
          </motion.div>

          {/* Search Form */}
          <motion.form 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            onSubmit={handleSearch} 
            className="relative max-w-4xl mx-auto mb-20"
          >
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-500" />
              <div className="relative flex items-center bg-slate-900 border border-slate-700/50 rounded-2xl p-3 backdrop-blur-xl">
                <Search className="w-6 h-6 text-slate-500 ml-4" />
                <input
                  type="text"
                  placeholder="Search papers, topics, authors..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full bg-transparent text-lg text-white px-6 py-4 outline-none placeholder:text-slate-500"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="px-8 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-600 hover:to-purple-700 transition-all disabled:opacity-50 mr-2 flex items-center gap-2 shadow-lg shadow-indigo-500/30"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Search"}
                </button>
              </div>
            </div>
          </motion.form>

          {/* Results Section */}
          {loading ? (
            <div className="flex justify-center items-center py-20">
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
                <p className="text-slate-400">Searching academic database...</p>
              </div>
            </div>
          ) : papers.length > 0 ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-bold text-white">
                  Found <span className="text-indigo-400">{papers.length}</span> papers
                </h2>
              </div>
              <AnimatePresence>
                {papers.map((paper, index) => (
                  <motion.div
                    key={paper.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.08 }}
                    className="group relative"
                  >
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-300" />
                    <div className="relative bg-slate-800/40 border border-slate-700/50 backdrop-blur-xl rounded-2xl p-6 md:p-8 hover:bg-slate-800/60 transition-all">
                      <div className="grid md:grid-cols-3 gap-6 mb-6">
                        <div className="md:col-span-2 space-y-4">
                          <h2 className="text-xl md:text-2xl font-bold leading-tight text-white group-hover:text-indigo-300 transition-colors">
                            {paper.title}
                          </h2>
                          
                          <div className="space-y-3">
                            <div className="flex flex-wrap items-center gap-4 text-sm text-slate-400">
                              <div className="flex items-center gap-2">
                                <User className="w-4 h-4 text-slate-500" />
                                <span className="truncate max-w-[300px]">
                                  {paper.authors.length > 0 ? paper.authors.slice(0, 2).join(", ") : "Unknown"}
                                  {paper.authors.length > 2 ? ` +${paper.authors.length - 2}` : ""}
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <BookOpen className="w-4 h-4 text-slate-500" />
                                <span>{paper.journal || "Journal"}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Clock className="w-4 h-4 text-slate-500" />
                                <span>{paper.publication_year}</span>
                              </div>
                              {paper.cited_by_count > 0 && (
                                <div className="flex items-center gap-2">
                                  <Award className="w-4 h-4 text-slate-500" />
                                  <span>{paper.cited_by_count} citations</span>
                                </div>
                              )}
                            </div>

                            <div className="flex flex-wrap gap-2">
                              {paper.topics.slice(0, 3).map((topic, i) => (
                                <span key={i} className="px-3 py-1 rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-xs font-medium hover:bg-indigo-500/20 transition-colors">
                                  {topic}
                                </span>
                              ))}
                              {paper.topics.length > 3 && (
                                <span className="px-3 py-1 rounded-lg bg-slate-600/20 text-slate-400 text-xs">
                                  +{paper.topics.length - 3} more
                                </span>
                              )}
                            </div>

                            {paper.abstract && (
                              <p className="text-slate-300 line-clamp-2 text-sm leading-relaxed">
                                {paper.abstract}
                              </p>
                            )}
                          </div>
                        </div>

                        <div className="flex flex-col gap-3">
                          <button
                            onClick={() => handleSummarize(paper)}
                            disabled={summarizingId === paper.id || !paper.abstract}
                            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold hover:from-indigo-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shadow-lg shadow-indigo-500/25"
                          >
                            {summarizingId === paper.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Sparkles className="w-4 h-4" />
                            )}
                            AI Summary
                          </button>
                          {paper.pdf_url && (
                            <button
                              onClick={() => handleOpenChat(paper)}
                              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-semibold transition-all cursor-pointer"
                            >
                              <MessageSquare className="w-4 h-4" />
                              Chat w/ Paper
                            </button>
                          )}
                          {paper.pdf_url && (
                            <a
                              href={paper.pdf_url}
                              target="_blank"
                              rel="noreferrer"
                              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-white font-semibold border border-slate-600/50 transition-all"
                            >
                              <ExternalLink className="w-4 h-4" />
                              PDF
                            </a>
                          )}
                        </div>
                      </div>

                      {/* AI Summary Section */}
                      <AnimatePresence>
                        {summaries[paper.id] && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            className="border-t border-slate-700/50 pt-6 mt-6"
                          >
                            <div className="flex gap-4 p-4 rounded-xl bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/20">
                              <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-300 flex-shrink-0">
                                <Sparkles className="w-5 h-5" />
                              </div>
                              <div className="flex-1">
                                <h4 className="text-sm font-semibold text-indigo-300 mb-2">AI Analysis</h4>
                                <p className="text-slate-300 leading-relaxed text-sm">
                                  {summaries[paper.id]}
                                </p>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>

                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          ) : hasSearched ? (
            <div className="text-center py-20">
              <BookOpen className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-300 mb-2">No papers found</h3>
              <p className="text-slate-400">Try different keywords or search terms</p>
            </div>
          ) : (
            <div className="text-center py-20">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                <Search className="w-16 h-16 text-slate-600 mx-auto opacity-50" />
                <h3 className="text-2xl font-bold text-slate-300">Start Exploring</h3>
                <p className="text-slate-400 max-w-md mx-auto">
                  Search for research papers by topic, author, or keywords to get started
                </p>
              </motion.div>
            </div>
          )}
        </div>
      </div>

      {/* Chat Modal */}
      <AnimatePresence>
        {activeChat && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setActiveChat(null)}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          >
            <motion.div 
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-2xl bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700/50 rounded-2xl shadow-2xl flex flex-col overflow-hidden max-h-[80vh] backdrop-blur-xl"
            >
              {/* Chat Header */}
              <div className="flex items-center justify-between p-6 border-b border-slate-700/50 bg-slate-900/50">
                <div className="flex flex-col">
                  <h3 className="font-bold text-white text-lg">Chat with Paper</h3>
                  <p className="text-sm text-slate-400 truncate max-w-md">{activeChat.title}</p>
                </div>
                <button 
                  onClick={() => setActiveChat(null)}
                  className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-slate-200 transition-all"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Chat Messages */}
              <div 
                ref={chatScrollRef}
                className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-slate-900 to-slate-950"
              >
                {chatHistory.map((msg, idx) => (
                  <motion.div 
                    key={idx} 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div className={`max-w-[80%] rounded-2xl p-4 ${
                      msg.role === "user" 
                        ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-br-none shadow-lg shadow-indigo-500/20" 
                        : "bg-slate-800 text-slate-100 rounded-bl-none border border-slate-700/50"
                    }`}>
                      <p className="text-sm md:text-base leading-relaxed">{msg.content}</p>
                    </div>
                  </motion.div>
                ))}
                
                {isProcessingPdf && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-start"
                  >
                    <div className="bg-slate-800 border border-slate-700/50 text-slate-300 rounded-2xl rounded-bl-none p-4 flex items-center gap-3">
                      <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                      <span className="text-sm">Reading and analyzing PDF...</span>
                    </div>
                  </motion.div>
                )}
                {isChatting && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-start"
                  >
                    <div className="bg-slate-800 border border-slate-700/50 text-slate-300 rounded-2xl rounded-bl-none p-4 flex items-center gap-3">
                      <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                      <span className="text-sm">Thinking...</span>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Chat Input */}
              <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-700/50 bg-slate-900/50">
                <div className="relative flex items-center bg-slate-800/50 border border-slate-700 rounded-xl p-1 focus-within:border-indigo-500/50 transition-colors">
                  <input
                    type="text"
                    placeholder="Ask a question about this paper..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    disabled={isProcessingPdf || isChatting || !activeChat.pdf_url}
                    className="w-full bg-transparent text-white px-4 py-3 outline-none placeholder:text-slate-600 disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={!chatInput.trim() || isProcessingPdf || isChatting || !activeChat.pdf_url}
                    className="p-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed mr-1 shadow-lg shadow-indigo-500/20"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
