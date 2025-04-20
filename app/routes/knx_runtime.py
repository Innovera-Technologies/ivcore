from fastapi import APIRouter, HTTPException, Query
from xknx.tools import group_value_read, group_value_write, read_group_value
from knx_control import (
    get_xknx_instance,
    get_all_rooms,
    add_room_instance,
    remove_room_instance,
    get_current_configuration,
    add_room_instance_by_id,
)

router = APIRouter(tags=["KNX Runtime"])


@router.get(
    "/ga-read",
    summary="Read from a group address",
    description="Read a value from a KNX group address.",
)
async def read_ga(
    room_id: str = Query(..., description="Room ID to use for the KNX connection"),
    address: str = Query(..., description="Group address like 1/2/3"),
    dpt: str = Query(
        None, description="Optional DPT type like 'temperature', 'percent', etc."
    ),
):
    try:
        xknx = get_xknx_instance(room_id)
        if xknx is None:
            raise HTTPException(
                status_code=400, detail=f"KNX room {room_id} is not configured"
            )
        value = await read_group_value(xknx, address, value_type=dpt)
        return {"room_id": room_id, "address": address, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Read error: {e}")


@router.post(
    "/ga-write",
    summary="Write to a group address",
    description="Send a value to a KNX group address.",
)
async def write_ga(
    room_id: str = Query(..., description="Room ID to use for the KNX connection"),
    address: str = Query(..., description="Group address like 1/2/3"),
    value: str = Query(..., description="Value to send"),
    dpt: str = Query(
        None, description="Optional DPT type like 'percent', 'temperature', etc."
    ),
):
    try:
        xknx = get_xknx_instance(room_id)
        if xknx is None:
            raise HTTPException(
                status_code=400, detail=f"KNX room {room_id} is not configured"
            )
        parsed_value = eval(value)  # Replace later with safer parsing
        group_value_write(xknx, address, parsed_value, value_type=dpt)
        return {
            "status": "✅ sent",
            "room_id": room_id,
            "address": address,
            "value": parsed_value,
            "dpt": dpt,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write error: {e}")


@router.post("/connect-room/{room_id}", summary="Manually connect a KNX room")
async def connect_room(room_id: str):
    all_rooms = get_all_rooms()
    config = next((r for r in all_rooms.values() if r.room_id == room_id), None)
    if not config:
        raise HTTPException(
            status_code=404, detail=f"Room {room_id} not found in stored configuration"
        )

    try:
        await add_room_instance(config)
        return {"status": f"✅ Room {room_id} connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect room: {e}")


@router.post("/disconnect-room/{room_id}", summary="Manually disconnect a KNX room")
async def disconnect_room(room_id: str):
    try:
        await remove_room_instance(room_id)
        return {"status": f"🚫 Room {room_id} disconnected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect room: {e}")


# ✅ Connect all rooms
@router.post("/connect-all", summary="Connect all KNX rooms")
async def connect_all_rooms():
    configs = get_current_configuration().get("rooms", [])
    if not configs:
        raise HTTPException(status_code=404, detail="No stored KNX config found.")

    results = {}
    for room in configs:
        room_id = room["room_id"]
        try:
            await add_room_instance_by_id(room_id)
            results[room_id] = "✅ connected"
        except Exception as e:
            results[room_id] = f"❌ failed: {e}"

    return results


# ✅ Disconnect all rooms
@router.post("/disconnect-all", summary="Disconnect all KNX rooms")
async def disconnect_all_rooms():
    active_rooms = list(get_all_rooms().keys())

    results = {}
    for room_id in active_rooms:
        try:
            await remove_room_instance(room_id)
            results[room_id] = "✅ disconnected"
        except Exception as e:
            results[room_id] = f"❌ failed: {e}"

    return results
