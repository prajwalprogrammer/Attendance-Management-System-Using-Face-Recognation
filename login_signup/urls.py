
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('signup/', views.signup),
    path('login/', views.login),
    path('sign_up/', views.sign_up),
    path('signnin/', views.signnin),
    path('logout/', views.logout),
    path('profile/', views.profile),
    path('addimage/', views.addimage),
    path('MarkAttendance/', views.MarkAttendance),
    path('desplayAttendance/', views.desplayAttendance),
    path('aboutus/', views.aboutus),
]
