from xknx.devices import RawValue

def resolve_raw_value_state(device: RawValue) -> dict:
    return {
        "name": device.name,
        "type": "RawValue",
        "room_id": getattr(device, "room_id", None),
        "value": device.resolve_state(),
        "group_address": device.remote_value.group_address,
        "payload_length": device.remote_value.payload_length,
    }
