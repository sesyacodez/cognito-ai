from django.urls import path

from .views import firebase_login, login, register

urlpatterns = [
    path("register", register),
    path("login", login),
    path("firebase-login", firebase_login),
]
