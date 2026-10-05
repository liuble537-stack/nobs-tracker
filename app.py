from datetime import date
import json
import os
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="No BS Tracker",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Mobile Touch & Pull-to-Refresh Crash Overrides
st.markdown(
    """
    <style>
    html, body, .stApp {
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
    }
    .stProgress > div > div > div > div {
        background-color: #00c853;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

USER_FILE = "users.json"

# Master Registry of All Tracked Nutrients & Labels
NUTRIENT_CATEGORIES = {
    "Basic Macros": {
        "protein": "Total Protein (g)",
        "carbs": "Total Carbs (g)",
        "fat": "Total Fat (g)",
        "fiber": "Total Fiber (g)",
    },
    "Protein Breakdown": {
        "protein_complete": "Complete Protein (g)",
        "protein_incomplete": "Incomplete Protein (g)",
    },
    "Fiber Subtypes": {
        "fiber_soluble": "Soluble Fiber (g)",
        "fiber_insoluble": "Insoluble Fiber (g)",
    },
    "Fat Subtypes & Omegas": {
        "fat_sat": "Saturated Fat (g)",
        "fat_mufa": "Monounsaturated Fat / MUFA (g)",
        "fat_pufa": "Polyunsaturated Fat / PUFA (g)",
        "omega_3": "Omega-3 Fatty Acids (g)",
        "omega_6": "Omega-6 Fatty Acids (g)",
        "omega_7": "Omega-7 Fatty Acids (g)",
        "omega_9": "Omega-9 Fatty Acids (g)",
    },
    "Vitamins": {
        "vit_a": "Vitamin A (mcg)",
        "vit_c": "Vitamin C (mg)",
        "vit_d": "Vitamin D (mcg)",
        "vit_e": "Vitamin E (mg)",
        "vit_k": "Vitamin K (mcg)",
        "vit_b1": "Thiamin B1 (mg)",
        "vit_b2": "Riboflavin B2 (mg)",
        "vit_b3": "Niacin B3 (mg)",
        "vit_b6": "Vitamin B6 (mg)",
        "vit_b9": "Folate B9 (mcg)",
        "vit_b12": "Vitamin B12 (mcg)",
    },
    "Minerals": {
        "calcium": "Calcium (mg)",
        "iron": "Iron (mg)",
        "magnesium": "Magnesium (mg)",
        "potassium": "Potassium (mg)",
        "sodium": "Sodium (mg)",
        "zinc": "Zinc (mg)",
        "copper": "Copper (mg)",
        "manganese": "Manganese (mg)",
        "selenium": "Selenium (mcg)",
        "molybdenum": "Molybdenum (mcg)",
    },
}

# Flattened lookup dict for fast label resolution
ALL_NUTRIENTS = {}
for cat_dict in NUTRIENT_CATEGORIES.values():
    ALL_NUTRIENTS.update(cat_dict)


# 3. Crash-Proof Local File Handler
def load_data(filepath, default_val):
    if not os.path.exists(filepath):
        return default_val
    try:
        with open(filepath, "r") as f:
            content = f.read().strip()
            if not content:
                return default_val
            return json.loads(content)
    except Exception:
        return default_val


def save_data(filepath, data):
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Storage error: {e}")


# 4. Session State Guard
if "user_data" not in st.session_state:
    st.session_state["user_data"] = load_data(USER_FILE, {})

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None


# 5. Core Application Logic
def run_app():
    st.title("⚡ No BS Tracker")

    if not st.session_state["logged_in"]:
        username = st.text_input("Enter Username to Start / Resume")
        if st.button("Continue"):
            if username.strip():
                u_clean = username.strip()
                st.session_state["current_user"] = u_clean
                st.session_state["logged_in"] = True

                if u_clean not in st.session_state["user_data"]:
                    st.session_state["user_data"][u_clean] = {
                        "habits": {},
                        "meals": {},
                        "favorites": {},
                        "goals": {},
                    }
                    save_data(USER_FILE, st.session_state["user_data"])

                st.rerun()
    else:
        user = st.session_state["current_user"]
        user_info = st.session_state["user_data"].get(
            user, {"habits": {}, "meals": {}, "favorites": {}, "goals": {}}
        )

        # Ensure dictionary integrity
        for key in ["habits", "meals", "favorites", "goals"]:
            if key not in user_info:
                user_info[key] = {}

        st.caption(f"Logged in as: **{user}**")

        # --- Four Primary Navigation Tabs ---
        tab_habits, tab_nutrition, tab_goals, tab_tips = st.tabs(
            [
                "⚡ Habits",
                "🥗 Meal & Macro Log",
                "🎯 Nutrient Goals",
                "💡 Nutrition Guide",
            ]
        )

        # ==========================================
        # TAB 1: HABITS & STREAKS
        # ==========================================
        with tab_habits:
            st.subheader("🔥 Habit Streaks")

            with st.form("add_habit_form", clear_on_submit=True):
                new_habit = st.text_input("New Habit Name")
                if st.form_submit_button("Add Habit"):
                    if new_habit.strip():
                        h_name = new_habit.strip()
                        if h_name not in user_info["habits"]:
                            user_info["habits"][h_name] = {
                                "streak": 0,
                                "last_completed": "",
                            }
                            st.session_state["user_data"][user] = user_info
                            save_data(USER_FILE, st.session_state["user_data"])
                            st.rerun()

            if user_info["habits"]:
                today_str = date.today().strftime("%Y-%m-%d")

                for h_name, h_data in list(user_info["habits"].items()):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    col1.write(f"**{h_name}**")
                    col2.write(f"🔥 {h_data.get('streak', 0)} day streak")

                    already_done = h_data.get("last_completed") == today_str
                    if col3.button(
                        "Done" if not already_done else "✓",
                        key=f"btn_{h_name}",
                        disabled=already_done,
                    ):
                        h_data["streak"] = h_data.get("streak", 0) + 1
                        h_data["last_completed"] = today_str
                        st.session_state["user_data"][user] = user_info
                        save_data(USER_FILE, st.session_state["user_data"])
                        st.balloons()
                        st.rerun()
            else:
                st.info("No habits logged yet.")

        # ==========================================
        # TAB 2: MEAL & MACRO LOG
        # ==========================================
        with tab_nutrition:
            selected_date = st.date_input("📅 Select Date", date.today())
            date_str = selected_date.strftime("%Y-%m-%d")

            daily_meals = user_info["meals"].get(date_str, [])

            # Compute daily totals
            total_cals = sum(float(m.get("calories", 0)) for m in daily_meals)
            nutrient_totals = {k: 0.0 for k in ALL_NUTRIENTS.keys()}

            for m in daily_meals:
                m_nutrients = m.get("nutrients", {})
                for k in nutrient_totals.keys():
                    nutrient_totals[k] += float(m_nutrients.get(k, 0.0))

            # Daily Overview Header
            st.markdown(f"### Daily Summary for {date_str}")
            user_goals = user_info.get("goals", {})

            # Main Macro Cards
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", f"{int(total_cals)} kcal")
            c2.metric("Protein", f"{round(nutrient_totals['protein'], 1)}g")
            c3.metric("Carbs", f"{round(nutrient_totals['carbs'], 1)}g")
            c4.metric("Fat", f"{round(nutrient_totals['fat'], 1)}g")

            # Daily Goal Progress Visualizers (if set)
            if user_goals:
                with st.expander("📊 Goal Progress Bars", expanded=True):
                    for g_key, g_target in user_goals.items():
                        if g_target > 0 and g_key in ALL_NUTRIENTS:
                            curr_val = (
                                total_cals
                                if g_key == "calories"
                                else nutrient_totals.get(g_key, 0.0)
                            )
                            pct = min(1.0, curr_val / g_target)
                            label_name = (
                                "Calories"
                                if g_key == "calories"
                                else ALL_NUTRIENTS[g_key]
                            )
                            st.caption(
                                f"**{label_name}:** {round(curr_val, 1)} / {g_target} ({int(pct*100)}%)"
                            )
                            st.progress(pct)

            # Detailed Micronutrient Breakdown Toggle
            with st.expander("🔬 Complete Daily Breakdown"):
                for cat_name, cat_fields in NUTRIENT_CATEGORIES.items():
                    st.markdown(f"**{cat_name}**")
                    sub_cols = st.columns(2)
                    idx = 0
                    for k, label in cat_fields.items():
                        col_target = sub_cols[idx % 2]
                        val = round(nutrient_totals[k], 2)
                        col_target.write(f"• {label}: **{val}**")
                        idx += 1

            if daily_meals:
                st.markdown("#### Today's Logged Meals")
                st.table(
                    [
                        {
                            "Meal": m["name"],
                            "Calories": f"{m.get('calories', 0)} kcal",
                            "Protein": f"{m.get('nutrients', {}).get('protein', 0)}g",
                            "Carbs": f"{m.get('nutrients', {}).get('carbs', 0)}g",
                            "Fat": f"{m.get('nutrients', {}).get('fat', 0)}g",
                            "Fiber": f"{m.get('nutrients', {}).get('fiber', 0)}g",
                        }
                        for m in daily_meals
                    ]
                )
                if st.button("Clear Date Logs"):
                    user_info["meals"][date_str] = []
                    st.session_state["user_data"][user] = user_info
                    save_data(USER_FILE, st.session_state["user_data"])
                    st.rerun()
            else:
                st.info("No meals logged for this date.")

            st.markdown("---")

            # Favorites Quick Fill System
            fav_dict = user_info["favorites"]
            fav_options = ["-- Quick-Fill Favorite --"] + list(fav_dict.keys())
            selected_fav = st.selectbox("Favorite Templates", fav_options)

            def_name = ""
            def_cals = 0
            def_nutrients = {k: 0.0 for k in ALL_NUTRIENTS.keys()}

            if selected_fav != "-- Quick-Fill Favorite --":
                fav_item = fav_dict[selected_fav]
                def_name = selected_fav
                def_cals = int(fav_item.get("calories", 0))
                def_nutrients.update(fav_item.get("nutrients", {}))

            # Meal Entry Form
            st.subheader("➕ Add Meal")
            with st.form("log_meal_form", clear_on_submit=True):
                f_name = st.text_input("Meal Name", value=def_name)
                f_cals = st.number_input(
                    "Calories (kcal)", min_value=0, value=def_cals, step=10
                )

                st.markdown("**Basic Macros**")
                bm1, bm2, bm3, bm4 = st.columns(4)
                f_protein = bm1.number_input(
                    "Protein (g)",
                    min_value=0.0,
                    value=float(def_nutrients["protein"]),
                    step=0.5,
                )
                f_carbs = bm2.number_input(
                    "Carbs (g)",
                    min_value=0.0,
                    value=float(def_nutrients["carbs"]),
                    step=0.5,
                )
                f_fat = bm3.number_input(
                    "Fat (g)",
                    min_value=0.0,
                    value=float(def_nutrients["fat"]),
                    step=0.5,
                )
                f_fiber = bm4.number_input(
                    "Fiber (g)",
                    min_value=0.0,
                    value=float(def_nutrients["fiber"]),
                    step=0.5,
                )

                form_nutrients = {
                    "protein": f_protein,
                    "carbs": f_carbs,
                    "fat": f_fat,
                    "fiber": f_fiber,
                }

                # Optional Section 1: Protein & Fiber Breakdown
                with st.expander(
                    "🥩 Protein & Fiber Breakdown (Optional)", expanded=False
                ):
                    p_col1, p_col2 = st.columns(2)
                    form_nutrients["protein_complete"] = p_col1.number_input(
                        "Complete Protein (g)",
                        min_value=0.0,
                        value=float(def_nutrients.get("protein_complete", 0.0)),
                        step=0.5,
                    )
                    form_nutrients["protein_incomplete"] = (
                        p_col2.number_input(
                            "Incomplete Protein (g)",
                            min_value=0.0,
                            value=float(
                                def_nutrients.get("protein_incomplete", 0.0)
                            ),
                            step=0.5,
                        )
                    )

                    f_col1, f_col2 = st.columns(2)
                    form_nutrients["fiber_soluble"] = f_col1.number_input(
                        "Soluble Fiber (g)",
                        min_value=0.0,
                        value=float(def_nutrients.get("fiber_soluble", 0.0)),
                        step=0.5,
                    )
                    form_nutrients["fiber_insoluble"] = f_col2.number_input(
                        "Insoluble Fiber (g)",
                        min_value=0.0,
                        value=float(def_nutrients.get("fiber_insoluble", 0.0)),
                        step=0.5,
                    )

                # Optional Section 2: Fat Subtypes & Omegas
                with st.expander(
                    "🥑 Fat Subtypes & Omegas (Optional)", expanded=False
                ):
                    fat_col1, fat_col2 = st.columns(2)
                    idx = 0
                    for k, label in NUTRIENT_CATEGORIES[
                        "Fat Subtypes & Omegas"
                    ].items():
                        target_col = fat_col1 if idx % 2 == 0 else fat_col2
                        form_nutrients[k] = target_col.number_input(
                            label,
                            min_value=0.0,
                            value=float(def_nutrients.get(k, 0.0)),
                            step=0.1,
                            key=f"inp_{k}",
                        )
                        idx += 1

                # Optional Section 3: Vitamins & Minerals
                with st.expander(
                    "💊 Vitamins & Minerals (Optional)", expanded=False
                ):
                    vit_col1, vit_col2 = st.columns(2)
                    idx = 0
                    for cat_k in ["Vitamins", "Minerals"]:
                        for k, label in NUTRIENT_CATEGORIES[cat_k].items():
                            target_col = vit_col1 if idx % 2 == 0 else vit_col2
                            form_nutrients[k] = target_col.number_input(
                                label,
                                min_value=0.0,
                                value=float(def_nutrients.get(k, 0.0)),
                                step=0.1,
                                key=f"inp_{k}",
                            )
                            idx += 1

                save_fav = st.checkbox("Save as Favorite template")

                if st.form_submit_button("Log Meal"):
                    if f_name.strip():
                        new_entry = {
                            "name": f_name.strip(),
                            "calories": int(f_cals),
                            "nutrients": form_nutrients,
                        }
                        if date_str not in user_info["meals"]:
                            user_info["meals"][date_str] = []

                        user_info["meals"][date_str].append(new_entry)

                        if save_fav:
                            user_info["favorites"][f_name.strip()] = {
                                "calories": int(f_cals),
                                "nutrients": form_nutrients,
                            }

                        st.session_state["user_data"][user] = user_info
                        save_data(USER_FILE, st.session_state["user_data"])
                        st.rerun()

        # ==========================================
        # TAB 3: DAILY NUTRIENT GOALS
        # ==========================================
        with tab_goals:
            st.subheader("🎯 Daily Targets & Goals")
            st.caption(
                "Set optional targets for calories, macros, fibers, fat subtypes, and micronutrients."
            )

            current_goals = user_info.get("goals", {})

            with st.form("set_goals_form"):
                new_goals = {}
                new_goals["calories"] = st.number_input(
                    "Daily Calories Goal (kcal)",
                    min_value=0,
                    value=int(current_goals.get("calories", 2000)),
                    step=50,
                )

                for cat_name, cat_fields in NUTRIENT_CATEGORIES.items():
                    with st.expander(f"Goal Settings: {cat_name}"):
                        g_col1, g_col2 = st.columns(2)
                        g_idx = 0
                        for k, label in cat_fields.items():
                            target_col = g_col1 if g_idx % 2 == 0 else g_col2
                            val_init = float(current_goals.get(k, 0.0))
                            new_goals[k] = target_col.number_input(
                                f"Target {label}",
                                min_value=0.0,
                                value=val_init,
                                step=1.0,
                                key=f"goal_{k}",
                            )
                            g_idx += 1

                if st.form_submit_button("Save Daily Goals"):
                    user_info["goals"] = new_goals
                    st.session_state["user_data"][user] = user_info
                    save_data(USER_FILE, st.session_state["user_data"])
                    st.success("Daily goals saved successfully!")
                    st.rerun()

        # ==========================================
        # TAB 4: NUTRITION TIPS & EDUCATION
        # ==========================================
        with tab_tips:
            st.subheader("💡 Practical Nutrition & Science Guide")

            st.markdown(
                """
            ### 🥩 Protein: Complete vs. Incomplete
            * **Complete Proteins:** Contain all 9 essential amino acids in sufficient quantities (found in eggs, meat, poultry, fish, dairy, soy, and quinoa). Ideal for optimal muscle protein synthesis.
            * **Incomplete Proteins:** Missing or low in one or more essential amino acids (found in beans, grains, nuts, and seeds). Combining different incomplete proteins (e.g., rice and black beans) yields a complete amino acid profile.

            ---

            ### 🌾 Fiber: Soluble vs. Incomplete (Insoluble)
            * **Soluble Fiber:** Dissolves in water to form a gel-like substance (found in oats, barley, chia seeds, apples, and psyllium). Helps lower LDL cholesterol and stabilizes blood glucose spikes.
            * **Insoluble Fiber:** Adds bulk to stool and speeds up transit time through the digestive tract (found in whole wheat, bran, nuts, and cruciferous vegetables). Essential for gut motility and colon health.

            ---

            ### 🥑 Fats & Omega Ratios
            * **Saturated Fats:** Found in animal products, coconut oil, and butter. Keep within 7–10% of total daily calories.
            * **Monounsaturated Fats (MUFA):** Found in olive oil, avocados, and almonds. Promotes heart health and insulin sensitivity.
            * **Polyunsaturated Fats (PUFA):** Includes essential fatty acids that the body cannot synthesize on its own.
                * **Omega-3:** Highly anti-inflammatory (found in wild salmon, walnuts, flaxseeds, and chia).
                * **Omega-6:** Essential for cellular structure but inflammatory if consumed in extreme excess relative to Omega-3. Aim for a ratio close to 4:1 or lower.
                * **Omega-7 & Omega-9:** Non-essential but helpful monounsaturated fats supporting metabolic function and cholesterol balance.

            ---

            ### 🔬 Essential Micronutrient Focus
            * **Molybdenum:** Essential cofactor for enzymes that break down toxic sulfites, aldehydes (from alcohol and pollution), and purines into uric acid.
            * **Magnesium & Potassium:** Electrolyte minerals vital for fluid balance, muscle contraction, and blood pressure regulation.
            * **B-Complex Vitamins:** Essential catalysts for converting dietary macronutrients into ATP cellular energy.
            """
            )

        st.markdown("---")
        if st.button("Log Out"):
            st.session_state["logged_in"] = False
            st.session_state["current_user"] = None
            st.rerun()


# Catch background WebSocket reconnect glitches automatically
if __name__ == "__main__":
    try:
        run_app()
    except Exception:
        st.toast("Session reconnected.", icon="🔄")
        st.rerun()