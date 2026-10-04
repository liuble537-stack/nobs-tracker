from datetime import date, timedelta
import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="No BS Tracker",
    page_icon="💪",
    layout="wide",
)

# --- PERSISTENT USER STORAGE ---
USERS_FILE = "users.json"


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"ignas": "bulk2700"}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# --- PERSISTENT STREAK STORAGE ---
STREAK_FILE = "streak.json"


def load_streak_data():
    if os.path.exists(STREAK_FILE):
        try:
            with open(STREAK_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {"streak": 0, "last_date": None}
    return {"streak": 0, "last_date": None}


def save_streak_data(streak, last_date_str):
    with open(STREAK_FILE, "w") as f:
        json.dump({"streak": streak, "last_date": last_date_str}, f)


def check_active_streak():
    data = load_streak_data()
    last_date_str = data.get("last_date")
    streak = data.get("streak", 0)

    if not last_date_str:
        return 0

    today = date.today()
    last_date = date.fromisoformat(last_date_str)

    if last_date == today or last_date == (today - timedelta(days=1)):
        return streak
    else:
        return 0


def record_meal_logged():
    data = load_streak_data()
    last_date_str = data.get("last_date")
    streak = data.get("streak", 0)
    today = date.today()
    today_str = str(today)

    if last_date_str == today_str:
        return streak

    if last_date_str:
        last_date = date.fromisoformat(last_date_str)
        if today - last_date == timedelta(days=1):
            streak += 1
        elif today - last_date > timedelta(days=1):
            streak = 1
    else:
        streak = 1

    save_streak_data(streak, today_str)
    return streak


# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "food_list" not in st.session_state:
    st.session_state.food_list = []

# --- AUTHENTICATION PORTAL ---
if not st.session_state.authenticated:
    st.title("💪 No BS Tracker Portal")

    col1, col2 = st.columns([1, 2])
    with col1:
        tab_login, tab_signup = st.tabs(["🔑 Log In", "📝 Sign Up"])
        users = load_users()

        with tab_login:
            with st.form("login_form"):
                username_input = st.text_input("Username").strip().lower()
                password_input = st.text_input("Password", type="password")
                login_button = st.form_submit_button(
                    "Log In", use_container_width=True
                )

                if login_button:
                    if (
                        username_input in users
                        and users[username_input] == password_input
                    ):
                        st.session_state.authenticated = True
                        st.session_state.username = username_input
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_signup:
            with st.form("signup_form"):
                new_user = st.text_input("Choose Username").strip().lower()
                new_pass = st.text_input("Choose Password", type="password")
                confirm_pass = st.text_input(
                    "Confirm Password", type="password"
                )
                signup_button = st.form_submit_button(
                    "Create Account", use_container_width=True
                )

                if signup_button:
                    if not new_user or not new_pass:
                        st.warning("Please fill in all fields.")
                    elif new_user in users:
                        st.error("Username already taken! Try another.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    else:
                        users[new_user] = new_pass
                        save_users(users)
                        st.success("Account created! Switch to Log In tab.")

    st.stop()

# --- MAIN DASHBOARD ---
current_streak = check_active_streak()

# SIDEBAR: USER, STREAK & CUSTOM TARGETS
with st.sidebar:
    st.write(f"👤 Logged in as: **{st.session_state.username}**")
    st.info(f"🔥 **Current Streak:** {current_streak} Day(s)")

    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

    st.markdown("---")
    st.header("🎯 Daily Targets")

    # Macro Targets
    daily_calories = st.number_input(
        "Daily Calorie Goal (kcal)", value=2700, step=50
    )
    st.subheader("Macro Split %")
    p_pct = st.number_input("Protein %", value=20)
    c_pct = st.number_input("Carbs %", value=55)
    f_pct = st.number_input("Fat %", value=25)

    target_p = (daily_calories * (p_pct / 100)) / 4
    target_c = (daily_calories * (c_pct / 100)) / 4
    target_f = (daily_calories * (f_pct / 100)) / 9

    # Customizable Micro & Fiber Targets
    with st.expander("⚙️ Customize Fiber & Micro Targets"):
        st.markdown("**Fiber Target**")
        target_fiber = st.number_input("Fiber Goal (g)", value=30, step=5)

        st.markdown("**Vitamin Goals**")
        target_vit_a = st.number_input("Vit A Goal (mcg)", value=900, step=50)
        target_vit_c = st.number_input("Vit C Goal (mg)", value=90.0, step=5.0)
        target_vit_d = st.number_input("Vit D Goal (mcg)", value=20.0, step=1.0)
        target_vit_e = st.number_input("Vit E Goal (mg)", value=15.0, step=1.0)
        target_vit_k = st.number_input("Vit K Goal (mcg)", value=120.0, step=5.0)
        target_b1 = st.number_input("B1 Thiamine Goal (mg)", value=1.2, step=0.1)
        target_b2 = st.number_input("B2 Riboflavin Goal (mg)", value=1.3, step=0.1)
        target_b3 = st.number_input("B3 Niacin Goal (mg)", value=16.0, step=1.0)
        target_b5 = st.number_input("B5 Pantothenic Goal (mg)", value=5.0, step=0.5)
        target_b6 = st.number_input("B6 Pyridoxine Goal (mg)", value=1.7, step=0.1)
        target_b7 = st.number_input("B7 Biotin Goal (mcg)", value=30.0, step=5.0)
        target_b9 = st.number_input("B9 Folate Goal (mcg)", value=400.0, step=25.0)
        target_b12 = st.number_input("B12 Cobalamin Goal (mcg)", value=2.4, step=0.2)

        st.markdown("**Mineral Goals**")
        target_calcium = st.number_input("Calcium Goal (mg)", value=1000, step=50)
        target_iron = st.number_input("Total Iron Goal (mg)", value=18.0, step=1.0)
        target_magnesium = st.number_input("Magnesium Goal (mg)", value=420, step=10)
        target_potassium = st.number_input("Potassium Goal (mg)", value=3400, step=100)
        target_sodium = st.number_input("Sodium Goal (mg)", value=2300, step=100)
        target_zinc = st.number_input("Zinc Goal (mg)", value=11.0, step=0.5)
        target_phosphorus = st.number_input("Phosphorus Goal (mg)", value=700, step=50)
        target_chloride = st.number_input("Chloride Goal (mg)", value=2300, step=100)
        target_copper = st.number_input("Copper Goal (mg)", value=0.9, step=0.1)
        target_manganese = st.number_input("Manganese Goal (mg)", value=2.3, step=0.1)
        target_selenium = st.number_input("Selenium Goal (mcg)", value=55.0, step=5.0)
        target_iodine = st.number_input("Iodine Goal (mcg)", value=150.0, step=10.0)
        target_chromium = st.number_input("Chromium Goal (mcg)", value=35.0, step=5.0)
        target_molybdenum = st.number_input("Molybdenum Goal (mcg)", value=45.0, step=5.0)

    st.markdown("---")
    st.write(f"🥩 **Protein Goal:** {target_p:.0f}g")
    st.write(f"🍞 **Carbs Goal:** {target_c:.0f}g")
    st.write(f"🥑 **Fat Goal:** {target_f:.0f}g")
    st.write(f"🌾 **Fiber Goal:** {target_fiber:.0f}g")

# HEADER
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("💪 No BS Tracker")
with header_col2:
    st.metric(label="🔥 Tracking Streak", value=f"{current_streak} Days")

# NUTRITION & BIOAVAILABILITY TIPS EXPANDER
with st.expander("💡 Bioavailability & Nutrition Tips"):
    st.markdown("""
    * **Complete vs. Incomplete Protein:** Complete proteins (meat, eggs, dairy, soy) contain all 9 essential amino acids. Incomplete proteins (grains, nuts, beans) lack one or more, but can be combined throughout the day.
    * **Non-Heme Iron + Vitamin C:** Plant-based iron (non-heme from oats, beans, spinach) is absorbed significantly better when eaten alongside **Vitamin C** (citrus, bell peppers, berries).
    * **Fat-Soluble Vitamins + Healthy Fats:** Vitamins **A, D, E, and K** require dietary fats (e.g., olive oil, eggs, nuts, avocados) to be absorbed by your body.
    * **Calcium vs. Iron:** Avoid consuming calcium-rich foods or supplements at the exact same time as high-iron meals, as calcium inhibits iron absorption.
    """)

# LOGGING FORM
with st.form("add_food_form", clear_on_submit=True):
    st.subheader("➕ Log a Meal")

    # Main Macros Row (including Complete & Incomplete Protein)
    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 2])
    with col1:
        food_name = st.text_input(
            "Food Item", placeholder="e.g., Steak, Eggs & Oats"
        )
    with col2:
        calories = st.number_input("Calories", min_value=0, value=0, step=10)
    with col3:
        complete_p = st.number_input(
            "Complete Protein (g)", min_value=0, value=0, step=1
        )
    with col4:
        incomplete_p = st.number_input(
            "Incomplete Protein (g)", min_value=0, value=0, step=1
        )
    with col5:
        carbs = st.number_input("Carbs (g)", min_value=0, value=0, step=1)
    with col6:
        fat = st.number_input("Fat (g)", min_value=0, value=0, step=1)

    # Detailed Micros & Fat Types Expander
    with st.expander("🌿 Optional: Fiber, Fats/Omegas, Vitamins & Minerals"):
        tab_fiber, tab_fats, tab_vits, tab_mins = st.tabs(
            ["🌾 Fiber", "🥑 Fats & Omegas", "💊 Vitamins", "🪨 Minerals"]
        )

        with tab_fiber:
            fc1, fc2 = st.columns(2)
            with fc1:
                sol_fiber = st.number_input(
                    "Soluble Fiber (g)", min_value=0.0, value=0.0, step=0.5
                )
            with fc2:
                insol_fiber = st.number_input(
                    "Insoluble Fiber (g)", min_value=0.0, value=0.0, step=0.5
                )

        with tab_fats:
            fat_col1, fat_col2 = st.columns(2)
            with fat_col1:
                st.markdown("**Fat Types**")
                sat_fat = st.number_input(
                    "Saturated Fat (g)", min_value=0.0, value=0.0, step=0.5
                )
                mufa_fat = st.number_input(
                    "MUFA (Monounsaturated) (g)",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                )
                pufa_fat = st.number_input(
                    "PUFA (Polyunsaturated) (g)",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                )
            with fat_col2:
                st.markdown("**Omega Fatty Acids**")
                omega3 = st.number_input(
                    "Omega-3 (g)", min_value=0.0, value=0.0, step=0.1
                )
                omega6 = st.number_input(
                    "Omega-6 (g)", min_value=0.0, value=0.0, step=0.1
                )
                omega7 = st.number_input(
                    "Omega-7 (g)", min_value=0.0, value=0.0, step=0.1
                )
                omega9 = st.number_input(
                    "Omega-9 (g)", min_value=0.0, value=0.0, step=0.1
                )

        with tab_vits:
            vc1, vc2, vc3, vc4 = st.columns(4)
            with vc1:
                vit_a = st.number_input("Vit A (mcg)", min_value=0, value=0, step=10)
                vit_c = st.number_input("Vit C (mg)", min_value=0.0, value=0.0, step=5.0)
                vit_d = st.number_input("Vit D (mcg)", min_value=0.0, value=0.0, step=1.0)
                vit_e = st.number_input("Vit E (mg)", min_value=0.0, value=0.0, step=0.5)
            with vc2:
                vit_k = st.number_input("Vit K (mcg)", min_value=0.0, value=0.0, step=1.0)
                vit_b1 = st.number_input("B1 Thiamine (mg)", min_value=0.0, value=0.0, step=0.1)
                vit_b2 = st.number_input("B2 Riboflavin (mg)", min_value=0.0, value=0.0, step=0.1)
                vit_b3 = st.number_input("B3 Niacin (mg)", min_value=0.0, value=0.0, step=0.5)
            with vc3:
                vit_b5 = st.number_input("B5 Pantothenic (mg)", min_value=0.0, value=0.0, step=0.5)
                vit_b6 = st.number_input("B6 Pyridoxine (mg)", min_value=0.0, value=0.0, step=0.1)
                vit_b7 = st.number_input("B7 Biotin (mcg)", min_value=0.0, value=0.0, step=1.0)
            with vc4:
                vit_b9 = st.number_input("B9 Folate (mcg)", min_value=0.0, value=0.0, step=10.0)
                vit_b12 = st.number_input("B12 Cobalamin (mcg)", min_value=0.0, value=0.0, step=0.1)

        with tab_mins:
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1:
                calcium = st.number_input("Calcium (mg)", min_value=0, value=0, step=25)
                heme_iron = st.number_input("Heme Iron (mg)", min_value=0.0, value=0.0, step=0.5)
                non_heme_iron = st.number_input("Non-Heme Iron (mg)", min_value=0.0, value=0.0, step=0.5)
                magnesium = st.number_input("Magnesium (mg)", min_value=0, value=0, step=10)
            with mc2:
                potassium = st.number_input("Potassium (mg)", min_value=0, value=0, step=50)
                sodium = st.number_input("Sodium (mg)", min_value=0, value=0, step=50)
                zinc = st.number_input("Zinc (mg)", min_value=0.0, value=0.0, step=0.5)
                phosphorus = st.number_input("Phosphorus (mg)", min_value=0, value=0, step=25)
            with mc3:
                chloride = st.number_input("Chloride (mg)", min_value=0, value=0, step=50)
                copper = st.number_input("Copper (mg)", min_value=0.0, value=0.0, step=0.1)
                manganese = st.number_input("Manganese (mg)", min_value=0.0, value=0.0, step=0.1)
                selenium = st.number_input("Selenium (mcg)", min_value=0.0, value=0.0, step=1.0)
            with mc4:
                iodine = st.number_input("Iodine (mcg)", min_value=0.0, value=0.0, step=5.0)
                chromium = st.number_input("Chromium (mcg)", min_value=0.0, value=0.0, step=1.0)
                molybdenum = st.number_input("Molybdenum (mcg)", min_value=0.0, value=0.0, step=1.0)

    submitted = st.form_submit_button("➕ Add Meal to Table", use_container_width=True)
    if submitted:
        if food_name.strip() != "":
            tot_p = complete_p + incomplete_p
            tot_fiber = sol_fiber + insol_fiber
            tot_iron = heme_iron + non_heme_iron
            st.session_state.food_list.append({
                "Food Item": food_name,
                "Calories": calories,
                "Total Protein (g)": tot_p,
                "Complete Protein (g)": complete_p,
                "Incomplete Protein (g)": incomplete_p,
                "Carbs (g)": carbs,
                "Fat (g)": fat,
                "Saturated Fat (g)": sat_fat,
                "MUFA (g)": mufa_fat,
                "PUFA (g)": pufa_fat,
                "Omega-3 (g)": omega3,
                "Omega-6 (g)": omega6,
                "Omega-7 (g)": omega7,
                "Omega-9 (g)": omega9,
                "Total Fiber (g)": tot_fiber,
                "Soluble Fiber (g)": sol_fiber,
                "Insoluble Fiber (g)": insol_fiber,
                "Total Iron (mg)": tot_iron,
                "Heme Iron (mg)": heme_iron,
                "Non-Heme Iron (mg)": non_heme_iron,
                "Vit A (mcg)": vit_a,
                "Vit C (mg)": vit_c,
                "Vit D (mcg)": vit_d,
                "Vit E (mg)": vit_e,
                "Vit K (mcg)": vit_k,
                "B1 (mg)": vit_b1,
                "B2 (mg)": vit_b2,
                "B3 (mg)": vit_b3,
                "B5 (mg)": vit_b5,
                "B6 (mg)": vit_b6,
                "B7 (mcg)": vit_b7,
                "B9 (mcg)": vit_b9,
                "B12 (mcg)": vit_b12,
                "Calcium (mg)": calcium,
                "Magnesium (mg)": magnesium,
                "Potassium (mg)": potassium,
                "Sodium (mg)": sodium,
                "Zinc (mg)": zinc,
                "Phosphorus (mg)": phosphorus,
                "Chloride (mg)": chloride,
                "Copper (mg)": copper,
                "Manganese (mg)": manganese,
                "Selenium (mcg)": selenium,
                "Iodine (mcg)": iodine,
                "Chromium (mcg)": chromium,
                "Molybdenum (mcg)": molybdenum,
            })
            record_meal_logged()
            st.rerun()
        else:
            st.warning("Please enter a food name first.")

