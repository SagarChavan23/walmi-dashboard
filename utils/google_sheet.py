import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SHEET_URL = "https://docs.google.com/spreadsheets/d/1VBrelqdBpRbkeE5AijQO5YkIN33McciChjKYMtJtDaI/edit?usp=sharing"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


@st.cache_resource
def get_client():
    try:
        # Local development
        return gspread.service_account(filename="credentials.json")
    except FileNotFoundError:
        # Streamlit Cloud
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        return gspread.authorize(creds)


@st.cache_data(ttl=30)
def load_data():
    gc = get_client()
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    return pd.DataFrame(data)