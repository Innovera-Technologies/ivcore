# app/core/ws_broadcaster.py
from fastapi import WebSocket
from xknx.telegram.address import GroupAddress
from collections import defaultdict


def serialize_state(state: dict) -> dict:
    """Convert all GroupAddress or other custom types to strings or primitives."""

    def serialize_value(val):
        if isinstance(val, GroupAddress):
            return str(val)
        if isinstance(val, dict):
            return serialize_state(val)
        if isinstance(val, list):
            return [serialize_value(v) for v in val]
        return val

    return {k: serialize_value(v) for k, v in state.items()}


from collections import defaultdict


class DeviceWebSocketBroadcaster:
    def __init__(self):
        self.subscriptions = defaultdict(set)

    def subscribe(self, room_id: str, device_name: str, ws: WebSocket):
        self.subscriptions[(room_id, device_name)].add(ws)

    def unsubscribe(self, ws: WebSocket):
        for key in list(self.subscriptions):
            self.subscriptions[key].discard(ws)
            if not self.subscriptions[key]:
                del self.subscriptions[key]

    async def broadcast(self, room_id: str, device_name: str, state: dict):
        key = (room_id, device_name)
        dead = set()

        for ws in self.subscriptions.get(key, []):
            try:
                await ws.send_json(
                    {
                        "device": device_name,
                        "room_id": room_id,
                        "state": serialize_state(state),
                    }
                )
            except Exception as e:
                print(f"⚠️ Error sending to WebSocket: {e}")
                dead.add(ws)

        # Remove dead sockets
        for ws in dead:
            self.subscriptions[key].discard(ws)
        if not self.subscriptions[key]:
            del self.subscriptions[key]


device_ws_broadcaster = DeviceWebSocketBroadcaster()
