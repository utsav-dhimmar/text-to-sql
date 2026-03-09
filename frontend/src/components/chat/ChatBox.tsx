import { useState, useEffect, useRef } from "react";
import { useAppDispatch, useAppSelector } from "../../store";
import {
    fetchChatHistory,
    sendChatMessage,
    addOptimisticUserMessage,
} from "../../store/slices/chatSlice";
import { Button } from "../ui";
import { Send, Loader2 } from "lucide-react";

export const ChatBox = () => {
    const dispatch = useAppDispatch();
    const { messages, loading, error } = useAppSelector((state) => state.chat);
    const [inputValue, setInputValue] = useState("");
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        dispatch(fetchChatHistory());
    }, [dispatch]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputValue.trim() || loading) return;

        // Dispatch optimistic update
        dispatch(addOptimisticUserMessage(inputValue));

        // Dispatch actual request
        dispatch(sendChatMessage(inputValue));
        setInputValue("");
    };

    return (
        <div className="flex flex-col h-[600px] border dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-gray-900 overflow-hidden shadow-lg mt-8">
            {/* Header */}
            <div className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 p-4">
                <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-100 items-center gap-2 flex">
                    SQL Assistant
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Ask questions about your data</p>
            </div>

            {/* Messages Area */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4">
                {messages.length === 0 && !loading && (
                    <div className="text-center text-gray-500 dark:text-gray-400 mt-10">
                        No messages yet. Start a conversation!
                    </div>
                )}

                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex flex-col max-w-[80%] ${msg.role === "user" ? "ml-auto items-end" : "mr-auto items-start"
                            }`}
                    >
                        <div
                            className={`px-4 py-2 rounded-2xl shadow-sm text-sm ${msg.role === "user"
                                    ? "bg-blue-600 text-white rounded-br-none"
                                    : "bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 border dark:border-gray-700 rounded-bl-none"
                                }`}
                        >
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                            {msg.sql_generated && (
                                <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700 text-xs font-mono overflow-x-auto text-gray-700 dark:text-gray-300">
                                    {msg.sql_generated}
                                </div>
                            )}
                        </div>
                        <span className="text-xs text-gray-400 mt-1">
                            {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                    </div>
                ))}
                {loading && (
                    <div className="flex items-center gap-2 text-gray-500 mr-auto p-2">
                        <Loader2 className="animate-spin w-4 h-4" />
                        <span className="text-sm">Thinking...</span>
                    </div>
                )}
                {error && (
                    <div className="text-red-500 text-sm p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg mx-auto text-center w-[80%]">
                        Error: {error}
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white dark:bg-gray-800 border-t dark:border-gray-700">
                <form onSubmit={handleSubmit} className="flex gap-2 relative">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Type your query here..."
                        className="flex-1 resize-none overflow-hidden rounded-full border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100 disabled:opacity-50"
                        disabled={loading}
                    />
                    <Button
                        type="submit"
                        disabled={loading || !inputValue.trim()}
                        className="rounded-full w-12 h-12 flex items-center justify-center !p-0 shrink-0 shadow-md bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white"
                        fullWidth={false}
                    >
                        <Send size={18} className={`${loading ? 'opacity-50' : 'opacity-100'} ml-1`} />
                    </Button>
                </form>
            </div>
        </div>
    );
};
