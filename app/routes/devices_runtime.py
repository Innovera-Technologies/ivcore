from fastapi import APIRouter
from knx_control import get_all_rooms

router = APIRouter(tags=["KNX Runtime"])

@router.get(
    "/devices-runtime",
    summary="Get all configured KNX devices (runtime)",
    description="Returns a flat list of all configured KNX devices from the runtime config (not live device states), with room_id included."
)
def get_runtime_devices():
    print("🔍 Fetching all configured KNX devices...")
    all_devices = []

    for room_id, room in get_all_rooms().items():
        for device in room.devices_config:
            print(f"Room {room_id}: {device}")
            device_with_room = device.copy()
            device_with_room["room_id"] = room_id
            all_devices.append(device_with_room)

    return all_devices
