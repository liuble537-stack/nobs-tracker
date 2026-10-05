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


# 3. Safe JSON Loader
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


# 4. Safe Session Initialization
if "user_data" not in st.session_state:
    st.session_state["user_data"] = load_data(USER_FILE, {})

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None


# 5. Core App Logic
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
                        "habits": [],
                        "streaks": {},
                        "meals": {},
                        "favorites": {},
                    }
                    save_data(USER_FILE, st.session_state["user_data"])

                st.rerun()
    else:
        user = st.session_state["current_user"]
        user_info = st.session_state["user_data"].get(
            user, {"habits": [], "streaks": {}, "meals": {}, "favorites": {}}
        )

        # Ensure dictionary keys exist
        if "meals" not in user_info:
            user_info["meals"] = {}
        if "favorites" not in user_info:
            user_info["favorites"] = {}

        st.subheader(f"User: {user}")

        # --- 1. Calendar & Date Selection ---
        selected_date = st.date_input("📅 Select Date", date.today())
        date_str = selected_date.strftime("%Y-%m-%d")

        # Load meals for selected date
        daily_meals = user_info["meals"].get(date_str, [])
        total_cals = sum(int(m["calories"]) for m in daily_meals)

        st.markdown(f"### 📊 Total for {date_str}: **{total_cals} kcal**")

        # Table Display
        if daily_meals:
            st.table(
                [
                    {"Meal": m["name"], "Calories (kcal)": m["calories"]}
                    for m in daily_meals
                ]
            )
            if st.button("Clear Date Logs"):
                user_info["meals"][date_str] = []
                st.session_state["user_data"][user] = user_info
                save_data(USER_FILE, st.session_state["user_data"])
                st.rerun()
        else:
            st.info("No meals logged for this date yet.")

        st.markdown("---")

        # --- 2. Quick-Autofill from Favorites ---
        st.subheader("⭐ Favorite Meals")
        fav_dict = user_info["favorites"]
        fav_options = ["-- Select a Favorite --"] + list(fav_dict.keys())

        selected_fav = st.selectbox("Quick-fill meal:", fav_options)

        default_name = ""
        default_cals = 0

        if selected_fav != "-- Select a Favorite --":
            default_name = selected_fav
            default_cals = int(fav_dict[selected_fav])

        # --- 3. Log Meal Form ---
        st.subheader("➕ Log Meal")
        with st.form("add_meal_form", clear_on_submit=True):
            meal_name = st.text_input("Meal Name", value=default_name)
            meal_cals = st.number_input(
                "Calories", min_value=0, value=default_cals, step=10
            )
            save_as_fav = st.checkbox("Save to Favorites for quick access")

            submitted = st.form_submit_button("Add Meal to Table")

            if submitted:
                if meal_name.strip():
                    new_meal = {
                        "name": meal_name.strip(),
                        "calories": int(meal_cals),
                    }

                    if date_str not in user_info["meals"]:
                        user_info["meals"][date_str] = []

                    user_info["meals"][date_str].append(new_meal)

                    if save_as_fav:
                        user_info["favorites"][meal_name.strip()] = int(
                            meal_cals
                        )

                    st.session_state["user_data"][user] = user_info
                    save_data(USER_FILE, st.session_state["user_data"])
                    st.success(
                        f"Added {meal_name} ({meal_cals} kcal) to {date_str}!"
                    )
                    st.rerun()
                else:
                    st.warning("Please enter a meal name.")

        st.markdown("---")
        if st.button("Log Out"):
            st.session_state["logged_in"] = False
            st.session_state["current_user"] = None
            st.rerun()


# Global reconnect crash protection
if __name__ == "__main__":
    try:
        run_app()
    except Exception:
        st.toast("Session reconnected.", icon="🔄")
        st.rerun()