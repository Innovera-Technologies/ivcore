from xknx.devices import Sensor

def resolve_sensor_state(device: Sensor) -> dict:
    return {
        "name": device.name,
        "type": "Sensor",
        "room_id": getattr(device, "room_id", None),
        "group_address_state": device.sensor_value.group_address_state,
        "value": device.sensor_value.value,
        "unit": device.unit_of_measurement(),
        "ha_class": device.ha_device_class(),
    }
