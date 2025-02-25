from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
import io
import os

# GitHub Raw CSV File URL
GITHUB_CSV_URL = "https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/frncztuioygz/b/solar-data-bucket/o/Solardata_1.csv"

# Function to fetch only necessary rows from GitHub CSV
def get_nearest_from_github(lat, lon):
    try:
        response = requests.get(GITHUB_CSV_URL)
        response.raise_for_status()  # Raise error if request fails

        # 🔍 Debugging: Print raw CSV response (first 500 characters)
        print("Raw CSV Response:\n", response.text[:500])

        # ✅ Explicitly set the delimiter to ensure correct parsing
        df = pd.read_csv(io.StringIO(response.text), delimiter=",")

        # ✅ Ensure correct column names
        expected_columns = ["TEMP", "GHI", "DNI", "DIF", "Latitude", "Longitude"]
        if list(df.columns) != expected_columns:
            return {"error": f"CSV format issue: Expected columns {expected_columns}, but got {list(df.columns)}"}

        # ✅ Fill missing values with 0
        df.fillna(0, inplace=True)

        # ✅ Convert necessary columns to numeric
        for col in ["Latitude", "Longitude", "GHI", "DNI", "DIF", "TEMP"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # ✅ Ensure valid lat/lon values
        df.dropna(subset=["Latitude", "Longitude"], inplace=True)

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

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nabeel9798.github.io/Solar-data-app/",
        "https://solar-data-app-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_solar_data")
def get_solar_data(lat: float = Query(...), lon: float = Query(...)):
    return get_nearest_from_github(lat, lon)

# Run server
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))  # Set port to 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
