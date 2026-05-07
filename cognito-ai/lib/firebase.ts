import { initializeApp, getApps, getApp, FirebaseApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, Auth } from "firebase/auth";

/* export const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
}; */

// DELETE THIS AND REPLACE WITH ENV 
const firebaseConfig = {
  apiKey: "AIzaSyBD-nh61dGDr6kCH5GNoba3S2r6Viiaj_k",
  authDomain: "cognitoai-loginationtest1.firebaseapp.com",
  projectId: "cognitoai-loginationtest1",
  storageBucket: "cognitoai-loginationtest1.firebasestorage.app",
  messagingSenderId: "136750296570",
  appId: "1:136750296570:web:fe25cb7069181de6f38843"
};

// Lazily initialize Firebase only on the client to avoid SSR/prerender issues.
let _app: FirebaseApp | null = null;
let _auth: Auth | null = null;

function getFirebaseApp(): FirebaseApp | null {
  if (typeof window === "undefined") return null;
  if (_app) return _app;
  try {
    _app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
    return _app;
  } catch (e) {
    // If initialization fails (missing env in build), return null and let callers handle it.
    // We avoid throwing during module import to keep SSR/build safe.
    // eslint-disable-next-line no-console
    console.warn("Firebase initialization skipped or failed:", e);
    return null;
  }
}

export function getFirebaseAuth(): Auth | null {
  if (typeof window === "undefined") return null;
  if (_auth) return _auth;
  const app = getFirebaseApp();
  if (!app) return null;
  _auth = getAuth(app);
  return _auth;
}

// Avoid creating provider during SSR/module-evaluation. Provide a safe getter instead.
export function getGoogleProvider(): GoogleAuthProvider | null {
  if (typeof window === "undefined") return null;
  try {
    return new GoogleAuthProvider();
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn("Could not create GoogleAuthProvider:", e);
    return null;
  }
}
