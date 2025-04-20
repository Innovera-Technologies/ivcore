from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.dependencies.ws_auth import websocket_auth
from knx_control import get_room_instance_by_id
from xknx.telegram import Telegram
from xknx.telegram.apci import GroupValueWrite
from xknx.devices import Device
from app.utils.device_state_resolvers import DEVICE_RESOLVERS
import asyncio
from app.core.ws_broadcaster import device_ws_broadcaster

router = APIRouter(tags=["KNX WebSocket"])

@router.websocket("/ws/device/{room_id}")
async def knx_device_websocket(websocket: WebSocket, room_id: str, auth=Depends(websocket_auth)):
    await websocket.accept()
    print(f"🔌 WebSocket connected for room {room_id} and Auth: {auth}")
    room = get_room_instance_by_id(room_id)
    if not room:
        await websocket.send_json({"error": f"Room {room_id} not found"})
        await websocket.close()
        return

    try:
        while True:
            msg = await websocket.receive_json()
            if "subscribe" in msg:
                for device_name in msg["subscribe"]:
                    device_ws_broadcaster.subscribe(room_id, device_name, websocket)
                    await websocket.send_json({"subscribed_device": device_name})
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for room {room_id}")
        device_ws_broadcaster.unsubscribe(websocket)


@router.websocket("/ws/group/{room_id}")
async def knx_group_websocket(websocket: WebSocket, room_id: str):
    await websocket.accept()
    room = get_room_instance_by_id(room_id)

    if not room:
        await websocket.send_json({"error": f"Room {room_id} not found"})
        await websocket.close()
        return

    subscribed_gas = set()
    subscribed_devices = set()

    async def telegram_listener(telegram: Telegram):
        # Handle raw GA subscriptions
        if isinstance(telegram.payload, GroupValueWrite):
            dest = str(telegram.destination_address)
            if dest in subscribed_gas:
                value = telegram.payload.value.value
                await websocket.send_json({"group_address": dest, "value": value})

        # Handle full device updates
        for device in room.devices:
            if device.name in subscribed_devices:
                resolver = DEVICE_RESOLVERS.get(device.__class__.__name__)
                if resolver:
                    state = resolver(device)
                    await websocket.send_json({"device": device.name, "state": state})

    room.xknx.telegram_queue.register_telegram_received_cb(telegram_listener)

    try:
        while True:
            msg = await websocket.receive_json()

            if "subscribe" in msg:
                for addr in msg["subscribe"]:
                    subscribed_gas.add(addr)
                    print(f"✅ Subscribed to GA {addr}")

            if "subscribe_devices" in msg:
                for dev in msg["subscribe_devices"]:
                    subscribed_devices.add(dev)
                    print(f"✅ Subscribed to device {dev}")

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for room {room_id}")
    finally:
        room.xknx.telegram_queue.unregister_telegram_received_cb(telegram_listener)
