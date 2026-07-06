import gspread
import pandas as pd

gc = gspread.service_account(filename="credentials.json")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1VBrelqdBpRbkeE5AijQO5YkIN33McciChjKYMtJtDaI/edit?usp=sharing"

def load_data():
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    return pd.DataFrame(data)