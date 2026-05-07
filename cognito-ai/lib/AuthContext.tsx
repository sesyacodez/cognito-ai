"use client";

import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  updateProfile,
  User as FirebaseUser,
} from "firebase/auth";
import { getFirebaseAuth, getGoogleProvider } from "@/lib/firebase";
import { AuthUser, setSession, clearSession } from "@/lib/auth";

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function mapFirebaseUser(firebaseUser: FirebaseUser): AuthUser {
  return {
    id: firebaseUser.uid,
    email: firebaseUser.email ?? "",
    name:
      firebaseUser.displayName ||
      firebaseUser.email?.split("@")[0] ||
      "User",
  };
}

function mapFirebaseError(err: unknown): Error {
  const code = (err as { code?: string }).code;
  const messages: Record<string, string> = {
    "auth/email-already-in-use": "An account with this email already exists.",
    "auth/invalid-email": "Invalid email address.",
    "auth/weak-password": "Password is too weak. Use at least 6 characters.",
    "auth/user-not-found": "No account found with this email.",
    "auth/wrong-password": "Incorrect password.",
    "auth/invalid-credential": "Invalid email or password.",
    "auth/too-many-requests": "Too many attempts. Please try again later.",
    "auth/network-request-failed": "Network error. Check your connection.",
    "auth/popup-closed-by-user": "Sign-in popup was closed.",
    "auth/cancelled-popup-request": "Sign-in cancelled.",
  };
  if (code && messages[code]) return new Error(messages[code]);
  return err instanceof Error ? err : new Error("Authentication failed.");
}

async function syncWithBackend(firebaseUser: FirebaseUser): Promise<AuthUser> {
  const mapped = mapFirebaseUser(firebaseUser);
  try {
    const idToken = await firebaseUser.getIdToken();
    const res = await fetch("/api/auth/firebase-login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_token: idToken }),
    });
    if (res.ok) {
      const data = await res.json();
      const backendUser: AuthUser = {
        id: data.user?.id ?? mapped.id,
        email: data.user?.email ?? mapped.email,
        name: data.user?.name ?? mapped.name,
      };
      setSession(data.session_token, backendUser);
      return backendUser;
    }
  } catch {
    // Backend unreachable — fall back to Firebase UID as token
  }
  setSession(firebaseUser.uid, mapped);
  return mapped;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const initialized = useRef(false);

  useEffect(() => {
    const a = getFirebaseAuth();
    if (!a) {
      // No auth available during SSR/prerender — mark as not-loading and exit safely
      if (!initialized.current) {
        initialized.current = true;
        setIsLoading(false);
      }
      return;
    }
    const unsubscribe = onAuthStateChanged(a, async (firebaseUser) => {
      if (firebaseUser) {
        const backendUser = await syncWithBackend(firebaseUser);
        setUser(backendUser);
      } else {
        setUser(null);
        clearSession();
      }
      if (!initialized.current) {
        initialized.current = true;
        setIsLoading(false);
      }
    });
    return () => unsubscribe();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const a = getFirebaseAuth();
      if (!a) throw new Error("Firebase auth not available");
      await signInWithEmailAndPassword(a, email, password);
      // onAuthStateChanged will update user state
    } catch (err) {
      throw mapFirebaseError(err);
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    setIsLoading(true);
    try {
      const a = getFirebaseAuth();
      const gp = getGoogleProvider();
      if (!a || !gp) throw new Error("Firebase auth or provider not available");
      await signInWithPopup(a, gp);
    } catch (err) {
      throw mapFirebaseError(err);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      const a = getFirebaseAuth();
      if (!a) throw new Error("Firebase auth not available");
      const { user: fbUser } = await createUserWithEmailAndPassword(a, email, password);
      await updateProfile(fbUser, { displayName: name });
      const backendUser = await syncWithBackend(fbUser);
      backendUser.name = name;
      setUser(backendUser);
    } catch (err) {
      throw mapFirebaseError(err);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    const a = getFirebaseAuth();
    if (!a) return;
    await signOut(a);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user !== null,
        login,
        loginWithGoogle,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
