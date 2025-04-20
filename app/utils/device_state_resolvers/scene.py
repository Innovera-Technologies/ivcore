from xknx.devices import Scene

def resolve_scene_state(device: Scene) -> dict:
    return {
        "name": device.name,
        "type": "Scene",
        "room_id": getattr(device, "room_id", None),
        "group_address": device.scene_value.group_address,
        "scene_number": device.scene_number,
    }
