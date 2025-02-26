from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import gspread
import json
import os
import uvicorn
from google.oauth2.service_account import Credentials

# ✅ Load Google Credentials from Railway Environment Variables
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS", "{}"))

# ✅ Authenticate Google Sheets API
creds = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)

# ✅ Define Google Sheet ID & Name
GOOGLE_SHEET_ID = "1JfFfUDvW-jmid3pEcocDMc57wXCQGUoOOWbWMszzLnM"  # Replace with your actual Google Sheet ID
SHEET_NAME = "solardata_2shp"  # Change if your sheet name is different

# ✅ Function to fetch nearest solar data from Google Sheets
def get_nearest_from_google_sheets(lat, lon):
    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_records()

        if not data:
            return {"error": "No data found in the Google Sheet"}

        df = pd.DataFrame(data)

        # ✅ Ensure correct column names
        expected_columns = ["TEMP", "GHI", "DNI", "DIF", "Latitude", "Longitude"]
        if not all(col in df.columns for col in expected_columns):
            return {"error": f"Google Sheet format issue: Expected columns {expected_columns}, but got {list(df.columns)}"}

        # ✅ Convert necessary columns to numeric
        for col in ["Latitude", "Longitude", "GHI", "DNI", "DIF", "TEMP"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # 📍 Find the nearest location
        df["distance"] = ((df["Latitude"] - lat) ** 2 + (df["Longitude"] - lon) ** 2)
        nearest_row = df.loc[df["distance"].idxmin()]

        return {
            "TEMP": nearest_row["TEMP"],
            "GHI": nearest_row["GHI"],
            "DNI": nearest_row["DNI"],
            "DIF": nearest_row["DIF"]
        }
    except Exception as e:
        return {"error": str(e)}

# ✅ Initialize FastAPI App
app = FastAPI()

# ✅ Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API Route to Fetch Solar Data
@app.get("/get_solar_data")
def get_solar_data(lat: float = Query(...), lon: float = Query(...)):
    return get_nearest_from_google_sheets(lat, lon)

# ✅ Run Server in Local (Not needed in Railway)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Solar Data API is running!"}

import os
print("GOOGLE_CREDENTIALS:", os.getenv("GOOGLE_CREDENTIALS"))
