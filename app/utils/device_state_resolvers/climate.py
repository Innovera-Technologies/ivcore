# app/resolvers/climate.py
from xknx.devices import Climate

def resolve_climate_state(device: Climate) -> dict:
    return {
        "temperature": device.temperature.value if device.temperature else None,
        "target_temperature": device.target_temperature.value if device.target_temperature else None,
        "on": device.on.value if device.on else None,
        "active": device.active.value if device.active else None,
        "fan_speed": device.current_fan_speed,
        "swing": device.current_swing,
        "horizontal_swing": device.current_horizontal_swing,
        "setpoint_shift": device.setpoint_shift,
    }