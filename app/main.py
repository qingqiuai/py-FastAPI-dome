from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.routers import load, transport, deliver, orders

app = FastAPI(title="Cargo API")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(load.router, prefix="/api")
app.include_router(transport.router, prefix="/api")
app.include_router(deliver.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
@app.on_event("startup")
async def on_start():
    await init_db()