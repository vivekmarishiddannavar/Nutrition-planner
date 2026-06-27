"""
Database Models for Nutrition Planner Application
"""

from django.db import models
from django.contrib.auth.models import User
import json


class UserProfile(models.Model):
    """
    Stores user's physical metrics and dietary preferences
    """

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    ACTIVITY_LEVELS = [
        ("sedentary", "Sedentary (little or no exercise)"),
        ("light", "Lightly Active (light exercise 1-3 days/week)"),
        ("moderate", "Moderately Active (moderate exercise 3-5 days/week)"),
        ("active", "Very Active (hard exercise 6-7 days/week)"),
        ("extra", "Extra Active (very hard exercise & physical job)"),
    ]

    GOALS = [
        ("lose", "Lose Weight"),
        ("maintain", "Maintain Weight"),
        ("gain", "Gain Weight"),
    ]

    DIET_PREFERENCES = [
        ("balanced", "Balanced Diet"),
        ("vegetarian", "Vegetarian (no meat)"),
        ("vegan", "Vegan (no animal products)"),
        ("keto", "Ketogenic (high fat, low carb)"),
        ("paleo", "Paleo (whole foods)"),
        ("gluten_free", "Gluten-Free"),
    ]

    # Link to Django user (optional - allows anonymous users too)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # Physical metrics
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    weight = models.FloatField(help_text="Weight in kg")
    height = models.FloatField(help_text="Height in cm")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS)

    # Goals
    goal = models.CharField(max_length=10, choices=GOALS)
    target_weight = models.FloatField(
        null=True, blank=True, help_text="Optional target weight in kg"
    )

    # Dietary preferences
    diet_preference = models.CharField(
        max_length=20, choices=DIET_PREFERENCES, default="balanced"
    )

    # Calculated fields
    bmr = models.FloatField(
        null=True, blank=True, help_text="Basal Metabolic Rate (calories/day)"
    )
    tdee = models.FloatField(
        null=True, blank=True, help_text="Total Daily Energy Expenditure (calories/day)"
    )
    daily_calorie_target = models.FloatField(
        null=True, blank=True, help_text="Daily calorie target based on goal"
    )

    # Macros (in grams)
    protein_target = models.FloatField(
        null=True, blank=True, help_text="Daily protein target (grams)"
    )
    carbs_target = models.FloatField(
        null=True, blank=True, help_text="Daily carbs target (grams)"
    )
    fat_target = models.FloatField(
        null=True, blank=True, help_text="Daily fat target (grams)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Profile - {self.get_gender_display()}, {self.age} years, {self.weight}kg"
        )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-created_at"]


class MealPlan(models.Model):
    """
    Stores generated meal plans for users
    """

    MEAL_TYPES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    # Link to user profile
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="meal_plans"
    )

    # Date for this plan
    plan_date = models.DateField()

    # Meal data stored as JSON
    # Format: {"breakfast": [{"name": "Oatmeal", "calories": 150, "protein": 5, ...}], ...}
    meals = models.JSONField(default=dict)

    # Daily totals
    total_calories = models.FloatField()
    total_protein = models.FloatField()
    total_carbs = models.FloatField()
    total_fat = models.FloatField()

    # Adherence tracking
    was_followed = models.BooleanField(
        null=True, blank=True, help_text="Did user follow this plan?"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meal Plan for {self.plan_date}"

    def get_meal_by_type(self, meal_type):
        """Get foods for a specific meal type"""
        return self.meals.get(meal_type, [])

    class Meta:
        verbose_name = "Meal Plan"
        verbose_name_plural = "Meal Plans"
        ordering = ["-plan_date"]
        unique_together = ["profile", "plan_date"]


class DailyLog(models.Model):
    """
    Stores daily tracking of weight and calorie intake
    """

    # Link to user profile
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="daily_logs"
    )

    # Date
    log_date = models.DateField()

    # Actual weight recorded
    weight = models.FloatField(help_text="Weight in kg")

    # Actual calories consumed
    calories_consumed = models.FloatField(
        default=0, help_text="Total calories consumed"
    )

    # Actual macros consumed
    protein_consumed = models.FloatField(
        default=0, help_text="Protein consumed (grams)"
    )
    carbs_consumed = models.FloatField(default=0, help_text="Carbs consumed (grams)")
    fat_consumed = models.FloatField(default=0, help_text="Fat consumed (grams)")

    # Water intake
    water_intake = models.FloatField(default=0, help_text="Water consumed (liters)")

    # Notes
    notes = models.TextField(blank=True, help_text="Any notes for the day")

    # Mood/energy
    energy_level = models.IntegerField(
        null=True,
        blank=True,
        help_text="Energy level (1-10)",
        choices=[(i, str(i)) for i in range(1, 11)],
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Log for {self.log_date} - {self.weight}kg"

    def get_calorie_difference(self):
        """Calculate difference between consumed and target"""
        return self.calories_consumed - self.profile.daily_calorie_target

    def get_weight_difference(self):
        """Calculate difference from starting weight"""
        return self.weight - self.profile.weight

    class Meta:
        verbose_name = "Daily Log"
        verbose_name_plural = "Daily Logs"
        ordering = ["-log_date"]
        unique_together = ["profile", "log_date"]
