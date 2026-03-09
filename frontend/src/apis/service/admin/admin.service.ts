import { AdminClient } from ".";
import type { UserAdminResponse, AuditLogResponse, ChatHistoryResponse } from "../../types";

export const AdminServices = {
  getUsers: async () => {
    const { data: res } =
      await AdminClient.get<UserAdminResponse[]>("/admin/users");
    return res;
  },

  deleteUser: async (userId: string) => {
    const { data: res } = await AdminClient.delete<boolean>(`/admin/users/${userId}`);
    return res;
  },

  updateUserStatus: async (userId: string, status: string) => {
    const { data: res } = await AdminClient.patch<boolean>(
      `/admin/users/${userId}/status`,
      { status },
    );
    return res;
  },

  updateUserRole: async (userId: string, role: string) => {
    const { data: res } = await AdminClient.patch<boolean>(
      `/admin/users/${userId}/role`,
      { role },
    );
    return res;
  },

  getAllChats: async (limit: number = 100) => {
    const { data: res } = await AdminClient.get<ChatHistoryResponse[]>(
      "/admin/chats",
      {
        params: { limit },
      }
    );
    return res;
  },

  getAuditLogs: async (limit: number = 50) => {
    const { data: res } = await AdminClient.get<AuditLogResponse[]>(
      "/admin/audit-logs",
      {
        params: { limit },
      },
    );
    return res;
  },
};
