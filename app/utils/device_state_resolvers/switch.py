from xknx.devices import Switch

def resolve_switch_state(device: Switch) -> dict:
    return {
        "name": device.name,
        "type": "Switch",
        "room_id": getattr(device, "room_id", None),
        "group_address": device.switch.group_address,
        "group_address_state": device.switch.group_address_state,
        "state": device.state,
    }
