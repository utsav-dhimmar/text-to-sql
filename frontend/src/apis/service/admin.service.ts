import { axiosClient } from "../client";

export const AuthService = {
  // todo: complete it based on backend apis
  temp: async () => {
    axiosClient.post("/");
  },
};
