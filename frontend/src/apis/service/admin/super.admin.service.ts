import { AdminClient } from ".";
import { AdminServices } from "./admin.service";

// TODO: REPLACE TO ACTUAL API ROUTES
// approx time 2 min
export const SuperAdminServices = {
  ...AdminServices,
  addNewSector: async (data: any) => {
    const { data: res } = await AdminClient.patch("/admin/new-sector", data);
    return res;
  },
  addNewCompany: async (data: any) => {
    const { data: res } = await AdminClient.post("/admin/new-company", data);
    return res;
  },
};
