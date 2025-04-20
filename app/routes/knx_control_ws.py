from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from knx_control import get_room_instance_by_id

router = APIRouter(tags=["KNX WebSocket Control"])

@router.websocket("/ws/control/{room_id}")
async def knx_device_control_ws(websocket: WebSocket, room_id: str):
    await websocket.accept()
    room = get_room_instance_by_id(room_id)

    if not room:
        await websocket.send_json({"error": f"Room {room_id} not found"})
        await websocket.close()
        return

    try:
        while True:
            msg = await websocket.receive_json()
            device_name = msg.get("device")
            action = msg.get("action")
            value = msg.get("value")

            if not device_name or not action:
                await websocket.send_json({"error": "Missing 'device' or 'action'"})
                continue

            device = next((d for d in room.devices if d.name == device_name), None)
            if not device:
                await websocket.send_json({"error": f"Device '{device_name}' not found"})
                continue

            if not hasattr(device, action):
                await websocket.send_json({"error": f"Device '{device_name}' has no action '{action}'"})
                continue

            try:
                method = getattr(device, action)
                if callable(method):
                    if value is not None:
                        await method(value)
                    else:
                        await method()
                    await websocket.send_json({
                        "status": "ok",
                        "device": device_name,
                        "action": action,
                        "value": value
                    })
                else:
                    await websocket.send_json({"error": f"Attribute '{action}' is not callable"})
            except Exception as e:
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        print(f"❌ Control socket disconnected for room {room_id}")
