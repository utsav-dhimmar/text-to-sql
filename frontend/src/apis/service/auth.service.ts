import type {
	RegisterFormValues,
	LoginFormValues,
} from "../../schema/user.schema";
import { axiosClient } from "../client";
import type { UserResponse, TokenResponse, MessageResponse } from "../types";

export const AuthService = {
	register: async (data: RegisterFormValues) => {
		const { data: res } = await axiosClient.post<UserResponse>(
			"/auth/register",
			data,
		);
		return res;
	},

	login: async (data: LoginFormValues) => {
		const { data: res } = await axiosClient.post<TokenResponse>(
			"/auth/login",
			data,
		);
		return res;
	},

	logout: async () => {
		const { data: res } =
			await axiosClient.post<MessageResponse>("/auth/logout");
		return res;
	},

	getMe: async () => {
		const { data: res } = await axiosClient.get<UserResponse>("/auth/me");
		return res;
	},

	refreshToken: async () => {
		const { data: res } =
			await axiosClient.post<TokenResponse>("/auth/refresh");
		return res;
	},
};
