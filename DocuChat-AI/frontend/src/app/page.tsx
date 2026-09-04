"use client";

  import { ChangeEvent, FormEvent, useEffect, useRef, useState } from "react";
  import { ArrowUp, FileText, FolderOpen, LoaderCircle, Plus, Search, Sparkles, X } from "lucide-react";

  type DocumentItem = { id: string; filename: string; pages: number; chunks: number };
  type Message = { role: "user" | "assistant"; content: string; sources?: { filename: string; page: number }[] };
  const API_URL = process.env.NEXT_API_URL ?? "http://localhost:8000";

  export default function Home() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [activeDocument, setActiveDocument] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [notice, setNotice] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  async function loadDocuments() { try { const response = await fetch(`${API_URL}/documents`); if (response.ok) setDocuments(await response.json()); } catch { setNotice("Backend offline. Start FastAPI on port 8000."); } }
  useEffect(() => {
    let cancelled = false;
    fetch(`${API_URL}/documents`).then(async (response) => { if (response.ok && !cancelled) setDocuments(await response.json()); }).catch(() => { if (!cancelled) setNotice("Backend offline. Start FastAPI on port 8000."); });
    return () => { cancelled = true; };
  }, []);
  async function upload(file: File) {
    setUploading(true); setNotice(""); const body = new FormData(); body.append("file", file);
    try { const response = await fetch(`${API_URL}/upload`, { method: "POST", body }); const data = await response.json(); if (!response.ok) throw new Error(data.detail ?? "Upload failed"); await loadDocuments(); setActiveDocument(data.id); setMessages([{ role: "assistant", content: `I am ready to answer questions about ${data.filename}. Ask me anything about its ${data.pages} pages.` }]); }
    catch (error) { setNotice(error instanceof Error ? error.message : "Upload failed"); } finally { setUploading(false); }
  }
  function handleFile(event: ChangeEvent<HTMLInputElement>) { const file = event.target.files?.[0]; if (file) void upload(file); event.target.value = ""; }
  async function ask(event: FormEvent) {
    event.preventDefault(); if (!question.trim() || asking || !documents.length) return; const currentQuestion = question.trim(); setQuestion(""); setMessages((current) => [...current, { role: "user", content: currentQuestion }]); setAsking(true); setNotice("");
    try { const response = await fetch(`${API_URL}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: currentQuestion, document_id: activeDocument }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail ?? "Could not answer"); setMessages((current) => [...current, { role: "assistant", content: data.answer, sources: data.sources }]); }
    catch (error) { setNotice(error instanceof Error ? error.message : "Could not answer"); } finally { setAsking(false); }
  }
  const activeName = documents.find((document) => document.id === activeDocument)?.filename;

  return <main className="app-shell">
    <aside className="sidebar"><div className="brand"><span className="brand-mark"><Sparkles size={17} /></span><span>docuchat</span><span className="brand-dot">.</span></div><button className="upload-button" onClick={() => fileInput.current?.click()} disabled={uploading}><Plus size={18} />{uploading ? "Indexing..." : "Add document"}</button><input ref={fileInput} className="visually-hidden" type="file" accept="application/pdf" onChange={handleFile} /><div className="library-heading"><span>Your library</span><span>{documents.length}</span></div><div className="document-list">{documents.map((document) => <button key={document.id} className={`document-item ${document.id === activeDocument ? "selected" : ""}`} onClick={() => setActiveDocument(document.id)}><FileText size={18} /><span className="document-name">{document.filename}</span><span className="document-pages">{document.pages}p</span></button>)}{!documents.length && <div className="empty-library"><FolderOpen size={22} /><span>No documents yet</span><small>Upload a PDF to begin</small></div>}</div><div className="sidebar-foot"><span className="status-dot" /> Local workspace <span className="secure">Private</span></div></aside>
    <section className="workspace"><header className="topbar"><div><span className="eyebrow">DOCUMENT INTELLIGENCE</span><h1>Ask your documents</h1></div><div className="topbar-actions"><span className="connection"><span className="status-dot" /> Connected</span><button className="icon-button" title="Search library"><Search size={18} /></button></div></header><div className="content"><div className="conversation-head"><div><p className="kicker">CURRENT CONVERSATION</p><h2>{activeName ?? "A clearer way to read"}</h2></div>{messages.length > 0 && <button className="clear-button" onClick={() => setMessages([])}><X size={15} /> Clear chat</button>}</div><div className="chat-area">{!messages.length ? <div className="welcome"><div className="welcome-icon"><Sparkles size={24} /></div><h3>What would you like to understand?</h3><p>Upload a PDF, then ask questions in plain language. Answers are grounded in the passages your document contains.</p><div className="suggestions"><button onClick={() => setQuestion("Summarize this document")}>Summarize this document <ArrowUp size={14} /></button><button onClick={() => setQuestion("What are the key takeaways?")}>What are the key takeaways? <ArrowUp size={14} /></button></div></div> : messages.map((message, index) => <div className={`message-row ${message.role}`} key={`${message.role}-${index}`}><div className="avatar">{message.role === "assistant" ? <Sparkles size={15} /> : "You"}</div><div className="message"><p>{message.content}</p>{message.sources?.length ? <div className="sources"><span>Sources</span>{message.sources.map((source, sourceIndex) => <span className="source" key={`${source.filename}-${sourceIndex}`}><FileText size={12} /> {source.filename} · p. {source.page}</span>)}</div> : null}</div></div>)}{asking && <div className="message-row assistant"><div className="avatar"><Sparkles size={15} /></div><div className="message thinking"><LoaderCircle size={17} /> Searching your document...</div></div>}</div>{notice && <div className="notice">{notice}</div>}<form className="composer" onSubmit={ask}><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={documents.length ? "Ask anything about your documents..." : "Upload a PDF to start chatting"} disabled={!documents.length || asking} /><button type="submit" title="Send question" disabled={!question.trim() || asking || !documents.length}><ArrowUp size={19} /></button></form><p className="disclaimer">DocuChat uses semantic search to find relevant passages. Always verify important details.</p></div></section>
  </main>;
  }
