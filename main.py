from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
import io

# Google Drive File ID (Extracted from your link)
FILE_ID = "1XMirzg03viOr5GSK2WbsQ0-lIe_VI5jB"

# Function to fetch only necessary rows from Google Drive
def get_nearest_from_drive(lat, lon):
    URL = f"https://drive.google.com/uc?id={FILE_ID}"  # Direct access link
    response = requests.get(URL)
    response.raise_for_status()  # Raise error if request fails

    # Read CSV directly from the response
    df = pd.read_csv(io.StringIO(response.text))
    df.fillna(0, inplace=True)  # Handle missing values

    # Find nearest location
    df["distance"] = ((df["Latitude"] - lat) ** 2 + (df["Longitude"] - lon) ** 2)
    nearest_row = df.loc[df["distance"].idxmin()]

    return {
        "GHI": nearest_row["GHI"],
        "DNI": nearest_row["DNI"],
        "DIF": nearest_row["DIF"],
        "TEMP": nearest_row["TEMP"]
    }

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_solar_data")
def get_solar_data(lat: float = Query(...), lon: float = Query(...)):
    return get_nearest_from_drive(lat, lon)

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
