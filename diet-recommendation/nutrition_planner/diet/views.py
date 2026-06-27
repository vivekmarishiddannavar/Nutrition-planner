"""
Views for Nutrition Planner Application
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Avg
from datetime import date, timedelta, datetime
import json

from .models import UserProfile, MealPlan, DailyLog
from .diet_engine import (
    NutritionCalculator,
    MealPlanGenerator,
    generate_complete_nutrition_plan,
)



# ============================================================
# SETUP & PROFILE VIEWS
# ============================================================

def home(request):
    """
    Landing page
    """
    if request.user.is_authenticated:
        return redirect("diet:dashboard")
    return render(request, "diet/home.html")


def custom_login(request):
    """
    Custom login view
    """
    if request.user.is_authenticated:
        return redirect("diet:dashboard")

    if request.method == "POST":
        from django.contrib.auth import authenticate

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Ensure UserProfile exists (create if not found)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("diet:dashboard")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "diet/login.html")


def custom_register(request):
    """
    User registration with role selection
    """
    if request.user.is_authenticated:
        return redirect("diet:dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = request.POST.get("role", "user")
            phone = request.POST.get("phone", "")
            institution = request.POST.get("institution", "")

            UserProfile.objects.create(
                user=user, role=role, phone=phone, institution=institution
            )

            messages.success(request, "Registration successful! Please login.")
            return redirect("diet:login")
    else:
        form = UserCreationForm()

    return render(request, "diet/register.html", {"form": form})


def custom_logout(request):
    """
    Logout view
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("diet:home")


def setup(request):
    """
    Initial setup view - Collect user health data
    """
    if request.method == "POST":
        try:
            # Extract form data
            age = int(request.POST.get("age"))
            gender = request.POST.get("gender")
            weight = float(request.POST.get("weight"))
            height = float(request.POST.get("height"))
            activity_level = request.POST.get("activity_level")
            goal = request.POST.get("goal")
            target_weight = request.POST.get("target_weight")
            diet_preference = request.POST.get("diet_preference", "balanced")

            # Calculate nutritional targets
            targets = NutritionCalculator.calculate_daily_targets(
                gender=gender,
                age=age,
                weight=weight,
                height=height,
                activity_level=activity_level,
                goal=goal,
                diet_preference=diet_preference,
            )

            # Create user profile
            profile = UserProfile.objects.create(
                age=age,
                gender=gender,
                weight=weight,
                height=height,
                activity_level=activity_level,
                goal=goal,
                target_weight=float(target_weight) if target_weight else None,
                diet_preference=diet_preference,
                bmr=targets["bmr"],
                tdee=targets["tdee"],
                daily_calorie_target=targets["daily_calories"],
                protein_target=targets["protein_g"],
                carbs_target=targets["carbs_g"],
                fat_target=targets["fat_g"],
            )

            # Store profile ID in session
            request.session["profile_id"] = profile.id

            messages.success(request, "Profile created successfully!")
            return redirect("diet:dashboard")

        except Exception as e:
            messages.error(request, f"Error creating profile: {str(e)}")
            return redirect("diet:setup")

    # GET request - show setup form
    context = {
        "page_title": "Setup Your Profile",
    }
    return render(request, "diet/setup.html", context)


def update_profile(request):
    """
    Update existing profile
    """
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return redirect("diet:setup")

    profile = get_object_or_404(UserProfile, id=profile_id)

    if request.method == "POST":
        try:
            profile.age = int(request.POST.get("age"))
            profile.gender = request.POST.get("gender")
            profile.weight = float(request.POST.get("weight"))
            profile.height = float(request.POST.get("height"))
            profile.activity_level = request.POST.get("activity_level")
            profile.goal = request.POST.get("goal")
            profile.target_weight = (
                float(request.POST.get("target_weight"))
                if request.POST.get("target_weight")
                else None
            )
            profile.diet_preference = request.POST.get("diet_preference", "balanced")

            # Recalculate targets
            targets = NutritionCalculator.calculate_daily_targets(
                gender=profile.gender,
                age=profile.age,
                weight=profile.weight,
                height=profile.height,
                activity_level=profile.activity_level,
                goal=profile.goal,
                diet_preference=profile.diet_preference,
            )

            profile.bmr = targets["bmr"]
            profile.tdee = targets["tdee"]
            profile.daily_calorie_target = targets["daily_calories"]
            profile.protein_target = targets["protein_g"]
            profile.carbs_target = targets["carbs_g"]
            profile.fat_target = targets["fat_g"]
            profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("diet:dashboard")

        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")

    context = {
        "page_title": "Update Profile",
        "profile": profile,
    }
    return render(request, "diet/setup.html", context)


# ============================================================
# DASHBOARD VIEWS
# ============================================================


