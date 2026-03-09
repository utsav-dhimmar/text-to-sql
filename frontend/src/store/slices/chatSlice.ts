import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";
import { ChatService, type ChatCreateData } from "../../apis/service/chat.service";
import type { ChatHistoryResponse } from "../../apis/types";

export interface ChatMessage {
    id: string;
    role: "user" | "assistant";
    content: string;
    sql_generated?: string;
    result_summary?: string;
    timestamp: string;
}

interface ChatState {
    messages: ChatMessage[];
    loading: boolean;
    error: string | null;
    sessionId: string;
}

const initialState: ChatState = {
    messages: [],
    loading: false,
    error: null,
    sessionId: "",
};

export const fetchChatHistory = createAsyncThunk(
    "chat/fetchHistory",
    async (_, { rejectWithValue }) => {
        try {
            const history = await ChatService.getHistory();
            return history;
        } catch (err: any) {
            return rejectWithValue(err.response?.data?.detail || "Failed to fetch chat history");
        }
    }
);

export const sendChatMessage = createAsyncThunk(
    "chat/sendMessage",
    async (query: string, { getState, rejectWithValue }) => {
        try {
            const state = getState() as { chat: ChatState };
            const currentSessionId = state.chat.sessionId;

            const data: ChatCreateData = {
                human_query: query,
                session_id: currentSessionId || undefined,
            };

            const response = await ChatService.queryChat(data);
            return { query, response };
        } catch (err: any) {
            return rejectWithValue(err.response?.data?.detail || "Failed to send message");
        }
    }
);

export const clearChatHistory = createAsyncThunk(
    "chat/clearHistory",
    async (_, { rejectWithValue }) => {
        try {
            await ChatService.clearHistory();
            return true;
        } catch (err: any) {
            return rejectWithValue(err.response?.data?.detail || "Failed to clear history");
        }
    }
);

const chatSlice = createSlice({
    name: "chat",
    initialState,
    reducers: {
        addOptimisticUserMessage: (state, action: PayloadAction<string>) => {
            const tempId = Date.now().toString();
            state.messages.push({
                id: tempId,
                role: "user",
                content: action.payload,
                timestamp: new Date().toISOString(),
            });
        },
    },
    extraReducers: (builder) => {
        builder
            // Fetch History
            .addCase(fetchChatHistory.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchChatHistory.fulfilled, (state, action: PayloadAction<ChatHistoryResponse[]>) => {
                state.loading = false;

                // Map backend history to frontend message format (flattening the Q&A)
                const formattedMessages: ChatMessage[] = [];

                // Sort by created_at (assuming older messages first)
                const sortedHistory = [...action.payload].sort(
                    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
                );

                sortedHistory.forEach((item) => {
                    // Add User Message
                    formattedMessages.push({
                        id: `user-${item.id}`,
                        role: "user",
                        content: item.human_query,
                        timestamp: item.created_at,
                    });

                    // Add Assistant Message (if there's a result or generated SQL)
                    if (item.result_summary || item.sql_generated) {
                        formattedMessages.push({
                            id: `assistant-${item.id}`,
                            role: "assistant",
                            content: item.result_summary || "Query processed successfully.",
                            sql_generated: item.sql_generated,
                            result_summary: item.result_summary,
                            timestamp: item.created_at, // using same timestamp as it's from history
                        });
                    }
                });

                state.messages = formattedMessages;
            })
            .addCase(fetchChatHistory.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload as string;
            })

            // Send Message
            .addCase(sendChatMessage.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(sendChatMessage.fulfilled, (state, action) => {
                state.loading = false;
                const { response } = action.payload;

                // Ensure Session ID is updated
                if (response.session_id) {
                    state.sessionId = response.session_id;
                }

                const timestamp = new Date().toISOString();

                // Let's remove the optimistic user message if we added it, or just not add it here if we rely on optimistic
                // To be safe, let's just make sure we only add the assistant message since we added optimistic user message

                // If it's a clarification, add system question
                const isClarification = response.status === "clarification_needed";

                state.messages.push({
                    id: `assistant-${Date.now()}`,
                    role: "assistant",
                    content: response.message || (isClarification ? "I need more clarification." : "Here are the results"),
                    sql_generated: undefined, // the query endpoint doesn't return sql immediately, it caches or answers
                    result_summary: response.data ? JSON.stringify(response.data) : undefined,
                    timestamp,
                });
            })
            .addCase(sendChatMessage.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload as string;
            })

            // Clear History
            .addCase(clearChatHistory.pending, (state) => {
                state.loading = true;
            })
            .addCase(clearChatHistory.fulfilled, (state) => {
                state.loading = false;
                state.messages = [];
                state.sessionId = "";
            });
    },
});

export const { addOptimisticUserMessage } = chatSlice.actions;
export default chatSlice.reducer;
