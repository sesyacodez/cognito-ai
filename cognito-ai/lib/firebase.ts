import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBD-nh61dGDr6kCH5GNoba3S2r6Viiaj_k",
  authDomain: "cognitoai-loginationtest1.firebaseapp.com",
  projectId: "cognitoai-loginationtest1",
  storageBucket: "cognitoai-loginationtest1.firebasestorage.app",
  messagingSenderId: "136750296570",
  appId: "1:136750296570:web:fe25cb7069181de6f38843",
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
