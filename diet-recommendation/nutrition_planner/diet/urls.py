"""
URL Configuration for Diet App
"""

from django.urls import path
from . import views

app_name = "diet"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.custom_login, name="login"),
    path("register/", views.custom_register, name="register"),
    path("logout/", views.custom_logout, name="logout"),
    # Setup & Profile
    path("", views.setup, name="setup"),
    path("update/", views.update_profile, name="update_profile"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("regenerate/", views.regenerate_meal_plan, name="regenerate"),
    # Logging
    path("log/", views.log_daily, name="log"),
    path("log/history/", views.log_history, name="log_history"),
    # Reports
    path("report/weekly/", views.weekly_report, name="weekly_report"),
    path("meal-plan/<int:plan_id>/", views.meal_plan_detail, name="meal_plan_detail"),
    # Utility
    path("reset/", views.reset_profile, name="reset"),
    path("about/", views.about, name="about"),
]
