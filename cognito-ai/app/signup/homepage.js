import { initializeApp } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut, deleteUser } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-auth.js";

import { getFirestore, getDoc, doc, deleteDoc, setDoc } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-firestore.js";


const firebaseConfig = {
apiKey: "AIzaSyBD-nh61dGDr6kCH5GNoba3S2r6Viiaj_k",
authDomain: "cognitoai-loginationtest1.firebaseapp.com",
projectId: "cognitoai-loginationtest1",
storageBucket: "cognitoai-loginationtest1.firebasestorage.app",
messagingSenderId: "136750296570",
appId: "1:136750296570:web:fe25cb7069181de6f38843"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

const auth = getAuth(app);
const db = getFirestore(app);
const profileStatus = document.getElementById('profileStatus');
onAuthStateChanged(auth, (user) => {
    if (user) {
        profileStatus.innerText = 'Loading profile...';
        const userId = user.uid || localStorage.getItem('loggedInUserID') || localStorage.getItem('loggedInUserId');
        localStorage.setItem('loggedInUserID', userId);
        const docRef = doc(db, "users", userId);
        getDoc(docRef)
            .then((docSnap) => {
                if (docSnap.exists()) {
                    const userData = docSnap.data();
                    document.getElementById('loggedInUsername').innerText = userData.username;
                    document.getElementById('loggedInEmail').innerText = userData.email;
                    profileStatus.innerText = '';
                } else {
                    const fallbackUsername = user.displayName || (user.email ? user.email.split('@')[0] : 'User');
                    const fallbackEmail = user.email || 'No email';
                    const fallbackUserData = {
                        username: fallbackUsername,
                        email: fallbackEmail
                    };

                    setDoc(doc(db, "users", userId), fallbackUserData, { merge: true })
                        .then(() => {
                            document.getElementById('loggedInUsername').innerText = fallbackUserData.username;
                            document.getElementById('loggedInEmail').innerText = fallbackUserData.email;
                            profileStatus.innerText = '';
                        })
                        .catch((createError) => {
                            console.error("Error creating fallback profile: ", createError);
                            document.getElementById('loggedInUsername').innerText = fallbackUserData.username;
                            document.getElementById('loggedInEmail').innerText = fallbackUserData.email;
                            profileStatus.innerText = 'Profile restored from login data.';
                        });
                }
            })
            .catch((error) => {
                console.error("Error fetching user data: ", error);
                profileStatus.innerText = 'Could not load profile.';
            });
    } else {
        console.log("No user is currently logged in.");
        window.location.href = 'main.html';
    }
});

const logoutButton = document.getElementById('logoutButton');
const deleteAccountButton = document.getElementById('deleteAccountButton');

logoutButton.addEventListener('click', () => {
    signOut(auth)
        .then(() => {
            localStorage.removeItem('loggedInUserID');
            localStorage.removeItem('loggedInUserId');
            window.location.href = 'main.html';
        })
        .catch((error) => {
            console.error("Error signing out: ", error);
        });
});

deleteAccountButton.addEventListener('click', async () => {
    const user = auth.currentUser;
    if (!user) {
        alert('No authenticated user found. Please log in again.');
        window.location.href = 'main.html';
        return;
    }

    const shouldDelete = window.confirm('Are you sure you want to permanently delete your account?');
    if (!shouldDelete) {
        return;
    }

    try {
        await deleteDoc(doc(db, 'users', user.uid));
        await deleteUser(user);
        localStorage.removeItem('loggedInUserID');
        localStorage.removeItem('loggedInUserId');
        alert('Your account has been deleted.');
        window.location.href = 'main.html';
    } catch (error) {
        if (error.code === 'auth/requires-recent-login') {
            alert('For security, please log in again and then try deleting your account.');
        } else {
            console.error('Error deleting account:', error);
            alert('Could not delete account. Please try again.');
        }
    }
});









