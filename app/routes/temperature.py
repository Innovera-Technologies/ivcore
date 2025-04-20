from fastapi import APIRouter
from knx_control import get_all_rooms

router = APIRouter()

@router.get("/temperature/all", tags=["Development"])
async def get_all_temperatures():
    from knx_control import get_all_rooms

    all_temps = {}

    for room_id, room in get_all_rooms().items():
        for device in room.devices:
            if device.__class__.__name__ == "Sensor":
                print(f"📡 Syncing sensor '{device.name}' in Room {room_id}...")
                await device.sync(wait_for_result=True)
                temp = device.resolve_state()
                print(f"🌡️ Room {room_id} → {device.name}: {temp}")

                all_temps[room_id] = {
                    "device": device.name,
                    "temperature": temp if temp is not None else "no data"
                }
                break

    return all_temps
