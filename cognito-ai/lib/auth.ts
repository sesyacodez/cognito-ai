// Auth utilities for session token management
const SESSION_TOKEN_KEY = "auth_session_token";
const USER_KEY = "auth_user";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export interface AuthResponse {
  session_token: string;
  user: AuthUser;
}

export function setSession(token: string, user: AuthUser) {
  if (typeof window !== "undefined") {
    localStorage.setItem(SESSION_TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

export function getSession(): { token: string; user: AuthUser } | null {
  if (typeof window === "undefined") return null;

  const token = localStorage.getItem(SESSION_TOKEN_KEY);
  const userJson = localStorage.getItem(USER_KEY);

  if (!token || !userJson) return null;

  try {
    return {
      token,
      user: JSON.parse(userJson),
    };
  } catch {
    return null;
  }
}

export function clearSession() {
  if (typeof window !== "undefined") {
    localStorage.removeItem(SESSION_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

export function getAuthHeader(): Record<string, string> {
  const session = getSession();
  if (!session) return {};
  return {
    Authorization: `Bearer ${session.token}`,
  };
}
