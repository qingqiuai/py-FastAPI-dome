# C:\py-FastAPI-dome\main.py
import os
import uvicorn

if __name__ == "__main__":
    reload = os.getenv("FASTAPI_RELOAD", "0") == "1"
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=reload)