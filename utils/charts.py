import plotly.express as px
import pandas as pd

PRIMARY = "#1F4B44"
SECONDARY = "#D9A404"


def find_column(df, keyword):
    for c in df.columns:
        if keyword.lower() in c.lower():
            return c
    return None


# -------------------------------
# Department Chart
# -------------------------------

def department_chart(df):

    dept = find_column(df, "department")

    if dept is None:
        return None

    chart_df = (
        df[dept]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    chart_df.columns = ["Department", "Responses"]

    fig = px.bar(
        chart_df,
        x="Responses",
        y="Department",
        orientation="h",
        color="Responses",
        color_continuous_scale="Teal",
        text="Responses"
    )

    fig.update_layout(
        height=420,
        coloraxis_showscale=False,
        template="plotly_white",
        margin=dict(l=10,r=10,t=30,b=10)
    )

    return fig


# -------------------------------
# Meal Distribution
# -------------------------------

def meal_chart(df):

    meal = find_column(df,"meal")

    if meal is None:
        return None

    chart_df = (
        df[meal]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    chart_df.columns=["Meal","Responses"]

    fig = px.pie(
        chart_df,
        names="Meal",
        values="Responses",
        hole=.55
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


# -------------------------------
# Taste Distribution
# -------------------------------

def taste_chart(df):

    col=find_column(df,"taste")

    if col is None:
        return None

    temp=df.copy()

    temp[col]=pd.to_numeric(temp[col],errors="coerce")

    temp=temp.dropna(subset=[col])

    fig=px.histogram(
        temp,
        x=col,
        nbins=5,
        color_discrete_sequence=["#D9A404"]
    )

    fig.update_layout(
        template="plotly_white",
        height=400,
        xaxis_title="Taste Rating",
        yaxis_title="Responses"
    )

    return fig


# -------------------------------
# Hygiene Distribution
# -------------------------------

def hygiene_chart(df):

    col=find_column(df,"hygiene")

    if col is None:
        return None

    temp=df.copy()

    temp[col]=pd.to_numeric(temp[col],errors="coerce")

    temp=temp.dropna(subset=[col])

    fig=px.histogram(
        temp,
        x=col,
        nbins=5,
        color_discrete_sequence=["#1F4B44"]
    )

    fig.update_layout(
        template="plotly_white",
        height=400,
        xaxis_title="Hygiene Rating",
        yaxis_title="Responses"
    )

    return fig


# -------------------------------
# Daily Trend
# -------------------------------

def trend_chart(df):

    date_col=find_column(df,"timestamp")

    if date_col is None:
        return None

    temp=df.copy()

    temp[date_col]=pd.to_datetime(
        temp[date_col],
        errors="coerce"
    )

    temp["Date"]=temp[date_col].dt.date

    trend=(
        temp.groupby("Date")
        .size()
        .reset_index(name="Responses")
    )

    fig=px.line(
        trend,
        x="Date",
        y="Responses",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig