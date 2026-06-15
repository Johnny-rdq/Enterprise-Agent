import { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import MessageInput from './MessageInput';

export default function ChatArea({ title, messages, isStreaming, onSend, onStop, welcomeMsg, sidebarOpen, onToggleSidebar }) {
  const containerRef = useRef(null);
  const userScrolledUpRef = useRef(false);

  const isNearBottom = () => {
    const el = containerRef.current;
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < 80;
  };

  const handleScroll = () => {
    userScrolledUpRef.current = !isNearBottom();
  };

  useEffect(() => {
    if (containerRef.current && !userScrolledUpRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section className="flex-1 flex flex-col justify-between bg-gray-900 relative">
      <header className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 p-4 flex items-center">
        {!sidebarOpen && (
          <button
            onClick={onToggleSidebar}
            className="mr-3 w-8 h-8 rounded-lg bg-gray-800 hover:bg-gray-700 flex items-center justify-center text-gray-400 hover:text-gray-200 transition-all active:scale-90 flex-shrink-0"
            title="展开侧边栏"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
        )}
        <div className="flex items-center gap-3">
          <span className="text-2xl">🧠</span>
          <div>
            <h1 className="text-base font-bold tracking-wide">{title}</h1>
            <p className="text-xs text-gray-400">四 Agent 协作管线 — 规划 → 调研 → 编码 → 审查</p>
          </div>
        </div>
      </header>

      <main
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 min-h-0 overflow-y-auto p-4 md:p-8 flex flex-col gap-6 w-full max-w-4xl mx-auto scroll-smooth"
      >
        {messages.length === 0 ? (
          <div className="flex gap-4">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex-shrink-0 flex items-center justify-center text-sm">AI</div>
            <div className="bg-gray-800 p-4 rounded-xl rounded-tl-none border border-gray-800 text-sm text-gray-200 shadow-sm">
              {welcomeMsg}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <ChatMessage key={i} role={msg.role} intent={msg.intent} thinking={msg.thinking} content={msg.content} result={msg.result} isStreaming={msg.isStreaming} isError={msg.isError} />
          ))
        )}
      </main>

      <MessageInput onSend={onSend} disabled={isStreaming} onStop={onStop} isStreaming={isStreaming} />
    </section>
  );
}
