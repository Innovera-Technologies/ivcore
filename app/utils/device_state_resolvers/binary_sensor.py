# app/resolvers/binary_sensor.py

from xknx.devices import BinarySensor

def resolve_binary_sensor_state(device: BinarySensor) -> dict:
    return {
        "name": device.name,
        "type": "binary_sensor",
        "state": device.state,
        "is_on": device.is_on(),
        "is_off": device.is_off(),
        "counter": device.counter,
        "group_address": device.remote_value.group_address,
        "room_id": getattr(device, "room_id", None)  # optional if dynamically attached
    }