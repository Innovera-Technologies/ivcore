from pydantic import BaseModel, Field
from typing import List, Optional


class KNXDeviceConfig(BaseModel):
    name: str
    type: str  # Must match SUPPORTED_DEVICES keys
    group_address: Optional[str] = None
    group_address_state: Optional[str] = None
    passive_group_addresses: Optional[List[str]] = []
    value_type: Optional[str] = None
    sync_state: Optional[bool] = None
    always_callback: Optional[bool] = None


class RoomConfig(BaseModel):
    room_id: str
    ip: str
    devices: List[KNXDeviceConfig]


class KNXRuntimeConfig(BaseModel):
    rooms: List[RoomConfig] = Field(..., description="List of rooms with KNX devices")
