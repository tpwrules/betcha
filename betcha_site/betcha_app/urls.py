from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('week/<int:week>/', views.week, name="week"),

    path('history/', views.past_weeks, name="past_weeks"),

    path('winston/', views.winston, name="winston"),

    path('accounts/login/', auth_views.LoginView.as_view(), name="login"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('accounts/password_change/',
        auth_views.PasswordChangeView.as_view(),
        name="password_change"),
    path('accounts/password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done"),
]