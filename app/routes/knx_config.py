# /app/routes/knx_config.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import asyncio
from typing import List, Dict, Optional
import os, json
from knx_control import update_room_configuration, get_current_configuration, get_all_rooms, get_temperature_for_room

router = APIRouter()

UPLOAD_DIR = "./app/uploads"
CONFIG_PATH = os.path.join(UPLOAD_DIR, "knx_runtime_config.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Define a Pydantic model for a single device
class KNXDeviceConfig(BaseModel):
    name: str
    type: str
    group_address: str | None = None
    group_address_state: str | None = None
    passive_group_addresses: list[str] = []
    value_type: str | None = None

    class Config:
        extra = "allow"


# Define a room with its KNX IP interface and devices
class RoomConfig(BaseModel):
    room_id: str
    ip: str
    devices: List[KNXDeviceConfig]


# Wrapper for complete runtime configuration
class KNXRuntimeConfig(BaseModel):
    rooms: List[RoomConfig] = Field(..., description="List of rooms with KNX devices")


# ✅ POST: Save config to disk (offline-safe)
@router.post("/knx-config", tags=["KNX Config"])
async def save_knx_config(config: KNXRuntimeConfig):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config.dict(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {e}")
    return {"status": "✅ Configuration saved to disk"}


# ✅ GET: Load saved config
@router.get("/knx-config", tags=["KNX Config"])
def load_knx_config():
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(status_code=404, detail="No saved configuration found")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/knx-runtime-temperatures", tags=["Runtime Commands"])
async def read_all_temperatures():
    # Grab the dict of { room_id: RoomKNX instance }
    rooms = get_all_rooms()  # from knx_control.py :contentReference[oaicite:0]{index=0}

    # Kick off a temperature-read task for each room
    tasks = {
        room_id: asyncio.create_task(get_temperature_for_room(room_id))
        for room_id in rooms
    }

    # Await them all, capturing any per-room exceptions
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    # Map back into your response shape
    response = {}
    for room_id, result in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            response[room_id] = {"error": str(result)}
        else:
            # get_temperature_for_room returns {"room_id", "sensor", "temperature"}
            response[room_id] = {
                "device": result["sensor"],
                "temperature": result["temperature"],
            }

    return response

# ✅ POST: Apply config to runtime (best-effort)
# app/routes/knx_config.py

@router.post("/knx-config-runtime", tags=["Development"])
async def configure_knx_runtime():
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(status_code=404, detail="No saved configuration found")

    # 1) Load the full JSON array of rooms
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    # 2) Apply in one shot and get back a summary
    try:
        result = await update_room_configuration(config_data["rooms"])
    except Exception as e:
        # Unexpected errors (e.g. file parse, code bug)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    # 3) If any rooms failed, return a 207 Multi-Status
    if result.get("status") == "partial":
        # e.g. {"status":"partial","configured":10,"failed_rooms":["4121","4125"]}
        raise HTTPException(status_code=207, detail=result)

    # 4) Otherwise everything is up
    return {
        "status": "✅ Configuration applied",
        "details": result,   # {"status":"complete","configured":12,"failed_rooms":[]}
    }



# ✅ GET: Show currently running runtime setup
@router.get("/knx-config-runtime", tags=["Development"])
def get_knx_config():
    return get_current_configuration()
