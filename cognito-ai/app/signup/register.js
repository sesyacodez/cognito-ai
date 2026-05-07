


// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-auth.js";

import { getFirestore, setDoc, doc } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-firestore.js";


// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
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

function showMessage(message, divID) {
    var messageDiv = document.getElementById(divID);
    messageDiv.innerHTML = message;
    messageDiv.style.display = 'block';
    messageDiv.style.opacity = 1;

    setTimeout(function() {
        messageDiv.style.opacity = 0;
    }, 3000);
}

const signUp = document.getElementById('submitSignUp');
const signIn = document.getElementById('submitLogin');

const auth = getAuth(app);
const db = getFirestore(app);

signUp.addEventListener('click', (event) => {
    event.preventDefault();
    const signUpForm = event.currentTarget.closest('form');
    const username = signUpForm.querySelector('#username').value;
    const email = signUpForm.querySelector('#email').value;
    const password = signUpForm.querySelector('#password').value;

    createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            // Signed in
            const user = userCredential.user;
            const userData = {
                username: username,
                email: email
            };
            // Save user data to Firestore
            return setDoc(doc(db, "users", user.uid), userData)
                .then(() => {
                    showMessage('Account created successfully!', 'signUpMessage');
                    window.location.href = 'homepage.html';
                });
        })
        .catch((error) => {
            const errorCode = error.code;
            if (errorCode === 'auth/email-already-in-use') {
                showMessage('Email is already in use. Please try another one.', 'signUpMessage');
            } else if (errorCode === 'auth/invalid-email') {
                showMessage('Invalid email format. Please enter a valid email.', 'signUpMessage');
            } else if (errorCode === 'auth/weak-password') {
                showMessage('Password is too weak. Please enter a stronger password.', 'signUpMessage');
            } else {
                showMessage('Error: ' + error.message, 'signUpMessage');
            }
            console.error('Sign up error:', error);
        });
});

signIn.addEventListener('click', (event) => {
    event.preventDefault();
    const signInForm = event.currentTarget.closest('form');
    const email = signInForm.querySelector('#email').value;
    const password = signInForm.querySelector('#password').value;

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            // Signed in
            const user = userCredential.user;
            localStorage.setItem('loggedInUserID', user.uid);
            showMessage('Login successful!', 'loginMessage');
            window.location.href = 'homepage.html';
        })
        .catch((error) => {
            const errorCode = error.code;
            if (errorCode === 'auth/user-not-found') {
                showMessage('User not found. Please check your credentials.', 'loginMessage');
            } else if (errorCode === 'auth/invalid-email') {
                showMessage('Invalid email format. Please enter a valid email.', 'loginMessage');
            } else if (errorCode === 'auth/wrong-password') {
                showMessage('Wrong password. Please try again.', 'loginMessage');
            } else {
                showMessage('Error: ' + error.message, 'loginMessage');
            }
        });
});