def dashboard(request):
    """
    Main dashboard with meal plan and progress charts
    """
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return redirect("diet:setup")

    profile = get_object_or_404(UserProfile, id=profile_id)

    # Get today's meal plan or create one
    today = date.today()
    meal_plan = MealPlan.objects.filter(profile=profile, plan_date=today).first()

    # If meal plan doesn't exist, generate it
    if not meal_plan:
        meal_plan = generate_and_save_meal_plan(profile, today)

    # Get recent daily logs for charts
    recent_logs = DailyLog.objects.filter(profile=profile).order_by("-log_date")[:30]

    # Prepare chart data
    chart_data = prepare_chart_data(profile, recent_logs)

    # Get today's log if exists
    today_log = DailyLog.objects.filter(profile=profile, log_date=today).first()

    # Calculate progress stats
    stats = calculate_progress_stats(profile, recent_logs)

    context = {
        "page_title": "Dashboard",
        "profile": profile,
        "meal_plan": meal_plan,
        "today_log": today_log,
        "chart_data": json.dumps(chart_data),
        "stats": stats,
    }
    return render(request, "diet/dashboard.html", context)


def generate_and_save_meal_plan(profile, plan_date):
    """
    Generate and save a meal plan for a specific date
    """
    generator = MealPlanGenerator(
        {
            "daily_calories": profile.daily_calorie_target,
            "protein_g": profile.protein_target,
            "carbs_g": profile.carbs_target,
            "fat_g": profile.fat_target,
        },
        profile.diet_preference,
    )

    daily_plan = generator._generate_single_day()

    # Convert meals to the format expected by the model
    meals_json = {}
    for meal_type, foods in daily_plan["meals"].items():
        meals_json[meal_type] = foods

    meal_plan = MealPlan.objects.create(
        profile=profile,
        plan_date=plan_date,
        meals=meals_json,
        total_calories=daily_plan["totals"]["calories"],
        total_protein=daily_plan["totals"]["protein"],
        total_carbs=daily_plan["totals"]["carbs"],
        total_fat=daily_plan["totals"]["fat"],
    )

    return meal_plan


def regenerate_meal_plan(request):
    """
    Regenerate today's meal plan
    """
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return redirect("diet:setup")

    profile = get_object_or_404(UserProfile, id=profile_id)
    today = date.today()

    # Delete existing meal plan for today
    MealPlan.objects.filter(profile=profile, plan_date=today).delete()

    # Generate new meal plan
    generate_and_save_meal_plan(profile, today)

    messages.success(request, "Meal plan regenerated successfully!")
    return redirect("diet:dashboard")


def prepare_chart_data(profile, logs):
    """
    Prepare data for Chart.js visualization
    """
    if not logs:
        return {
            "labels": [],
            "weight": [],
            "calories": [],
            "target_calories": [],
        }

    # Reverse to get chronological order
    logs = list(reversed(logs))

    labels = [log.log_date.strftime("%b %d") for log in logs]
    weight_data = [log.weight for log in logs]
    calories_data = [log.calories_consumed for log in logs]
    target_calories = [profile.daily_calorie_target] * len(logs)

    return {
        "labels": labels,
        "weight": weight_data,
        "calories": calories_data,
        "target_calories": target_calories,
    }


def calculate_progress_stats(profile, logs):
    """
    Calculate progress statistics
    """
    if not logs:
        return {
            "current_weight": profile.weight,
            "weight_change": 0,
            "avg_calories": 0,
            "days_tracked": 0,
            "goal_progress": 0,
        }

    logs_list = list(logs)
    current_weight = logs_list[0].weight if logs_list else profile.weight
    starting_weight = profile.weight
    weight_change = current_weight - starting_weight

    avg_calories = logs.aggregate(avg_cal=Avg("calories_consumed"))["avg_cal"] or 0
    days_tracked = logs.count()

    # Calculate goal progress
    if profile.goal == "lose" and profile.target_weight:
        goal_progress = (
            (starting_weight - current_weight)
            / (starting_weight - profile.target_weight)
        ) * 100
    elif profile.goal == "gain" and profile.target_weight:
        goal_progress = (
            (current_weight - starting_weight)
            / (profile.target_weight - starting_weight)
        ) * 100
    else:
        goal_progress = 0

    goal_progress = max(0, min(100, goal_progress))  # Clamp between 0-100

    return {
        "current_weight": round(current_weight, 1),
        "weight_change": round(weight_change, 1),
        "avg_calories": round(avg_calories, 1),
        "days_tracked": days_tracked,
        "goal_progress": round(goal_progress, 1),
    }


# ============================================================
# LOGGING VIEWS
# ============================================================


