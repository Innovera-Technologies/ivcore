from xknx.devices import Notification

def resolve_notification_state(device: Notification) -> dict:
    return {
        "name": device.name,
        "type": "Notification",
        "room_id": getattr(device, "room_id", None),
        "message": device.message,
    }
