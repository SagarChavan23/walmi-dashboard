import os
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ----------------------------
# Google Sheet URL
# ----------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1VBrelqdBpRbkeE5AijQO5YkIN33McciChjKYMtJtDaI/edit?usp=sharing"

# ----------------------------
# Google API Scopes
# ----------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ----------------------------
# Create Google Client
# ----------------------------
@st.cache_resource
def get_client():

    # ---------- Local Development ----------
    if os.path.exists("credentials.json"):
        return gspread.service_account(
            filename="credentials.json"
        )

    # ---------- Streamlit Cloud ----------
    if "gcp_service_account" not in st.secrets:
        raise Exception(
            """
            Google credentials not found.

            Add your Service Account JSON inside
            Streamlit Cloud -> App Settings -> Secrets
            under [gcp_service_account]
            """
        )

    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=SCOPES,
    )

    return gspread.authorize(credentials)


# ----------------------------
# Load Google Sheet
# ----------------------------
@st.cache_data(ttl=30)
def load_data():

    client = get_client()

    sheet = client.open_by_url(SHEET_URL)

    worksheet = sheet.sheet1

    records = worksheet.get_all_records()

    df = pd.DataFrame(records)

    return df