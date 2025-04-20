from xknx.devices import NumericValue

def resolve_numeric_value_state(device: NumericValue) -> dict:
    return {
        "name": device.name,
        "type": "NumericValue",
        "room_id": getattr(device, "room_id", None),
        "value": device.resolve_state(),
        "unit": device.unit_of_measurement(),
        "device_class": device.ha_device_class(),
        "group_address": device.sensor_value.group_address,
    }
