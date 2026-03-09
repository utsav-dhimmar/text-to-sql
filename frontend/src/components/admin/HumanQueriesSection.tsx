import { ChevronRight, MessageSquare } from "lucide-react";
import type { ChatHistoryResponse } from "../../apis/types";

interface HumanQueriesSectionProps {
  chats: ChatHistoryResponse[];
  selectedChat: ChatHistoryResponse | null;
  onSelectChat: (chat: ChatHistoryResponse) => void;
}

export function HumanQueriesSection({
  chats,
  selectedChat,
  onSelectChat,
}: HumanQueriesSectionProps) {
  return (
    <div className="grid grid-rows-[1fr,1fr] gap-6 h-[640px]">
      <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden flex flex-col">
        <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-center bg-gray-50/50 dark:bg-zinc-900/50">
          <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
            <MessageSquare className="text-indigo-500" size={20} />
            Human Queries
          </h2>
          <span className="text-sm text-gray-500 dark:text-zinc-400">
            {chats.length} Queries
          </span>
        </div>
        <div className="overflow-y-auto flex-1">
          <div className="divide-y divide-gray-200 dark:divide-zinc-800">
            {chats.map((chat) => (
              <button
                key={chat.id}
                onClick={() => onSelectChat(chat)}
                className={`w-full text-left p-4 hover:bg-gray-50 dark:hover:bg-zinc-800/30 transition-all flex items-start justify-between group ${
                  selectedChat?.id === chat.id
                    ? "bg-indigo-50/50 dark:bg-indigo-900/10 border-l-4 border-indigo-500"
                    : "border-l-4 border-transparent"
                }`}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-zinc-200 line-clamp-1">
                    {chat.human_query}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-zinc-500 mt-1">
                    {new Date(chat.created_at).toLocaleString()}
                  </p>
                </div>
                <ChevronRight
                  className={`text-gray-400 group-hover:translate-x-1 transition-transform ${
                    selectedChat?.id === chat.id
                      ? "text-indigo-500 translate-x-1"
                      : ""
                  }`}
                  size={16}
                />
              </button>
            ))}
          </div>
        </div>
      </div>

      <div
        className={`bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden transition-all duration-300 ${
          selectedChat
            ? "opacity-100 translate-y-0"
            : "opacity-50 translate-y-4 pointer-events-none"
        }`}
      >
        <div className="p-6 h-full overflow-y-auto">
          <h3 className="text-lg font-bold dark:text-white mb-4 flex items-center gap-2">
            <div className="w-2 h-6 bg-indigo-500 rounded-full"></div>
            Generated AI Query
          </h3>
          {selectedChat ? (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 dark:bg-zinc-800 rounded-lg border border-gray-200 dark:border-zinc-700">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                  Human Question
                </p>
                <p className="text-sm text-gray-700 dark:text-zinc-300 italic">
                  "{selectedChat.human_query}"
                </p>
              </div>
              <div className="p-4 bg-zinc-900 dark:bg-black rounded-lg border border-zinc-700 overflow-x-auto">
                <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">
                  Generated SQL
                </p>
                <pre className="text-sm text-emerald-400 font-mono leading-relaxed">
                  {selectedChat.sql_generated || "-- No SQL generated"}
                </pre>
              </div>
              {selectedChat.result_summary && (
                <div className="p-4 bg-gray-50 dark:bg-zinc-800 rounded-lg border border-gray-200 dark:border-zinc-700">
                  <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                    Summary Result
                  </p>
                  <p className="text-sm text-gray-700 dark:text-zinc-300">
                    {selectedChat.result_summary}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="py-12 flex flex-col items-center justify-center text-gray-400 dark:text-zinc-600">
              <MessageSquare
                size={48}
                strokeWidth={1}
                className="mb-4 opacity-20"
              />
              <p>Select a query to see the details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
