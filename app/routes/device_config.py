# app/routes/device_config.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from knx_control import add_room_instance, get_all_rooms

router = APIRouter()


class DeviceConfig(BaseModel):
    name: str
    type: str

    # Accept arbitrary device-specific fields
    class Config:
        extra = "allow"  # or extra = "allow"


class RoomDefinition(BaseModel):
    room_id: str
    ip: str
    devices: list[DeviceConfig]


@router.post("/configure-room", tags=["Development"])
async def configure_room(room: RoomDefinition):
    try:
        await add_room_instance(room)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": f"Room '{room.room_id}' configured successfully"}


@router.get("/configured-rooms", tags=["Development"])
def get_rooms():
    return list(get_all_rooms().keys())