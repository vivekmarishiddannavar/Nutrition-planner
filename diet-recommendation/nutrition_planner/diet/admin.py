"""
Admin Configuration for Nutrition Planner
"""

from django.contrib import admin
from .models import UserProfile, MealPlan, DailyLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile
    """

    list_display = [
        "id",
        "age",
        "gender",
        "weight",
        "height",
        "activity_level",
        "goal",
        "diet_preference",
        "bmr",
        "tdee",
        "daily_calorie_target",
        "created_at",
    ]
    list_filter = ["gender", "activity_level", "goal", "diet_preference", "created_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = [
        "bmr",
        "tdee",
        "daily_calorie_target",
        "protein_target",
        "carbs_target",
        "fat_target",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Physical Metrics",
            {"fields": ("age", "gender", "weight", "height", "activity_level")},
        ),
        (
            "Goals & Preferences",
            {"fields": ("goal", "target_weight", "diet_preference")},
        ),
        (
            "Calculated Values",
            {
                "fields": (
                    "bmr",
                    "tdee",
                    "daily_calorie_target",
                    "protein_target",
                    "carbs_target",
                    "fat_target",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    """
    Admin interface for MealPlan
    """

    list_display = [
        "id",
        "profile",
        "plan_date",
        "total_calories",
        "total_protein",
        "total_carbs",
        "total_fat",
        "was_followed",
        "created_at",
    ]
    list_filter = ["plan_date", "was_followed", "created_at"]
    search_fields = ["profile__user__username"]
    readonly_fields = ["created_at"]

    fieldsets = (
        ("Plan Information", {"fields": ("profile", "plan_date")}),
        ("Meals", {"fields": ("meals",)}),
        (
            "Daily Totals",
            {"fields": ("total_calories", "total_protein", "total_carbs", "total_fat")},
        ),
        ("Tracking", {"fields": ("was_followed",)}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    """
    Admin interface for DailyLog
    """

    list_display = [
        "id",
        "profile",
        "log_date",
        "weight",
        "calories_consumed",
        "protein_consumed",
        "carbs_consumed",
        "fat_consumed",
        "water_intake",
        "energy_level",
        "created_at",
    ]
    list_filter = ["log_date", "energy_level", "created_at"]
    search_fields = ["profile__user__username", "notes"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Log Information", {"fields": ("profile", "log_date")}),
        ("Weight & Calories", {"fields": ("weight", "calories_consumed")}),
        (
            "Macros Consumed",
            {"fields": ("protein_consumed", "carbs_consumed", "fat_consumed")},
        ),
        ("Additional Info", {"fields": ("water_intake", "energy_level", "notes")}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
