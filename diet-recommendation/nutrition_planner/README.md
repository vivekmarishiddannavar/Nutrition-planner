# Personalized Nutrition and Diet Recommendation Web Application

![Django](https://img.shields.io/badge/Django-6.0+-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A Django-based web application that calculates user caloric needs using the **Mifflin-St Jeor equation** and generates personalized 7-day meal plans based on dietary preferences. Features progress tracking and data visualization with Chart.js.

---

## 🌟 Features

### Core Functionality
- ✅ **BMR & TDEE Calculation** - Uses scientifically proven Mifflin-St Jeor equation
- ✅ **Personalized Meal Plans** - AI-powered meal generation respecting dietary preferences
- ✅ **Macro Tracking** - Protein, Carbs, Fats targets based on user goals
- ✅ **Daily Logging** - Track weight, calories, water intake, and energy levels
- ✅ **Progress Visualization** - Interactive charts with Chart.js
- ✅ **Weekly Reports** - Comprehensive nutrition summaries
- ✅ **Dietary Preferences** - Support for Vegan, Vegetarian, Keto, Paleo, Gluten-Free
- ✅ **Adaptive System** - Regenerate meal plans with one click

### Tech Stack
- **Backend**: Python 3.8+, Django 6.0+
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Database**: SQLite (default)
- **Visualization**: Chart.js 4.4.0

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /d/Projects/nutrition_planner
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Start Server
```bash
python manage.py runserver
```

### 4. Open Browser
```
http://127.0.0.1:8000/
```

---

## 📊 How It Works

### 1. BMR Calculation (Mifflin-St Jeor Equation)

**For Men:**
```
BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
```

**For Women:**
```
BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161
```

### 2. TDEE Calculation

```
TDEE = BMR × Activity Multiplier
```

**Activity Multipliers:**
- Sedentary: 1.2
- Lightly Active: 1.375
- Moderately Active: 1.55
- Very Active: 1.725
- Extra Active: 1.9

### 3. Calorie Target Based on Goal

- **Lose Weight**: TDEE - 500 calories
- **Maintain Weight**: TDEE
- **Gain Weight**: TDEE + 500 calories

### 4. Macro Distribution

| Goal | Protein | Carbs | Fat |
|------|---------|-------|-----|
| Lose Weight | 40% | 30% | 30% |
| Maintain | 30% | 40% | 30% |
| Gain Weight | 30% | 50% | 20% |

**Keto Diet Special**: 25% Protein, 5% Carbs, 70% Fat

---

## 📁 Project Structure

```
nutrition_planner/
├── manage.py
├── requirements.txt
├── README.md
│
├── nutrition_planner/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── diet/                        # Main app
│   ├── models.py               # UserProfile, MealPlan, DailyLog
│   ├── views.py                # All views (11 functions)
│   ├── urls.py                 # App URLs
│   ├── admin.py                # Admin configuration
│   ├── diet_engine.py          # AI recommendation engine
│   ├── migrations/             # Database migrations
│   └── templates/diet/         # HTML templates
│       ├── base.html           # Master template
│       ├── setup.html          # Profile setup
│       ├── dashboard.html      # Main dashboard
│       ├── log.html            # Daily logging
│       ├── log_history.html    # Log history
│       ├── report.html         # Weekly report
│       ├── meal_plan_detail.html
│       ├── about.html
│       └── reset.html
│
└── static/diet/                # Static files
    ├── css/
    └── js/
```

---

## 🍽️ Food Database

The application includes a comprehensive food database with **30+ food items** organized by:
- Meal type compatibility (Breakfast, Lunch, Dinner, Snack)
- Macro nutrients (calories, protein, carbs, fat)
- Dietary tags (vegan, vegetarian, gluten-free, paleo)

**Sample Foods:**
- Proteins: Chicken Breast, Salmon, Eggs, Greek Yogurt, Tuna, Tofu
- Carbs: Brown Rice, Quinoa, Oats, Sweet Potato, Banana
- Fats: Avocado, Almonds, Olive Oil, Peanut Butter
- Vegetables: Broccoli, Spinach, Mixed Veggies

---

## 🎨 UI/UX Features

### Health-Focused Color Scheme
- Primary Green: #28a745
- Secondary Green: #20c997
- Dark Green: #155724
- Light Green: #d4edda

### Key UI Elements
- **Stat Cards**: Display current weight, daily targets, averages
- **Progress Bars**: Goal progress visualization
- **Meal Cards**: Color-coded by meal type
- **Macro Badges**: Quick visual reference for macros
- **Interactive Charts**: Weight and calorie tracking

---

## 📱 Pages & Features

### 1. Setup Page (`/`)
- Collect user health data (age, gender, weight, height)
- Activity level selection
- Goal selection (lose/maintain/gain)
- Dietary preference selection
- Real-time BMR/TDEE preview

### 2. Dashboard (`/dashboard/`)
- Today's meal plan with macro breakdown
- Progress stats (current weight, avg calories, days tracked)
- Weight progress chart
- Calorie intake vs target chart
- Quick action buttons

### 3. Daily Log (`/log/`)
- Log daily weight
- Track calories consumed
- Log macro intake (protein, carbs, fat)
- Water intake tracking
- Energy level (1-10 scale)
- Notes section

### 4. Weekly Report (`/report/weekly/`)
- 7-day averages (weight, calories, macros)
- Daily breakdown table
- Meal plans for the week
- Print functionality

### 5. About Page (`/about/`)
- How the calculations work
- Features overview
- Important disclaimer
- Technology stack info

---

## 🔧 Available Views

| View | URL | Purpose |
|------|-----|---------|
| `setup` | `/` | Create user profile |
| `update_profile` | `/update/` | Update existing profile |
| `dashboard` | `/dashboard/` | Main dashboard |
| `regenerate` | `/regenerate/` | Regenerate meal plan |
| `log` | `/log/` | Daily logging |
| `log_history` | `/log/history/` | View log history |
| `weekly_report` | `/report/weekly/` | Weekly nutrition report |
| `meal_plan_detail` | `/meal-plan/<id>/` | View meal plan details |
| `about` | `/about/` | About page |
| `reset` | `/reset/` | Reset profile |

---

## 🧪 Test Scenarios

### Test 1: Weight Loss Goal
**Input:**
- Male, 30 years, 85kg, 175cm
- Activity: Moderately Active
- Goal: Lose Weight
- Diet: Balanced

**Expected Output:**
- BMR: ~1748 cal/day
- TDEE: ~2710 cal/day
- Daily Target: ~2210 cal/day
- Macros: P: 221g, C: 166g, F: 74g

### Test 2: Vegetarian Diet
**Input:**
- Female, 25 years, 60kg, 165cm
- Activity: Lightly Active
- Goal: Maintain Weight
- Diet: Vegetarian

**Expected Output:**
- Only vegetarian foods in meal plan
- BMR: ~1338 cal/day
- TDEE: ~1840 cal/day
- Daily Target: ~1840 cal/day

---

## 📈 Database Models

### UserProfile
- Physical metrics (age, gender, weight, height)
- Activity level and goals
- Dietary preferences
- Calculated BMR, TDEE, calorie targets
- Macro targets (protein, carbs, fat)

### MealPlan
- Linked to user profile
- Plan date
- Meal data (JSON field)
- Daily totals (calories, protein, carbs, fat)
- Adherence tracking

### DailyLog
- Linked to user profile
- Log date
- Weight and calories consumed
- Macro intake
- Water intake
- Energy level
- Notes

---

## 🎯 Customization

### Adding New Foods

Edit `diet/diet_engine.py` and add to `FoodDatabase.FOODS`:

```python
'your_food_key': {
    'name': 'Your Food Name (serving size)',
    'calories': 100,
    'protein': 10,
    'carbs': 20,
    'fat': 5,
    'meal_types': ['breakfast', 'lunch', 'dinner'],
    'tags': ['vegan', 'vegetarian', 'gluten_free']
},
```

### Adjusting Macro Ratios

Edit `NutritionCalculator.MACRO_RATIOS` in `diet_engine.py`:

```python
MACRO_RATIOS = {
    'lose': {'protein': 0.40, 'carbs': 0.30, 'fat': 0.30},
    'maintain': {'protein': 0.30, 'carbs': 0.40, 'fat': 0.30},
    'gain': {'protein': 0.30, 'carbs': 0.50, 'fat': 0.20},
}
```

---

## ⚠️ Medical Disclaimer

**IMPORTANT**: This tool provides general nutritional guidance and should NOT replace professional medical advice, diagnosis, or treatment.

- ❌ NOT a substitute for professional medical advice
- ❌ NOT suitable for treating medical conditions
- ✅ YES for educational and informational purposes
- ✅ YES as a starting point for discussions with healthcare providers

**Always consult with a registered dietitian or healthcare provider before making significant changes to your diet.**

---

## 🔒 Privacy & Data

- All data stored locally in SQLite database
- No external API calls
- No data collection or transmission
- Session-based profile tracking
- Users can reset/delete their data anytime

---

## 🚀 Production Deployment

### Switch to PostgreSQL

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nutrition_planner',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Configure Static Files

```bash
python manage.py collectstatic
```

### Use Gunicorn

```bash
pip install gunicorn
gunicorn nutrition_planner.wsgi:application
```

---

## 📞 Support

For issues or questions:

1. Check the About page in the app
2. Review code comments in each file
3. Verify Django is properly installed
4. Check browser console for JavaScript errors

---

## 📝 File Details

### Core Files
- **[diet_engine.py](diet/diet_engine.py)** (700+ lines)
  - BMR/TDEE calculations
  - Food database with 30+ items
  - Meal generation algorithm

- **[models.py](diet/models.py)** (184 lines)
  - UserProfile, MealPlan, DailyLog models
  - Helper methods and metadata

- **[views.py](diet/views.py)** (518 lines)
  - 11 view functions
  - Chart data preparation
  - Progress calculations

### Templates
- **[base.html](diet/templates/diet/base.html)** - Master template with health theme
- **[setup.html](diet/templates/diet/setup.html)** - Profile setup with live calculations
- **[dashboard.html](diet/templates/diet/dashboard.html)** - Main dashboard with Chart.js
- **[log.html](diet/templates/diet/log.html)** - Daily logging form
- **[report.html](diet/templates/diet/report.html)** - Weekly nutrition report
- **[about.html](diet/templates/diet/about.html)** - About page with formula explanations

---

## ✅ Feature Checklist

- [x] Django project and app structure
- [x] Database models (UserProfile, MealPlan, DailyLog)
- [x] BMR/TDEE calculation using Mifflin-St Jeor
- [x] Food database with 30+ items
- [x] Meal plan generation
- [x] Dietary preference support (Vegan, Vegetarian, Keto, Paleo, GF)
- [x] Goal-based adjustments (lose/maintain/gain)
- [x] Profile setup page
- [x] Dashboard with meal plans
- [x] Chart.js integration
- [x] Daily logging functionality
- [x] Weekly reports
- [x] Progress visualization
- [x] Responsive design
- [x] Health-focused green/white theme
- [x] Admin interface
- [x] Documentation

---

## 🎉 Success!

Your Personalized Nutrition and Diet Recommendation application is complete!

**What it can do:**
- Calculate accurate BMR and TDEE using Mifflin-St Jeor equation
- Generate personalized meal plans
- Track weight and calorie intake
- Visualize progress with interactive charts
- Support multiple dietary preferences
- Adapt to weight loss, maintenance, or gain goals

**Start using it now!** 🚀

---

**Project**: Personalized Nutrition Planner
**Status**: COMPLETE
**Version**: 1.0.0
**Date**: 2025-02-04
**Tech Stack**: Django 6.0.1, Python 3.8+, Bootstrap 5.3.2, Chart.js 4.4.0
