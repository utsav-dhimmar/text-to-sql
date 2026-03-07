import { AdminClient } from ".";

// TODO: REPLACE TO ACTUAL API ROUTES
// time 5 min
export const AdminServices = {
  login: async (data: any) => {
    const { data: res } = await AdminClient.post("/admin/login", data);
    return res;
  },
  getUser: async () => {
    // get name, role
    const { data: res } = await AdminClient.post("/admin/users");
    return res;
  },
  getQuery: async () => {
    // get query, actual SQL query and from which user
    const { data: res } = await AdminClient.post("/admin/query");
    return res;
  },
  toggleUserStatus: async (id: any) => {
    const { data: res } = await AdminClient.patch(`/admin/users/${id}/toggle`);
    return res;
  },
  deleteUser: async (id: any) => {
    const { data: res } = await AdminClient.delete(`/admin/users/${id}/toggle`);
    return res;
  },
  makeAdmin: async (id: any) => {
    const { data: res } = await AdminClient.patch(`/admin/users/${id}/make-admin`);
    return res;
  },
};
