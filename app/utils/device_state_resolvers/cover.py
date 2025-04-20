from xknx.devices import Cover

def resolve_cover_state(device: Cover) -> dict:
    return {
        "name": device.name,
        "type": "Cover",
        "room_id": getattr(device, "room_id", None),
        "position": device.current_position(),
        "angle": device.current_angle(),
        "locked": device.is_locked(),
        "is_open": device.is_open(),
        "is_closed": device.is_closed(),
        "is_opening": device.is_opening(),
        "is_closing": device.is_closing(),
        "is_traveling": device.is_traveling(),
        "position_reached": device.position_reached(),
        "supports_stop": device.supports_stop,
        "supports_locked": device.supports_locked,
        "supports_position": device.supports_position,
        "supports_angle": device.supports_angle,
    }
