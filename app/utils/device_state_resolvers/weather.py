from xknx.devices import Weather

def resolve_weather_state(device: Weather) -> dict:
    return {
        "name": device.name,
        "type": "Weather",
        "room_id": getattr(device, "room_id", None),
        "temperature": device.temperature,
        "humidity": device.humidity,
        "air_pressure": device.air_pressure,
        "wind_speed": device.wind_speed,
        "wind_bearing": device.wind_bearing,
        "brightness_south": device.brightness_south,
        "brightness_north": device.brightness_north,
        "brightness_east": device.brightness_east,
        "brightness_west": device.brightness_west,
        "max_brightness": device.max_brightness,
        "rain_alarm": device.rain_alarm,
        "frost_alarm": device.frost_alarm,
        "wind_alarm": device.wind_alarm,
        "day_night": device.day_night,
        "condition": device.ha_current_state().value,
    }
