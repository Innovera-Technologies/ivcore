# main.py (cleaned up)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from app.routes import project_parser, knx_config, device_config, devices_runtime, knx_ws, knx_control_ws
from knx_control import get_temperature_for_room
from app.routes import temperature, knx_runtime
import psutil
import asyncio

app = FastAPI()

# ✅ Include API routers
app.include_router(project_parser.router)
app.include_router(knx_config.router)
app.include_router(device_config.router)
app.include_router(temperature.router)
app.include_router(knx_runtime.router)
app.include_router(devices_runtime.router)
app.include_router(knx_ws.router)
app.include_router(knx_control_ws.router)

@app.on_event("startup")
async def startup_event():
    print("\U0001F680 IVCore backend is running. Awaiting runtime KNX configuration...")

@app.get("/")
def root():
    return {"status": "KNX backend is running. Please upload config via /knx-config."}

@app.get("/temperature/{room_id}", tags=["Development"])
async def read_temp(room_id: str):
    return await get_temperature_for_room(room_id)

@app.get("/stats")
def system_stats():
    p = psutil.Process()
    mem = round(p.memory_info().rss / 1024 / 1024, 2)
    cpu = p.cpu_percent(interval=0.5)
    threads = p.num_threads()
    return {
        "memory_mb": mem,
        "cpu_percent": cpu,
        "threads": threads,
        "pid": p.pid
    }

@app.get("/favicon.ico")
def favicon():
    return Response(content="", media_type="image/x-icon")

@app.websocket("/ws/temperature/{room_id}")
async def websocket_temperature(websocket: WebSocket, room_id: int):
    await websocket.accept()
    try:
        while True:
            data = await get_temperature_for_room(room_id - 1)
            await websocket.send_json(data)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected: Room {room_id}")