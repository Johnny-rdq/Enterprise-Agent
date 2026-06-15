import { marked } from 'marked';
import DOMPurify from 'dompurify';

function renderMarkdown(text) {
  if (!text) return '';
  return DOMPurify.sanitize(marked.parse(text));
}

function getLastStatusLine(text) {
  if (!text) return '';
  const lines = text.trim().split('\n');
  return lines[lines.length - 1].replace(/^[#*\-\s]+/, '').trim().substring(0, 40);
}

export default function ChatMessage({ role, intent, thinking, content, result, isStreaming, isError }) {
  const isUser = role === 'user';
  const hasIntent = intent && intent.length > 0;
  const hasContent = content && content.length > 0;
  const hasResult = result && result.length > 0;
  const isEmpty = !hasIntent && !hasContent && !hasResult;

  const statusLine = getLastStatusLine(thinking);

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-9 h-9 rounded-lg flex-shrink-0 flex items-center justify-center text-sm shadow-md ${
        isUser ? 'bg-indigo-500' : 'bg-blue-600'
      }`}>
        {isUser ? '我' : 'AI'}
      </div>
      <div className={`p-4 rounded-xl text-sm max-w-[85%] w-full shadow-sm break-words ${
        isUser
          ? 'bg-indigo-600 rounded-tr-none text-white max-w-[75%]'
          : isError
            ? 'bg-red-900/50 border border-red-800 rounded-tl-none text-red-200'
            : 'bg-gray-800 rounded-tl-none border border-gray-800 text-gray-200'
      }`}>
        {isUser ? (
          content
        ) : isStreaming && !hasContent && !hasResult ? (
          <div className="flex items-center gap-2">
            <svg className="animate-spin h-4 w-4 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span className="text-gray-400 text-xs">{statusLine || '正在处理...'}</span>
          </div>
        ) : !isStreaming && isEmpty && !isError ? (
          <span className="text-gray-400">思考中...</span>
        ) : (
          <div className="space-y-3">
            {hasIntent && (
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-900/50 border border-indigo-700/50 text-indigo-300 text-xs animate-pulse">
                <span className="w-2 h-2 rounded-full bg-indigo-400" />
                {intent}
              </div>
            )}
            {isStreaming && statusLine && (
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <svg className="animate-spin h-3 w-3 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                {statusLine}
              </div>
            )}
            {hasContent && (
              isStreaming ? (
                <div className="text-gray-200 whitespace-pre-wrap">{content}</div>
              ) : (
                <div
                  className="markdown-body"
                  dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
                />
              )
            )}
            {hasResult && (
              <div className={`p-3 rounded-lg border whitespace-pre-wrap ${
                isError
                  ? 'bg-red-900/30 border-red-800 text-red-200'
                  : result.includes('失败') || result.includes('错误') || result.includes('❌')
                    ? 'bg-red-900/20 border-red-800/50 text-red-200'
                    : 'bg-emerald-900/20 border-emerald-800 text-gray-200'
              }`}>
                {isStreaming ? result : <div className="markdown-body text-sm" dangerouslySetInnerHTML={{ __html: renderMarkdown(result) }} />}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
