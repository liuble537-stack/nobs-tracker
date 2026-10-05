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
        tab_habits, tab_calories = st.tabs(
            ["⚡ Habit & Streak Tracker", "🥗 Calorie & Meal Log"]
        )

        # ==========================================
        # TAB 1: HABITS & STREAKS
        # ==========================================
        with tab_habits:
            st.subheader("🔥 Habit Streaks")

            # Add new habit
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

            # Display active habits
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
                st.info("No habits added yet. Create your first one above!")

        # ==========================================
        # TAB 2: CALORIES & MEALS
        # ==========================================
        with tab_calories:
            selected_date = st.date_input("📅 Select Date", date.today())
            date_str = selected_date.strftime("%Y-%m-%d")

            daily_meals = user_info["meals"].get(date_str, [])
            total_cals = sum(int(m["calories"]) for m in daily_meals)

            st.markdown(f"### Total for {date_str}: **{total_cals} kcal**")

            if daily_meals:
                st.table(
                    [
                        {"Meal": m["name"], "Calories": f"{m['calories']} kcal"}
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
            if selected_fav != "-- Quick-Fill Favorite --":
                def_name = selected_fav
                def_cals = int(fav_dict[selected_fav])

            # Meal Entry Form
            with st.form("log_meal_form", clear_on_submit=True):
                meal_name = st.text_input("Meal Name", value=def_name)
                meal_cals = st.number_input(
                    "Calories", min_value=0, value=def_cals, step=10
                )
                save_fav = st.checkbox("Save as Favorite template")

                if st.form_submit_button("Log Meal"):
                    if meal_name.strip():
                        new_entry = {
                            "name": meal_name.strip(),
                            "calories": int(meal_cals),
                        }
                        if date_str not in user_info["meals"]:
                            user_info["meals"][date_str] = []

                        user_info["meals"][date_str].append(new_entry)

                        if save_fav:
                            user_info["favorites"][meal_name.strip()] = int(
                                meal_cals
                            )

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