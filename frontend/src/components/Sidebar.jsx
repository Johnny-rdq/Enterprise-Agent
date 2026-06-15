export default function Sidebar({ sessions, currentId, onSwitch, onCreate, onDelete, onToggle }) {
  return (
    <aside className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col justify-between flex-shrink-0">
      <div className="p-3 flex flex-col gap-4 overflow-hidden h-full">
        <div className="flex items-center gap-2">
          <button
            onClick={onCreate}
            className="flex-1 border border-gray-700 hover:border-blue-500 hover:bg-gray-900 text-sm font-medium py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all active:scale-95"
          >
            <span>+</span> 新建会话
          </button>
          <button
            onClick={onToggle}
            className="w-9 h-9 rounded-lg bg-gray-800 hover:bg-gray-700 flex items-center justify-center text-gray-500 hover:text-gray-300 transition-all active:scale-90 flex-shrink-0"
            title="收起侧边栏"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" /></svg>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto flex flex-col gap-1 pr-1">
          {sessions.map(s => {
            const isActive = s.id === currentId;
            return (
              <button
                key={s.id}
                onClick={() => onSwitch(s.id)}
                className={`w-full text-left text-sm py-3 px-4 rounded-xl flex items-center justify-between transition-all group ${
                  isActive
                    ? 'bg-gray-800 text-blue-400 font-medium border border-gray-700'
                    : 'text-gray-400 hover:bg-gray-900/50 hover:text-gray-200'
                }`}
              >
                <span className="flex items-center gap-2 truncate flex-1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} className="flex-shrink-0"><path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                  <span className="truncate">{s.title}</span>
                </span>
                <span
                  onClick={(e) => { e.stopPropagation(); onDelete(s.id); }}
                  className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 px-1 transition-all"
                >
                  ×
                </span>
              </button>
            );
          })}
        </div>
      </div>
      <div className="p-4 border-t border-gray-800 bg-gray-950/50 text-xs text-gray-500 text-center flex items-center justify-center gap-1.5">
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>
        AI 智能体协作平台
      </div>
    </aside>
  );
}
