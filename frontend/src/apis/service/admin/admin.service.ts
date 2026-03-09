import { AdminClient } from ".";
import type { UserAdminResponse, AuditLogResponse } from "../../types";

export const AdminServices = {
  getUsers: async () => {
    const { data: res } =
      await AdminClient.get<UserAdminResponse[]>("/admin/users");
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
