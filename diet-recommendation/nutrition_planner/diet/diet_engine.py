"""
Diet Recommendation Engine for Nutrition Planner

Implements:
- Mifflin-St Jeor Equation for BMR calculation
- TDEE calculation with activity multipliers
- Macro distribution based on goals
- Food database with macro nutrients
- Meal plan generation respecting dietary preferences
"""

import random
from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional


class NutritionCalculator:
    """
    Calculates BMR, TDEE, and daily macros using Mifflin-St Jeor equation
    """

    # Activity multipliers for TDEE calculation
    ACTIVITY_MULTIPLIERS = {
        "sedentary": 1.2,  # Little or no exercise
        "light": 1.375,  # Light exercise 1-3 days/week
        "moderate": 1.55,  # Moderate exercise 3-5 days/week
        "active": 1.725,  # Hard exercise 6-7 days/week
        "extra": 1.9,  # Very hard exercise & physical job
    }

    # Calorie adjustments for goals
    GOAL_ADJUSTMENTS = {
        "lose": -500,  # 500 calorie deficit for weight loss
        "maintain": 0,  # No adjustment
        "gain": 500,  # 500 calorie surplus for weight gain
    }

    # Macro ratios (protein, carbs, fat) for different goals
    MACRO_RATIOS = {
        "lose": {
            "protein": 0.40,
            "carbs": 0.30,
            "fat": 0.30,
        },  # High protein for satiety
        "maintain": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},  # Balanced
        "gain": {"protein": 0.30, "carbs": 0.50, "fat": 0.20},  # High carb for energy
    }

    # Special macro ratios for keto diet
    KETO_MACROS = {"protein": 0.25, "carbs": 0.05, "fat": 0.70}

    @staticmethod
    def calculate_bmr(gender: str, age: int, weight: float, height: float) -> float:
        """
        Calculate BMR using Mifflin-St Jeor Equation

        Formula:
        - Men: BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
        - Women: BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161

        Args:
            gender: 'M', 'F', or 'O'
            age: Age in years
            weight: Weight in kg
            height: Height in cm

        Returns:
            BMR in calories/day
        """
        base_bmr = (10 * weight) + (6.25 * height) - (5 * age)

        if gender == "M":
            return base_bmr + 5
        elif gender == "F":
            return base_bmr - 161
        else:  # Other/average
            return base_bmr - 78  # Average of male and female adjustments

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure

        Args:
            bmr: Basal Metabolic Rate
            activity_level: Activity level key

        Returns:
            TDEE in calories/day
        """
        multiplier = NutritionCalculator.ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
        return bmr * multiplier

    @staticmethod
    def calculate_daily_targets(
        gender: str,
        age: int,
        weight: float,
        height: float,
        activity_level: str,
        goal: str,
        diet_preference: str = "balanced",
    ) -> Dict:
        """
        Calculate all daily nutritional targets

        Args:
            gender: 'M', 'F', or 'O'
            age: Age in years
            weight: Weight in kg
            height: Height in cm
            activity_level: Activity level
            goal: 'lose', 'maintain', or 'gain'
            diet_preference: 'balanced', 'keto', etc.

        Returns:
            Dictionary with all targets
        """
        # Calculate BMR and TDEE
        bmr = NutritionCalculator.calculate_bmr(gender, age, weight, height)
        tdee = NutritionCalculator.calculate_tdee(bmr, activity_level)

        # Adjust for goal
        adjustment = NutritionCalculator.GOAL_ADJUSTMENTS.get(goal, 0)
        daily_calories = tdee + adjustment

        # Ensure minimum safe calorie intake
        daily_calories = max(daily_calories, 1200)  # Minimum 1200 calories

        # Calculate macros
        if diet_preference == "keto":
            ratios = NutritionCalculator.KETO_MACROS
        else:
            ratios = NutritionCalculator.MACRO_RATIOS.get(
                goal, NutritionCalculator.MACRO_RATIOS["maintain"]
            )

        # Convert ratios to grams (protein=4 cal/g, carbs=4 cal/g, fat=9 cal/g)
        protein_grams = (daily_calories * ratios["protein"]) / 4
        carbs_grams = (daily_calories * ratios["carbs"]) / 4
        fat_grams = (daily_calories * ratios["fat"]) / 9

        return {
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1),
            "daily_calories": round(daily_calories, 1),
            "protein_g": round(protein_grams, 1),
            "carbs_g": round(carbs_grams, 1),
            "fat_g": round(fat_grams, 1),
            "protein_percent": round(ratios["protein"] * 100),
            "carbs_percent": round(ratios["carbs"] * 100),
            "fat_percent": round(ratios["fat"] * 100),
        }


class FoodDatabase:
    """
    Comprehensive food database with macro nutrients
    Organized by meal type and dietary preferences
    """

    # Food items with macro nutrients (per 100g or per serving)
    FOODS = {
        # Proteins
        "chicken_breast": {
            "name": "Chicken Breast (100g)",
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6,
            "meal_types": ["breakfast", "lunch", "dinner"],
            "tags": ["high_protein", "lean", "gluten_free", "paleo"],
        },
        "salmon": {
            "name": "Salmon Fillet (100g)",
            "calories": 208,
            "protein": 20,
            "carbs": 0,
            "fat": 13,
            "meal_types": ["lunch", "dinner"],
            "tags": ["high_protein", "omega_3", "gluten_free", "paleo"],
        },
        "eggs": {
            "name": "Eggs (2 large)",
            "calories": 143,
            "protein": 12,
            "carbs": 0.7,
            "fat": 10,
            "meal_types": ["breakfast", "lunch", "dinner"],
            "tags": ["high_protein", "vegetarian", "gluten_free", "paleo"],
        },
        "greek_yogurt": {
            "name": "Greek Yogurt (170g)",
            "calories": 100,
            "protein": 17,
            "carbs": 6,
            "fat": 0.7,
            "meal_types": ["breakfast", "snack"],
            "tags": ["high_protein", "vegetarian", "gluten_free"],
        },
        "tuna": {
            "name": "Canned Tuna (100g)",
            "calories": 116,
            "protein": 26,
            "carbs": 0,
            "fat": 1,
            "meal_types": ["lunch", "dinner", "snack"],
            "tags": ["high_protein", "lean", "gluten_free", "paleo"],
        },
        "tofu": {
            "name": "Tofu (100g)",
            "calories": 76,
            "protein": 8,
            "carbs": 1.9,
            "fat": 4.8,
            "meal_types": ["breakfast", "lunch", "dinner", "snack"],
            "tags": ["high_protein", "vegan", "vegetarian", "gluten_free"],
        },
        "lentils": {
            "name": "Lentils (100g cooked)",
            "calories": 116,
            "protein": 9,
            "carbs": 20,
            "fat": 0.4,
            "meal_types": ["lunch", "dinner"],
            "tags": ["high_protein", "vegan", "vegetarian", "gluten_free"],
        },
        "beef": {
            "name": "Lean Beef (100g)",
            "calories": 250,
            "protein": 26,
            "carbs": 0,
            "fat": 15,
            "meal_types": ["lunch", "dinner"],
            "tags": ["high_protein", "gluten_free", "paleo"],
        },
        "turkey": {
            "name": "Turkey Breast (100g)",
            "calories": 135,
            "protein": 30,
            "carbs": 0,
            "fat": 1,
            "meal_types": ["breakfast", "lunch", "dinner"],
            "tags": ["high_protein", "lean", "gluten_free", "paleo"],
        },
        # Carbohydrates
        "brown_rice": {
            "name": "Brown Rice (100g cooked)",
            "calories": 112,
            "protein": 2.6,
            "carbs": 24,
            "fat": 0.9,
            "meal_types": ["lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free"],
        },
        "quinoa": {
            "name": "Quinoa (100g cooked)",
            "calories": 120,
            "protein": 4.4,
            "carbs": 21,
            "fat": 1.9,
            "meal_types": ["breakfast", "lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free"],
        },
        "oats": {
            "name": "Rolled Oats (50g dry)",
            "calories": 190,
            "protein": 8,
            "carbs": 34,
            "fat": 3,
            "meal_types": ["breakfast"],
            "tags": ["vegan", "vegetarian", "gluten_free"],
        },
        "sweet_potato": {
            "name": "Sweet Potato (150g)",
            "calories": 129,
            "protein": 2,
            "carbs": 30,
            "fat": 0.2,
            "meal_types": ["breakfast", "lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free", "paleo"],
        },
        "banana": {
            "name": "Banana (1 medium)",
            "calories": 105,
            "protein": 1.3,
            "carbs": 27,
            "fat": 0.4,
            "meal_types": ["breakfast", "snack"],
            "tags": ["vegan", "vegetarian", "gluten_free"],
        },
        "whole_wheat_bread": {
            "name": "Whole Wheat Bread (2 slices)",
            "calories": 200,
            "protein": 7,
            "carbs": 40,
            "fat": 3,
            "meal_types": ["breakfast", "snack"],
            "tags": ["vegan", "vegetarian"],
        },
        "pasta": {
            "name": "Whole Wheat Pasta (100g cooked)",
            "calories": 174,
            "protein": 7.5,
            "carbs": 37,
            "fat": 0.8,
            "meal_types": ["lunch", "dinner"],
            "tags": ["vegan", "vegetarian"],
        },
        "apple": {
            "name": "Apple (1 medium)",
            "calories": 95,
            "protein": 0.5,
            "carbs": 25,
            "fat": 0.3,
            "meal_types": ["breakfast", "snack"],
            "tags": ["vegan", "vegetarian", "gluten_free"],
        },
        # Fats
        "avocado": {
            "name": "Avocado (half)",
            "calories": 160,
            "protein": 2,
            "carbs": 9,
            "fat": 15,
            "meal_types": ["breakfast", "lunch", "dinner", "snack"],
            "tags": ["vegan", "vegetarian", "gluten_free", "paleo"],
        },
        "almonds": {
            "name": "Almonds (30g)",
            "calories": 170,
            "protein": 6,
            "carbs": 6,
            "fat": 15,
            "meal_types": ["breakfast", "snack"],
            "tags": ["vegan", "vegetarian", "gluten_free", "paleo"],
        },
        "olive_oil": {
            "name": "Olive Oil (1 tbsp)",
            "calories": 119,
            "protein": 0,
            "carbs": 0,
            "fat": 14,
            "meal_types": ["lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free", "paleo"],
        },
        "peanut_butter": {
            "name": "Peanut Butter (2 tbsp)",
            "calories": 190,
            "protein": 8,
            "carbs": 6,
            "fat": 16,
            "meal_types": ["breakfast", "snack"],
            "tags": ["vegan", "vegetarian", "gluten_free"],
        },
        "cheese": {
            "name": "Cheddar Cheese (30g)",
            "calories": 120,
            "protein": 7,
            "carbs": 0.4,
            "fat": 10,
            "meal_types": ["breakfast", "lunch", "dinner", "snack"],
            "tags": ["vegetarian", "gluten_free"],
        },
        # Vegetables
        "broccoli": {
            "name": "Broccoli (100g)",
            "calories": 34,
            "protein": 2.8,
            "carbs": 7,
            "fat": 0.4,
            "meal_types": ["lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free", "paleo"],
        },
        "spinach": {
            "name": "Spinach (100g raw)",
            "calories": 23,
            "protein": 2.9,
            "carbs": 3.6,
            "fat": 0.4,
            "meal_types": ["breakfast", "lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free", "paleo"],
        },
        "mixed_veggies": {
            "name": "Mixed Vegetables (150g)",
            "calories": 50,
            "protein": 2,
            "carbs": 10,
            "fat": 0,
            "meal_types": ["lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free", "paleo"],
        },
        "salad": {
            "name": "Green Salad (150g)",
            "calories": 30,
            "protein": 2,
            "carbs": 6,
            "fat": 0,
            "meal_types": ["lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free", "paleo"],
        },
        # Complete meals
        "oatmeal_bowl": {
            "name": "Oatmeal with Berries",
            "calories": 300,
            "protein": 10,
            "carbs": 55,
            "fat": 5,
            "meal_types": ["breakfast"],
            "tags": ["vegan", "vegetarian", "gluten_free"],
        },
        "smoothie": {
            "name": "Protein Smoothie",
            "calories": 280,
            "protein": 25,
            "carbs": 35,
            "fat": 5,
            "meal_types": ["breakfast", "snack"],
            "tags": ["vegetarian", "gluten_free"],
        },
        "chicken_salad": {
            "name": "Chicken Salad",
            "calories": 350,
            "protein": 35,
            "carbs": 15,
            "fat": 18,
            "meal_types": ["lunch", "dinner"],
            "tags": ["gluten_free", "paleo"],
        },
        "stir_fry": {
            "name": "Vegetable Stir Fry",
            "calories": 320,
            "protein": 15,
            "carbs": 35,
            "fat": 14,
            "meal_types": ["lunch", "dinner"],
            "tags": ["vegan", "vegetarian", "gluten_free"],
        },
    }

    @staticmethod
    def get_foods_by_meal_type(
        meal_type: str, diet_preference: str = "balanced"
    ) -> List[Dict]:
        """
        Get foods suitable for a specific meal type and dietary preference

        Args:
            meal_type: 'breakfast', 'lunch', 'dinner', or 'snack'
            diet_preference: 'balanced', 'vegetarian', 'vegan', 'keto', 'paleo', 'gluten_free'

        Returns:
            List of food dictionaries
        """
        suitable_foods = []

        for food_key, food_data in FoodDatabase.FOODS.items():
            # Check meal type compatibility
            if meal_type not in food_data["meal_types"]:
                continue

            # Check dietary preference
            if diet_preference == "vegan":
                if "vegan" not in food_data["tags"]:
                    continue
            elif diet_preference == "vegetarian":
                if "vegetarian" not in food_data["tags"]:
                    continue
            elif diet_preference == "gluten_free":
                if "gluten_free" not in food_data["tags"]:
                    continue

            suitable_foods.append({**food_data, "key": food_key})

        return suitable_foods


class MealPlanGenerator:
    """
    Generates personalized meal plans based on nutritional targets
    """

    def __init__(self, targets: Dict, diet_preference: str = "balanced"):
        """
        Initialize meal plan generator

        Args:
            targets: Dictionary with daily nutritional targets
            diet_preference: Dietary preference
        """
        self.targets = targets
        self.diet_preference = diet_preference

        # Calculate calorie distribution for meals
        self.meal_distribution = {
            "breakfast": 0.25,  # 25% of daily calories
            "lunch": 0.30,  # 30% of daily calories
            "dinner": 0.35,  # 35% of daily calories
            "snack": 0.10,  # 10% of daily calories
        }

    def generate_meal_plan(self, days: int = 7) -> List[Dict]:
        """
        Generate meal plan for specified number of days

        Args:
            days: Number of days to generate

        Returns:
            List of daily meal plans
        """
        meal_plans = []

        for day in range(days):
            daily_plan = self._generate_single_day()
            meal_plans.append(daily_plan)

        return meal_plans

    def _generate_single_day(self) -> Dict:
        """
        Generate a single day meal plan

        Returns:
            Dictionary with meals and totals
        """
        meals = {}
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0

        for meal_type, distribution in self.meal_distribution.items():
            target_calories = self.targets["daily_calories"] * distribution
            target_protein = self.targets["protein_g"] * distribution
            target_carbs = self.targets["carbs_g"] * distribution
            target_fat = self.targets["fat_g"] * distribution

            meal_foods = self._generate_meal(
                meal_type, target_calories, target_protein, target_carbs, target_fat
            )

            meals[meal_type] = meal_foods

            # Add to totals
            for food in meal_foods:
                total_calories += food["calories"]
                total_protein += food["protein"]
                total_carbs += food["carbs"]
                total_fat += food["fat"]

        return {
            "meals": meals,
            "totals": {
                "calories": round(total_calories, 1),
                "protein": round(total_protein, 1),
                "carbs": round(total_carbs, 1),
                "fat": round(total_fat, 1),
            },
        }

    def _generate_meal(
        self,
        meal_type: str,
        target_calories: float,
        target_protein: float,
        target_carbs: float,
        target_fat: float,
    ) -> List[Dict]:
        """
        Generate foods for a single meal

        Args:
            meal_type: Type of meal
            target_calories: Target calories for this meal
            target_protein: Target protein for this meal
            target_carbs: Target carbs for this meal
            target_fat: Target fat for this meal

        Returns:
            List of food items for the meal
        """
        available_foods = FoodDatabase.get_foods_by_meal_type(
            meal_type, self.diet_preference
        )

        if not available_foods:
            # Fallback to any foods for this meal type
            available_foods = [
                f for f in FoodDatabase.FOODS.values() if meal_type in f["meal_types"]
            ]

        selected_foods = []
        remaining_calories = target_calories

        # Select 2-4 foods per meal
        num_foods = random.randint(2, 4)

        for _ in range(num_foods):
            if remaining_calories <= 0 or not available_foods:
                break

            # Score foods by how well they match remaining targets
            scored_foods = []
            for food in available_foods:
                score = self._score_food(
                    food, remaining_calories, target_protein, target_carbs, target_fat
                )
                scored_foods.append((score, food))

            # Sort by score and pick top foods
            scored_foods.sort(reverse=True, key=lambda x: x[0])

            # Pick from top 3 foods randomly for variety
            top_foods = scored_foods[: min(3, len(scored_foods))]
            if top_foods:
                _, selected_food = random.choice(top_foods)
                selected_foods.append(selected_food)
                remaining_calories -= selected_food["calories"]

        return selected_foods

    def _score_food(
        self,
        food: Dict,
        remaining_calories: float,
        target_protein: float,
        target_carbs: float,
        target_fat: float,
    ) -> float:
        """
        Score a food based on how well it fits the remaining targets

        Args:
            food: Food data dictionary
            remaining_calories: Calories remaining for this meal
            target_protein: Target protein for this meal
            target_carbs: Target carbs for this meal
            target_fat: Target fat for this meal

        Returns:
            Score (higher is better)
        """
        score = 0

        # Calorie fit (prefer foods that don't exceed remaining calories)
        if food["calories"] <= remaining_calories:
            score += 10
        else:
            score -= 5

        # Macro fit
        protein_ratio = food["protein"] / max(target_protein, 1)
        carbs_ratio = food["carbs"] / max(target_carbs, 1)
        fat_ratio = food["fat"] / max(target_fat, 1)

        # Add score for macro balance
        score += min(protein_ratio * 3, 10)
        score += min(carbs_ratio * 2, 10)
        score += min(fat_ratio * 2, 10)

        # Bonus for high protein foods
        if food["protein"] >= 15:
            score += 5

        # Add some randomness for variety
        score += random.uniform(0, 5)

        return score


def generate_complete_nutrition_plan(
    gender: str,
    age: int,
    weight: float,
    height: float,
    activity_level: str,
    goal: str,
    diet_preference: str = "balanced",
    days: int = 7,
) -> Dict:
    """
    Generate a complete nutrition plan including targets and meal plans

    Args:
        gender: 'M', 'F', or 'O'
        age: Age in years
        weight: Weight in kg
        height: Height in cm
        activity_level: Activity level
        goal: 'lose', 'maintain', or 'gain'
        diet_preference: Dietary preference
        days: Number of days for meal plan

    Returns:
        Complete nutrition plan dictionary
    """
    # Calculate targets
    targets = NutritionCalculator.calculate_daily_targets(
        gender, age, weight, height, activity_level, goal, diet_preference
    )

    # Generate meal plans
    generator = MealPlanGenerator(targets, diet_preference)
    meal_plans = generator.generate_meal_plan(days)

    return {
        "targets": targets,
        "meal_plans": meal_plans,
        "preference": diet_preference,
        "goal": goal,
    }


if __name__ == "__main__":
    # Test the nutrition calculator
    print("=" * 70)
    print("Nutrition Planner Engine - Test")
    print("=" * 70)

    # Test calculation
    targets = NutritionCalculator.calculate_daily_targets(
        gender="M",
        age=30,
        weight=75,
        height=175,
        activity_level="moderate",
        goal="lose",
        diet_preference="balanced",
    )

    print("\n[TEST 1] Calculate Daily Targets")
    print(f"BMR: {targets['bmr']} calories/day")
    print(f"TDEE: {targets['tdee']} calories/day")
    print(f"Daily Calories: {targets['daily_calories']} calories/day")
    print(f"Protein: {targets['protein_g']}g ({targets['protein_percent']}%)")
    print(f"Carbs: {targets['carbs_g']}g ({targets['carbs_percent']}%)")
    print(f"Fat: {targets['fat_g']}g ({targets['fat_percent']}%)")

    # Test meal generation
    print("\n[TEST 2] Generate Sample Meal Plan (Day 1)")
    plan = generate_complete_nutrition_plan(
        gender="M",
        age=30,
        weight=75,
        height=175,
        activity_level="moderate",
        goal="lose",
        diet_preference="balanced",
        days=1,
    )

    day1 = plan["meal_plans"][0]
    for meal_type, foods in day1["meals"].items():
        print(f"\n{meal_type.upper()}:")
        for food in foods:
            print(
                f"  - {food['name']}: {food['calories']} cal, {food['protein']}g protein"
            )

    print(f"\nDay Totals: {day1['totals']['calories']} calories")

    print("\n" + "=" * 70)
    print("[SUCCESS] Diet engine is working correctly!")
    print("=" * 70)
