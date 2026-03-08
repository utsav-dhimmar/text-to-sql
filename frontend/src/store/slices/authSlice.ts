import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { UserResponse } from "../../apis/types";

interface AuthState {
  user: UserResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Helper to get initial state from localStorage
const getInitialState = (): AuthState => {
  const token = localStorage.getItem("token");
  const userStr = localStorage.getItem("user");
  let user: UserResponse | null = null;

  if (userStr) {
    try {
      user = JSON.parse(userStr);
    } catch (e) {
      console.error("Failed to parse user from localStorage", e);
    }
  }

  return {
    user,
    token,
    isAuthenticated: !!token,
    isLoading: false,
  };
};

const authSlice = createSlice({
  name: "auth",
  initialState: getInitialState(),
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setCredentials: (
      state,
      action: PayloadAction<{ user: UserResponse; token: string }>,
    ) => {
      const { user, token } = action.payload;
      state.user = user;
      state.token = token;
      state.isAuthenticated = true;
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },
  },
});

export const { setLoading, setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
