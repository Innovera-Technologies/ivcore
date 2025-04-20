# /app/routes/knx_config.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os, json
from knx_control import update_room_configuration, get_current_configuration

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


# ✅ POST: Apply config to runtime (best-effort)
@router.post("/knx-config-runtime", tags=["Development"])
async def configure_knx_runtime():
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(status_code=404, detail="No saved configuration found")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    successes, failures = [], []
    for room in config_data.get("rooms", []):
        try:
            await update_room_configuration([room])
            successes.append(room["room_id"])
        except Exception as e:
            failures.append({"room_id": room["room_id"], "error": str(e)})

    return {
        "status": "🛠️ Configuration applied",
        "succeeded": successes,
        "failed": failures
    }


# ✅ GET: Show currently running runtime setup
@router.get("/knx-config-runtime", tags=["Development"])
def get_knx_config():
    return get_current_configuration()
