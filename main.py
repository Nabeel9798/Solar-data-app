import os
import oci
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "App is running!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Read PORT from Railway env variables
    uvicorn.run(app, host="0.0.0.0", port=port)
