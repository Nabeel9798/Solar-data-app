import oci
from fastapi import FastAPI

app = FastAPI()

@app.get("/test_oci_config")
def test_oci_config():
    try:
        # Try loading the Oracle Cloud config file
        config = oci.config.from_file("/app/.oci/config")
        return {"message": "✅ Oracle SDK Config Loaded Successfully!"}
    except Exception as e:
        return {"error": str(e)}

