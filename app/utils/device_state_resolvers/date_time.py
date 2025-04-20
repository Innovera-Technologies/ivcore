from xknx.devices.datetime import DateTimeDevice, DateDevice, TimeDevice
from typing import Union

def resolve_datetime_state(device: Union[DateTimeDevice, DateDevice, TimeDevice]) -> dict:
    return {
        "name": device.name,
        "type": device.__class__.__name__,
        "room_id": getattr(device, "room_id", None),
        "value": str(device.value) if device.value else None,
        "localtime": device.localtime,
        "group_address": device.remote_value.group_address,
        "group_address_state": device.remote_value.group_address_state,
        "respond_to_read": device.respond_to_read,
    }
