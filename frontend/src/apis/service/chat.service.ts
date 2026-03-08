import { axiosClient } from "../client";
import type { ChatHistoryResponse } from "../types";

export interface ChatCreateData {
  human_query: string;
  sql_generated?: string;
  result_summary?: string;
}

export const ChatService = {
  saveChat: async (data: ChatCreateData) => {
    const { data: res } = await axiosClient.post<ChatHistoryResponse>(
      "/chat/",
      data,
    );
    return res;
  },

  getHistory: async (limit: number = 20) => {
    const { data: res } = await axiosClient.get<ChatHistoryResponse[]>(
      "/chat/history",
      {
        params: { limit },
      },
    );
    return res;
  },

  clearHistory: async () => {
    const { data: res } = await axiosClient.delete<number>("/chat/history");
    return res;
  },
};
