import axios from "axios";

export const AdminClient = axios.create({
  baseURL: "/api",
});

AdminClient.interceptors.request.use(
  (c) => {
    // TODO: take token from localstorge if token store in localstorage
    return c;
  },
  (error) => {
    return Promise.reject(error);
  },
);
