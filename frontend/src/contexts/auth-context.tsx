"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  createUserWithEmailAndPassword,
  getRedirectResult,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signInWithRedirect,
  signOut,
  type User,
} from "firebase/auth";
import { FirebaseError } from "firebase/app";
import { toast } from "sonner";
import { auth, googleProvider } from "@/lib/firebase";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  signInEmail: (email: string, password: string) => Promise<void>;
  signUpEmail: (email: string, password: string) => Promise<void>;
  signInGoogle: () => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const ERROR_MESSAGES: Record<string, string> = {
  "auth/invalid-email": "That email address doesn't look right.",
  "auth/user-not-found": "No account found with that email.",
  "auth/wrong-password": "Incorrect password. Please try again.",
  "auth/invalid-credential": "Incorrect email or password.",
  "auth/email-already-in-use": "An account already exists with that email.",
  "auth/weak-password": "Password must be at least 6 characters.",
  "auth/popup-closed-by-user": "Google sign-in was closed before finishing.",
  "auth/cancelled-popup-request": "Google sign-in was cancelled.",
  "auth/popup-blocked": "Your browser blocked the Google sign-in popup. Please allow popups and try again.",
  "auth/operation-not-supported-in-this-environment": "Google sign-in isn't supported in this browser. Try a different browser.",
  "auth/unauthorized-domain": "This domain isn't authorized for Google sign-in yet. Contact the site admin.",
  "auth/network-request-failed": "Network error. Check your connection and try again.",
  "auth/too-many-requests": "Too many attempts. Please wait a moment and try again.",
};

export function friendlyAuthError(error: unknown): string {
  if (error instanceof FirebaseError) {
    return ERROR_MESSAGES[error.code] ?? "Something went wrong. Please try again.";
  }
  return "Something went wrong. Please try again.";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRedirectResult(auth).catch((error) => {
      toast.error(friendlyAuthError(error));
    });

    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      signInEmail: async (email, password) => {
        await signInWithEmailAndPassword(auth, email, password);
      },
      signUpEmail: async (email, password) => {
        await createUserWithEmailAndPassword(auth, email, password);
      },
      signInGoogle: async () => {
        try {
          await signInWithPopup(auth, googleProvider);
        } catch (error) {
          if (
            error instanceof FirebaseError &&
            (error.code === "auth/popup-blocked" ||
              error.code === "auth/operation-not-supported-in-this-environment")
          ) {
            await signInWithRedirect(auth, googleProvider);
            return;
          }
          throw error;
        }
      },
      logout: async () => {
        await signOut(auth);
      },
    }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
