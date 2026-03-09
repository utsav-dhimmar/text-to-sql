import { axiosClient } from "../client";
import type { DatasetResponse } from "../types";

export const DatasetService = {
  getDatasets: async () => {
    const { data: res } =
      await axiosClient.get<DatasetResponse[]>("/datasets/");
    return res;
  },

  getDataset: async (id: string) => {
    const { data: res } = await axiosClient.get<DatasetResponse>(
      `/datasets/${id}`,
    );
    return res;
  },

  deleteDataset: async (id: string) => {
    const { data: res } = await axiosClient.delete<boolean>(`/datasets/${id}`);
    return res;
  },
};
