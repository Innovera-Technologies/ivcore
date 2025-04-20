from xknx.devices import Fan

def resolve_fan_state(device: Fan) -> dict:
    return {
        "name": device.name,
        "type": "Fan",
        "room_id": getattr(device, "room_id", None),
        "is_on": device.is_on,
        "current_speed": device.current_speed,
        "supports_oscillation": device.supports_oscillation,
        "current_oscillation": device.current_oscillation,
        "mode": device.mode.name if hasattr(device, "mode") else None,
        "max_step": device.max_step,
    }
