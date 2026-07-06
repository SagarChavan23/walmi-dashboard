import io
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from utils.google_sheet import load_data
from utils.charts import *
from utils.auth import login, logout
from streamlit_option_menu import option_menu

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="WALMI Dashboard",
    page_icon="🍽️",
    layout="wide",
)

if not login():
    st.stop()

with st.sidebar:

    st.image(
        "https://img.icons8.com/color/96/restaurant.png",
        width=80
    )

    st.title("WALMI")

    selected = option_menu(
        menu_title=None,
        options=[
            "Dashboard",
            "Responses",
            "Analytics",
            "Export"
        ],
        icons=[
            "speedometer2",
            "table",
            "bar-chart",
            "download"
        ],
        default_index=0,
    )

    st.sidebar.divider()

    st.sidebar.success("🟢 Logged In")

    logout()

    st.sidebar.divider()

    st.sidebar.caption("Developed by Sagar Chavan\nVersion 1.0")

st_autorefresh(interval=30000, key="refresh")

# ----------------------------
# Custom CSS
# ----------------------------
st.markdown("""
<style>

.main{
    background-color:#F6F2E7;
}

.block-container{
    padding-top:2rem;
}

h1,h2,h3{
    color:#153731;
}

[data-testid="stMetric"]{
    background:white;
    border-radius:12px;
    padding:15px;
    border:1px solid #E4DDCC;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header
# ----------------------------

left, right = st.columns([8, 2])

with left:
    st.title("🍽️ WALMI Mess Feedback Dashboard")
    st.caption("Live Google Form Responses")
    st.caption(
        f"🟢 Last Updated : {datetime.now().strftime('%d %b %Y %I:%M:%S %p')}"
    )

with right:
    if st.button("🔄 Refresh"):
        st.toast("Refreshing data...")
        st.rerun()

st.divider()

# ----------------------------
# Load Data (needed on every page, so it stays global)
# ----------------------------

try:
    with st.spinner("Loading latest responses..."):
        df = load_data()
except Exception as e:
    st.error(f"Unable to load Google Sheet: {e}")
    st.stop()

# ----------------------------
# Find Columns Automatically
# ----------------------------

def find_column(keyword):
    for c in df.columns:
        if keyword.lower() in c.lower():
            return c
    return None

name_col = find_column("name")
dept_col = find_column("department")
meal_col = find_column("meal")
taste_col = find_column("taste")
hygiene_col = find_column("hygiene")
menu_col = find_column("menu")


def compute_kpis(source_df):
    """Compute the shared KPI numbers for any dataframe slice."""
    total = len(source_df)

    departments = source_df[dept_col].nunique() if dept_col else 0

    taste_avg = (
        round(pd.to_numeric(source_df[taste_col], errors="coerce").mean(), 2)
        if taste_col else 0
    )

    hygiene_avg = (
        round(pd.to_numeric(source_df[hygiene_col], errors="coerce").mean(), 2)
        if hygiene_col else 0
    )

    menu_yes = 0
    if menu_col:
        menu_yes = round(
            (
                source_df[menu_col]
                .astype(str)
                .str.lower()
                .eq("yes")
                .mean()
            ) * 100,
            1
        )

    return total, departments, taste_avg, hygiene_avg, menu_yes


# ----------------------------
# Page Routing
# ----------------------------

if selected == "Dashboard":

    # ----------------------------
    # Filters
    # ----------------------------

    st.subheader("Filters")

    c1, c2, c3 = st.columns(3)

    selected_department = "All"
    selected_meal = "All"
    search = ""

    with c1:
        if dept_col:
            departments_list = ["All"] + sorted(df[dept_col].dropna().unique().tolist())
            selected_department = st.selectbox("Department", departments_list)

    with c2:
        if meal_col:
            meals = ["All"] + sorted(df[meal_col].dropna().unique().tolist())
            selected_meal = st.selectbox("Meal", meals)

    with c3:
        search = st.text_input("Search Name")

    filtered_df = df.copy()

    if dept_col and selected_department != "All":
        filtered_df = filtered_df[
            filtered_df[dept_col] == selected_department
        ]

    if meal_col and selected_meal != "All":
        filtered_df = filtered_df[
            filtered_df[meal_col] == selected_meal
        ]

    if search and name_col:
        filtered_df = filtered_df[
            filtered_df[name_col]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    st.divider()

    # ----------------------------
    # KPIs
    # ----------------------------

    total, departments, taste_avg, hygiene_avg, menu_yes = compute_kpis(filtered_df)

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric("📝 Total Responses", total)
    k2.metric("🏢 Departments", departments)
    k3.metric("⭐ Avg Taste", taste_avg)
    k4.metric("🧹 Avg Hygiene", hygiene_avg)
    k5.metric("🍽️ Menu Match", f"{menu_yes}%")

    st.divider()

    # ----------------------------
    # Charts
    # ----------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏢 Department Wise Responses")
        fig = department_chart(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🍽 Meal Distribution")
        fig = meal_chart(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("⭐ Taste Rating")
        fig = taste_chart(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("🧹 Hygiene Rating")
        fig = hygiene_chart(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Daily Responses")
    fig = trend_chart(filtered_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # Table
    # ----------------------------

    st.subheader("📋 Responses")

    table_search = st.text_input(
        "🔍 Search Name, Department, Email, Mobile..."
    )

    display_df = filtered_df.copy()

    if table_search:
        mask = display_df.astype(str).apply(
            lambda col: col.str.contains(table_search, case=False, na=False)
        ).any(axis=1)

        display_df = display_df[mask]

    csv = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download CSV",
        csv,
        "walmi_feedback.csv",
        "text/csv"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

elif selected == "Responses":

    st.title("📋 All Responses")

    search = st.text_input("🔍 Search Responses")

    display = df.copy()

    if search:
        mask = display.astype(str).apply(
            lambda col: col.str.contains(search, case=False, na=False)
        ).any(axis=1)

        display = display[mask]

    csv = display.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Responses",
        csv,
        "responses.csv",
        "text/csv"
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

elif selected == "Analytics":

    st.title("📈 Advanced Analytics")

    total, departments, taste_avg, hygiene_avg, menu_yes = compute_kpis(df)

    a1, a2, a3, a4 = st.columns(4)

    a1.metric("Total Responses", total)
    a2.metric("Departments", departments)
    a3.metric("Avg Taste", taste_avg)
    a4.metric("Avg Hygiene", hygiene_avg)

    fig = department_chart(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    fig = trend_chart(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

elif selected == "Export":

    st.title("📤 Export")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download CSV",
        csv,
        "walmi_feedback.csv",
        "text/csv"
    )

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        "📊 Download Excel",
        excel_buffer.getvalue(),
        "walmi_feedback.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )