import { AuthProvider, HttpError } from "react-admin";
import { API_BASE_URL } from "./utils/common";

function clearAuth() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("must_change_password");
}

function getStoredUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

export const authProvider: AuthProvider = {
  login: async ({ username, password }) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new HttpError("Unauthorized", 401, {
        message: "Invalid username or password",
      });
    }

    const { access_token, must_change_password } = await response.json();
    localStorage.setItem("token", access_token);

    // Fetch user identity
    const meResponse = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    if (meResponse.ok) {
      const user = await meResponse.json();
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: user.id,
          fullName: user.full_name,
          avatar: user.avatar,
          username: user.username,
          role: user.role,
        }),
      );
      if (must_change_password) {
        localStorage.setItem("must_change_password", "true");
      }
    }
  },
  logout: () => {
    clearAuth();
    return Promise.resolve();
  },
  checkError: ({ status }) => {
    if (status === 401) {
      clearAuth();
      return Promise.reject();
    }
    return Promise.resolve();
  },
  checkAuth: () => {
    const token = localStorage.getItem("token");
    if (!token) return Promise.reject();
    return Promise.resolve();
  },
  getPermissions: () => {
    const user = getStoredUser();
    return Promise.resolve(user?.role);
  },
  getIdentity: () => {
    return Promise.resolve(getStoredUser());
  },
};

export default authProvider;
