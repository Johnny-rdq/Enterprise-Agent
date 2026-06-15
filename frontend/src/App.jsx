import { useState, useCallback, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import { useSessions } from './hooks/useSessions';

const AUTH_TOKEN = 'demo_token';

export default function App() {
  const { sessions, currentId, create, switchTo, remove, updateTitle } = useSessions();
  const [chatHistory, setChatHistory] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const abortRef = useRef(null);

  const loadHistory = useCallback(async (threadId) => {
    try {
      const res = await fetch(`/get_chat_history?thread_id=${threadId}`);
      const data = await res.json();
      setChatHistory(data.history || []);
    } catch {
      setChatHistory([]);
    }
  }, []);

  useEffect(() => {
    if (currentId) {
      loadHistory(currentId);
    }
  }, [currentId, loadHistory]);

  const stopStreaming = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setIsStreaming(false);
    setChatHistory(prev => {
      if (prev.length === 0) return prev;
      return prev.map((item, index) => {
        if (index === prev.length - 1 && item.isStreaming) {
          return { ...item, isStreaming: false, intent: '', content: (item.content || '') + '\n\n---\n\n⏹️ **已取消**' };
        }
        return item;
      });
    });
  }, []);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isStreaming) return;

    const userMsg = { role: 'user', content: text };
    setChatHistory(prev => [...prev, userMsg]);
    setIsStreaming(true);

    if (currentId) {
      const s = sessions.find(s => s.id === currentId);
      if (s && s.title.startsWith('新会话')) {
        updateTitle(currentId, text.length > 15 ? text.substring(0, 15) + '...' : text);
      }
    }

    const aiMsg = { role: 'assistant', intent: '', thinking: '', content: '', result: '', isStreaming: true };
    setChatHistory(prev => [...prev, aiMsg]);

    const controller = new AbortController();
    abortRef.current = controller;

    let intentTimer = null;

    try {
      const res = await fetch('/agentrun', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: text, token: AUTH_TOKEN, thread_id: currentId }),
        signal: controller.signal,
      });

      if (!res.ok) {
        throw new Error(`服务器拒绝服务: ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let accIntent = '';
      let accThinking = '';
      let accContent = '';
      let accResult = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const messages = buffer.split('\n\n');
        buffer = messages.pop() || '';

        for (const msg of messages) {
          if (msg.trim() === 'data: [DONE]') break;
          if (msg.startsWith('data: ')) {
            const dataStr = msg.substring(6);
            try {
              const data = JSON.parse(dataStr);
              const msgType = data.type;
              const msgContent = data.content || '';

              if (msgType === 'intent') {
                accIntent += msgContent;
                if (intentTimer) clearTimeout(intentTimer);
                setChatHistory(prev => prev.map((item, index) => {
                  if (index === prev.length - 1) return { ...item, intent: accIntent };
                  return item;
                }));
                intentTimer = setTimeout(() => {
                  setChatHistory(prev => prev.map((item, index) => {
                    if (index === prev.length - 1) return { ...item, intent: '' };
                    return item;
                  }));
                }, 3000);
              } else if (msgType === 'thinking') {
                accThinking += msgContent;
                setChatHistory(prev => prev.map((item, index) => {
                  if (index === prev.length - 1) return { ...item, thinking: accThinking };
                  return item;
                }));
              } else if (msgType === 'token') {
                accContent += msgContent;
                setChatHistory(prev => prev.map((item, index) => {
                  if (index === prev.length - 1) return { ...item, content: accContent };
                  return item;
                }));
              } else if (msgType === 'result') {
                accResult += msgContent;
                setChatHistory(prev => prev.map((item, index) => {
                  if (index === prev.length - 1) return { ...item, result: accResult };
                  return item;
                }));
              }
            } catch { /* 容错残缺碎片 */ }
          }
        }
      }

      if (intentTimer) clearTimeout(intentTimer);
      setChatHistory(prev => {
        return prev.map((item, index) => {
          if (index === prev.length - 1) {
            return { role: 'assistant', intent: '', thinking: accThinking, content: accContent, result: accResult, isStreaming: false };
          }
          return item;
        });
      });

    } catch (e) {
      if (e.name === 'AbortError') return;
      if (intentTimer) clearTimeout(intentTimer);
      setChatHistory(prev => {
        return prev.map((item, index) => {
          if (index === prev.length - 1) {
            return { role: 'assistant', intent: '', thinking: accThinking, content: accContent, result: `异常: ${e.message}`, isError: true };
          }
          return item;
        });
      });
    } finally {
      abortRef.current = null;
      setIsStreaming(false);
    }
  }, [currentId, isStreaming, sessions, updateTitle]);

  const handleSwitch = useCallback((id) => {
    switchTo(id);
    loadHistory(id);
  }, [switchTo, loadHistory]);

  const handleCreate = useCallback(() => {
    const id = create();
    setChatHistory([]);
    loadHistory(id);
  }, [create, loadHistory]);

  const currentTitle = sessions.find(s => s.id === currentId)?.title || 'AI 智能体协作平台';

  return (
    <div className="flex h-dvh overflow-hidden">
      {sidebarOpen && (
        <Sidebar sessions={sessions} currentId={currentId} onSwitch={handleSwitch} onCreate={handleCreate} onDelete={remove} onToggle={() => setSidebarOpen(false)} />
      )}
      <ChatArea title={currentTitle} messages={chatHistory} isStreaming={isStreaming} onSend={sendMessage} onStop={stopStreaming} welcomeMsg="👋 欢迎使用 AI 智能体协作平台！试试问我：'什么是AI？' 或 '写一个贪吃蛇游戏'" sidebarOpen={sidebarOpen} onToggleSidebar={() => setSidebarOpen(v => !v)} />
    </div>
  );
}
