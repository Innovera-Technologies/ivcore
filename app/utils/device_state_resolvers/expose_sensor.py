from xknx.devices import ExposeSensor

def resolve_expose_sensor_state(device: ExposeSensor) -> dict:
    return {
        "name": device.name,
        "type": "ExposeSensor",
        "room_id": getattr(device, "room_id", None),
        "value": device.sensor_value.value,
        "unit_of_measurement": device.unit_of_measurement(),
        "group_address": device.sensor_value.group_address,
        "respond_to_read": device.respond_to_read,
        "cooldown": device.cooldown,
    }
