import { axiosClient } from "../client";

export const ChatService = {
  // todo: complete it based on backend apis
  temp: async () => {
    axiosClient.post("/");
  },
};
