# knx_control.py
import logging
import time
from app.utils.knx_device_loader import RoomKNX

# Dynamic config store
dynamic_room_config = []  # Will be filled from frontend/API
room_instances: list[RoomKNX] = []
ROOM_INSTANCES: dict[str, RoomKNX] = {}

logging.basicConfig(level=logging.INFO)
logging.getLogger("xknx.log").level = logging.DEBUG
logging.getLogger("xknx.knx").level = logging.DEBUG


def get_room_instance_by_id(room_id: str) -> RoomKNX | None:
    return ROOM_INSTANCES.get(room_id)

# ✅ Get a specific room config by ID (from stored config)
def get_room_config_by_id(room_id: str):
    return next((room for room in dynamic_room_config if room["room_id"] == room_id), None)

# ✅ Add a room instance from stored config
async def add_room_instance_by_id(room_id: str):
    config = get_room_config_by_id(room_id)
    if not config:
        raise ValueError(f"No stored config found for room {room_id}")

    await remove_room_instance(room_id)

    instance = RoomKNX(
        room_id=config["room_id"],
        ip=config["ip"],
        devices=config["devices"],
    )
    await instance.initialize()
    room_instances.append(instance)
    ROOM_INSTANCES[room_id] = instance

# ✅ Remove an instance by ID
async def remove_room_instance(room_id: str):
    global room_instances
    instance = next((r for r in room_instances if r.room_id == room_id), None)
    if instance:
        await instance.disconnect()  # optional: add graceful disconnect in RoomKNX
        room_instances = [r for r in room_instances if r.room_id != room_id]

# This is the main setup function triggered on FastAPI startup or config update
async def setup_knx_all():
    global room_instances, ROOM_INSTANCES
    room_instances = []
    ROOM_INSTANCES = {}

    for room in dynamic_room_config:
        instance = RoomKNX(
            room_id=room["room_id"], ip=room["ip"], devices=room["devices"]
        )
        await instance.initialize()
        room_instances.append(instance)
        ROOM_INSTANCES[room["room_id"]] = instance


# Update configuration dynamically from API
async def update_room_configuration(config: list[dict]):
    global dynamic_room_config
    dynamic_room_config = config
    await setup_knx_all()
    return {"status": "KNX rooms configured", "rooms": len(room_instances)}


# Utility to get data from a device (for now used by /temperature)
async def get_temperature_for_room(room_id: str):
    room = next((r for r in room_instances if r.room_id == room_id), None)
    if not room:
        return {"error": f"Room {room_id} is not configured"}

    for device in room.devices:
        if device.__class__.__name__ == "Sensor":
            print(f"📡 Syncing sensor '{device.name}' in Room {room_id}...")
            await device.sync(wait_for_result=True)
            temp = device.resolve_state()
            print(f"🌡️ Room {room_id} → {device.name}: {temp}")
            return {
                "room_id": room_id,
                "sensor": device.name,
                "temperature": temp if temp is not None else "no data",
            }

    return {"error": f"No sensor found in Room {room_id}"}


def get_current_configuration():
    return {
        "rooms": [
            {
                "room_id": room.room_id,
                "ip": room.ip,
                "devices": room.devices_config,
            }
            for room in room_instances
        ]
    }


def get_all_rooms():
    return {room.room_id: room for room in room_instances}


async def add_room_instance(room):
    global room_instances, dynamic_room_config

    # Remove old room config if exists
    room_instances = [r for r in room_instances if str(r.room_id) != str(room.room_id)]
    dynamic_room_config = [r for r in dynamic_room_config if str(r["room_id"]) != str(room.room_id)]


    # Add new config
    instance = RoomKNX(
        room_id=room.room_id,
        ip=room.ip,
        devices=[device.dict() for device in room.devices],
    )
    await instance.initialize()
    room_instances.append(instance)

    # Save updated config to store
    dynamic_room_config.append(room.dict())

    print("🔍 Saving full config:", room.dict())

    return {"status": f"Room {room.room_id} added."}

def get_xknx_instance(room_id: str):
    for room in room_instances:
        if str(room.room_id) == str(room_id):
            return room.xknx
    return None