def log_daily(request):
    """
    Log daily weight and intake
    """
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return redirect("diet:setup")

    profile = get_object_or_404(UserProfile, id=profile_id)

    if request.method == "POST":
        try:
            log_date = request.POST.get("log_date") or date.today()
            weight = float(request.POST.get("weight"))
            calories = float(request.POST.get("calories_consumed", 0))
            protein = float(request.POST.get("protein_consumed", 0))
            carbs = float(request.POST.get("carbs_consumed", 0))
            fat = float(request.POST.get("fat_consumed", 0))
            water = float(request.POST.get("water_intake", 0))
            energy_level = request.POST.get("energy_level")
            notes = request.POST.get("notes", "")

            # Create or update daily log
            daily_log, created = DailyLog.objects.update_or_create(
                profile=profile,
                log_date=log_date,
                defaults={
                    "weight": weight,
                    "calories_consumed": calories,
                    "protein_consumed": protein,
                    "carbs_consumed": carbs,
                    "fat_consumed": fat,
                    "water_intake": water,
                    "energy_level": int(energy_level) if energy_level else None,
                    "notes": notes,
                },
            )

            messages.success(request, f"Daily log for {log_date} saved successfully!")
            return redirect("diet:dashboard")

        except Exception as e:
            messages.error(request, f"Error saving log: {str(e)}")

    # Get existing log for today if any
    today = date.today()
    existing_log = DailyLog.objects.filter(profile=profile, log_date=today).first()

    context = {
        "page_title": "Daily Log",
        "profile": profile,
        "existing_log": existing_log,
        "today": today,
    }
    return render(request, "diet/log.html", context)


def log_history(request):
    """
    View log history
    """
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return redirect("diet:setup")

    profile = get_object_or_404(UserProfile, id=profile_id)

    logs = DailyLog.objects.filter(profile=profile).order_by("-log_date")[:30]

    context = {
        "page_title": "Log History",
        "profile": profile,
        "logs": logs,
    }
    return render(request, "diet/log_history.html", context)


# ============================================================
# REPORT VIEWS
# ============================================================


def weekly_report(request):
    """
    Weekly nutrition report
    """
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return redirect("diet:setup")

    profile = get_object_or_404(UserProfile, id=profile_id)

    # Get last 7 days of logs
    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    weekly_logs = DailyLog.objects.filter(
        profile=profile, log_date__gte=start_date, log_date__lte=end_date
    ).order_by("log_date")

    # Calculate weekly averages
    if weekly_logs.exists():
        avg_weight = weekly_logs.aggregate(Avg("weight"))["weight__avg"]
        avg_calories = weekly_logs.aggregate(Avg("calories_consumed"))[
            "calories_consumed__avg"
        ]
        avg_protein = weekly_logs.aggregate(Avg("protein_consumed"))[
            "protein_consumed__avg"
        ]
        avg_carbs = weekly_logs.aggregate(Avg("carbs_consumed"))["carbs_consumed__avg"]
        avg_fat = weekly_logs.aggregate(Avg("fat_consumed"))["fat_consumed__avg"]
        total_water = weekly_logs.aggregate(total=Sum("water_intake"))["total"]
    else:
        avg_weight = profile.weight
        avg_calories = 0
        avg_protein = 0
        avg_carbs = 0
        avg_fat = 0
        total_water = 0

    # Get meal plans for the week
    weekly_meal_plans = MealPlan.objects.filter(
        profile=profile, plan_date__gte=start_date, plan_date__lte=end_date
    ).order_by("plan_date")

    context = {
        "page_title": "Weekly Report",
        "profile": profile,
        "weekly_logs": weekly_logs,
        "weekly_meal_plans": weekly_meal_plans,
        "start_date": start_date,
        "end_date": end_date,
        "averages": {
            "weight": round(avg_weight, 1) if avg_weight else 0,
            "calories": round(avg_calories, 1) if avg_calories else 0,
            "protein": round(avg_protein, 1) if avg_protein else 0,
            "carbs": round(avg_carbs, 1) if avg_carbs else 0,
            "fat": round(avg_fat, 1) if avg_fat else 0,
            "water": round(total_water, 1) if total_water else 0,
        },
    }
    return render(request, "diet/report.html", context)


def meal_plan_detail(request, plan_id):
    """
    View detailed meal plan
    """
    profile_id = request.session.get("profile_id")
    if not profile_id:
        return redirect("diet:setup")

    meal_plan = get_object_or_404(MealPlan, id=plan_id, profile__id=profile_id)

    context = {
        "page_title": f"Meal Plan - {meal_plan.plan_date}",
        "meal_plan": meal_plan,
    }
    return render(request, "diet/meal_plan_detail.html", context)


# ============================================================
# UTILITY VIEWS
# ============================================================


def reset_profile(request):
    """
    Reset user profile and start over
    """
    if request.method == "POST":
        # Clear session
        request.session.flush()

        messages.success(request, "Profile reset. Please set up your profile again.")
        return redirect("diet:setup")

    context = {
        "page_title": "Reset Profile",
    }
    return render(request, "diet/reset.html", context)


def about(request):
    """
    About page - How the nutrition planner works
    """
    context = {
        "page_title": "About Nutrition Planner",
    }
    return render(request, "diet/about.html", context)


# Import Sum for weekly report calculations
from django.db.models import Sum
