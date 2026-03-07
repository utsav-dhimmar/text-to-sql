import type { RegisterFormValues, LoginFormValues } from "../../schema/user.schema";
import { axiosClient } from "../client";

export const AuthService = {
  register: async (data: RegisterFormValues) => {
    const { data: res } = await axiosClient.post<RegisterFormValues>("/auth/register", data);
    return res;
  },
  login: async (data: LoginFormValues) => {
    const { data: res } = await axiosClient.post<LoginFormValues>("/auth/login", data);
    return res;
  },

  // TODO: hanlde for google and github login
};
