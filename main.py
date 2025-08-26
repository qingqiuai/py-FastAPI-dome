# C:\py-FastAPI-dome\main.py
import uvicorn
# from app.main import app   # 注意这里导入的是 app/main.py 内的 app

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)