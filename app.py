from datetime import date
import json
import os
import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="No BS Tracker",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Prevent mobile pull-to-refresh
st.markdown(
    """
    <style>
    html, body, .stApp {
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

USER_FILE = "users.json"

# List of tracked nutrients
NUTRIENT_KEYS = {
    # Macros
    "protein": "Protein (g)",
    "carbs": "Carbs (g)",
    "fat": "Fat (g)",
    # Vitamins
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
    # Minerals
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
}


# 3. Safe Storage Helpers
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


# 4. Session State Setup
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
                st.session_state["current_user"] = username.strip()
                st.session_state["logged_in"] = True

                if username not in st.session_state["user_data"]:
                    st.session_state["user_data"][username] = {
                        "habits": {},
                        "meals": {},
                        "favorites": {},
                    }
                    save_data(USER_FILE, st.session_state["user_data"])

                st.rerun()
    else:
        user = st.session_state["current_user"]
        user_info = st.session_state["user_data"].get(
            user, {"habits": {}, "meals": {}, "favorites": {}}
        )

        # Structure checks
        if "habits" not in user_info:
            user_info["habits"] = {}
        if "meals" not in user_info:
            user_info["meals"] = {}
        if "favorites" not in user_info:
            user_info["favorites"] = {}

        st.caption(f"Logged in as: **{user}**")

        # --- Tab Navigation ---
        tab_habits, tab_nutrition = st.tabs(
            ["⚡ Habit & Streaks", "🥗 Nutrition & Micronutrients"]
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
                        habit_name = new_habit.strip()
                        if habit_name not in user_info["habits"]:
                            user_info["habits"][habit_name] = {
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
                st.info("No habits added yet.")

        # ==========================================
        # TAB 2: NUTRITION & MICRONUTRIENTS
        # ==========================================
        with tab_nutrition:
            selected_date = st.date_input("📅 Select Date", date.today())
            date_str = selected_date.strftime("%Y-%m-%d")

            daily_meals = user_info["meals"].get(date_str, [])

            # Compute totals safely
            total_cals = sum(float(m.get("calories", 0)) for m in daily_meals)
            nutrient_totals = {k: 0.0 for k in NUTRIENT_KEYS.keys()}

            for m in daily_meals:
                m_nutrients = m.get("nutrients", {})
                for k in nutrient_totals.keys():
                    nutrient_totals[k] += float(m_nutrients.get(k, 0))

            st.markdown(f"### Daily Summary for {date_str}")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Calories", f"{int(total_cals)} kcal")
            m_col2.metric("Protein", f"{round(nutrient_totals['protein'], 1)}g")
            m_col3.metric("Carbs", f"{round(nutrient_totals['carbs'], 1)}g")
            m_col4.metric("Fat", f"{round(nutrient_totals['fat'], 1)}g")

            with st.expander("💊 Daily Vitamin & Mineral Totals"):
                v_cols = st.columns(2)
                v_index = 0
                for k, label in NUTRIENT_KEYS.items():
                    if k not in ["protein", "carbs", "fat"]:
                        col_target = v_cols[v_index % 2]
                        val = round(nutrient_totals[k], 2)
                        col_target.write(f"• **{label}:** {val}")
                        v_index += 1

            if daily_meals:
                st.markdown("#### Logged Meals")
                st.table(
                    [
                        {
                            "Meal": m["name"],
                            "Calories": f"{m.get('calories', 0)} kcal",
                            "Protein": f"{m.get('nutrients', {}).get('protein', 0)}g",
                            "Carbs": f"{m.get('nutrients', {}).get('carbs', 0)}g",
                            "Fat": f"{m.get('nutrients', {}).get('fat', 0)}g",
                        }
                        for m in daily_meals
                    ]
                )
                if st.button("Clear Today's Meals"):
                    user_info["meals"][date_str] = []
                    st.session_state["user_data"][user] = user_info
                    save_data(USER_FILE, st.session_state["user_data"])
                    st.rerun()
            else:
                st.info("No meals logged for this date.")

            st.markdown("---")

            # Favorites Quick Fill
            fav_dict = user_info["favorites"]
            fav_options = ["-- Quick-Fill Favorite --"] + list(fav_dict.keys())
            selected_fav = st.selectbox("Favorite Templates", fav_options)

            def_name = ""
            def_cals = 0
            def_nutrients = {k: 0.0 for k in NUTRIENT_KEYS.keys()}

            if selected_fav != "-- Quick-Fill Favorite --":
                fav_item = fav_dict[selected_fav]
                def_name = selected_fav
                def_cals = int(fav_item.get("calories", 0))
                def_nutrients.update(fav_item.get("nutrients", {}))

            # Meal Entry Form
            st.subheader("➕ Add Meal & Micronutrients")
            with st.form("log_meal_form", clear_on_submit=True):
                f_name = st.text_input("Meal Name", value=def_name)
                f_cals = st.number_input(
                    "Calories (kcal)", min_value=0, value=def_cals, step=10
                )

                st.markdown("**Macros**")
                c1, c2, c3 = st.columns(3)
                f_protein = c1.number_input(
                    "Protein (g)",
                    min_value=0.0,
                    value=float(def_nutrients["protein"]),
                    step=0.5,
                )
                f_carbs = c2.number_input(
                    "Carbs (g)",
                    min_value=0.0,
                    value=float(def_nutrients["carbs"]),
                    step=0.5,
                )
                f_fat = c3.number_input(
                    "Fat (g)",
                    min_value=0.0,
                    value=float(def_nutrients["fat"]),
                    step=0.5,
                )

                with st.expander(
                    "🔬 Vitamins & Minerals Breakdown", expanded=False
                ):
                    form_nutrients = {
                        "protein": f_protein,
                        "carbs": f_carbs,
                        "fat": f_fat,
                    }

                    vit_col1, vit_col2 = st.columns(2)
                    idx = 0
                    for k, label in NUTRIENT_KEYS.items():
                        if k not in ["protein", "carbs", "fat"]:
                            target_col = vit_col1 if idx % 2 == 0 else vit_col2
                            val_init = float(def_nutrients.get(k, 0.0))
                            form_nutrients[k] = target_col.number_input(
                                label,
                                min_value=0.0,
                                value=val_init,
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

        st.markdown("---")
        if st.button("Log Out"):
            st.session_state["logged_in"] = False
            st.session_state["current_user"] = None
            st.rerun()


if __name__ == "__main__":
    try:
        run_app()
    except Exception:
        st.toast("Session reconnected.", icon="🔄")
        st.rerun()