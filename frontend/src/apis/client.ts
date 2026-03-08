import axios from "axios";

export const axiosClient = axios.create({
  baseURL: "/api",
});

axiosClient.interceptors.request.use(
  (c) => {
    // TODO: take token from localstorge if token store in localstorage
    return c;
  },
  (error) => {
    return Promise.reject(error);
  },
);