# --- DISPLAY TABLE & TOTALS ---
if st.session_state.food_list:
    df = pd.DataFrame(st.session_state.food_list)

    tot_cal = df["Calories"].sum()
    tot_p = df["Total Protein (g)"].sum()
    tot_comp_p = df["Complete Protein (g)"].sum()
    tot_incomp_p = df["Incomplete Protein (g)"].sum()
    tot_c = df["Carbs (g)"].sum()
    tot_f = df["Fat (g)"].sum()
    tot_fib = df["Total Fiber (g)"].sum()

    st.markdown("---")
    st.subheader("📊 Today's Macro Progress")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Calories", f"{tot_cal} kcal", f"{daily_calories - tot_cal} left")
    m2.metric(
        "Total Protein",
        f"{tot_p}g",
        f"Comp: {tot_comp_p}g | Incomp: {tot_incomp_p}g",
    )
    m3.metric("Carbs", f"{tot_c}g", f"{target_c - tot_c:.0f}g left")
    m4.metric("Fat", f"{tot_f}g", f"{target_f - tot_f:.0f}g left")
    m5.metric("Fiber", f"{tot_fib:.1f}g", f"{target_fiber - tot_fib:.1f}g left")

    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- MICRONUTRIENT & FIBER PROGRESS VS TARGETS ---
    with st.expander("🎯 View Daily Fiber, Vitamin & Mineral Goal Progress"):
        # Vitamins Progress
        st.markdown("### 💊 Vitamin Progress")
        v_cols = st.columns(3)

        vit_goals = [
            ("Vit A (mcg)", "Vit A", target_vit_a, "mcg"),
            ("Vit C (mg)", "Vit C", target_vit_c, "mg"),
            ("Vit D (mcg)", "Vit D", target_vit_d, "mcg"),
            ("Vit E (mg)", "Vit E", target_vit_e, "mg"),
            ("Vit K (mcg)", "Vit K", target_vit_k, "mcg"),
            ("B1 (mg)", "B1 Thiamine", target_b1, "mg"),
            ("B2 (mg)", "B2 Riboflavin", target_b2, "mg"),
            ("B3 (mg)", "B3 Niacin", target_b3, "mg"),
            ("B5 (mg)", "B5 Pantothenic", target_b5, "mg"),
            ("B6 (mg)", "B6 Pyridoxine", target_b6, "mg"),
            ("B7 (mcg)", "B7 Biotin", target_b7, "mcg"),
            ("B9 (mcg)", "B9 Folate", target_b9, "mcg"),
            ("B12 (mcg)", "B12 Cobalamin", target_b12, "mcg"),
        ]

        for idx, (col_key, label, target, unit) in enumerate(vit_goals):
            val = df[col_key].sum()
            pct = min(1.0, val / target) if target > 0 else 0.0
            with v_cols[idx % 3]:
                st.write(f"**{label}:** {val:.1f} / {target} {unit}")
                st.progress(pct)

        st.markdown("---")
        # Minerals Progress
        st.markdown("### 🪨 Mineral Progress")
        m_cols = st.columns(3)

        min_goals = [
            ("Calcium (mg)", "Calcium", target_calcium, "mg"),
            ("Total Iron (mg)", "Total Iron", target_iron, "mg"),
            ("Magnesium (mg)", "Magnesium", target_magnesium, "mg"),
            ("Potassium (mg)", "Potassium", target_potassium, "mg"),
            ("Sodium (mg)", "Sodium", target_sodium, "mg"),
            ("Zinc (mg)", "Zinc", target_zinc, "mg"),
            ("Phosphorus (mg)", "Phosphorus", target_phosphorus, "mg"),
            ("Chloride (mg)", "Chloride", target_chloride, "mg"),
            ("Copper (mg)", "Copper", target_copper, "mg"),
            ("Manganese (mg)", "Manganese", target_manganese, "mg"),
            ("Selenium (mcg)", "Selenium", target_selenium, "mcg"),
            ("Iodine (mcg)", "Iodine", target_iodine, "mcg"),
            ("Chromium (mcg)", "Chromium", target_chromium, "mcg"),
            ("Molybdenum (mcg)", "Molybdenum", target_molybdenum, "mcg"),
        ]

        for idx, (col_key, label, target, unit) in enumerate(min_goals):
            val = df[col_key].sum()
            pct = min(1.0, val / target) if target > 0 else 0.0
            with m_cols[idx % 3]:
                st.write(f"**{label}:** {val:.1f} / {target} {unit}")
                st.progress(pct)

    if st.button("🗑️ Clear Today's Log"):
        st.session_state.food_list = []
        st.rerun()