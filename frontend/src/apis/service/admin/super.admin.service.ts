import { AdminClient } from ".";
import { AdminServices } from "./admin.service";
import type { UserAdminResponse } from "../../types";

export const SuperAdminServices = {
  ...AdminServices,
  getAdmins: async () => {
    const { data: res } =
      await AdminClient.get<UserAdminResponse[]>("/superadmin/admins");
    return res;
  },
  updateUserRole: async (userId: string, role: string) => {
    const { data: res } = await AdminClient.patch<boolean>(
      `/superadmin/users/${userId}/role`,
      { role },
    );
    return res;
  },
};
