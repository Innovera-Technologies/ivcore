from xknx.devices import Light

def resolve_light_state(device: Light) -> dict:
    current_color, white = device.current_color

    return {
        "name": device.name,
        "type": "Light",
        "room_id": getattr(device, "room_id", None),
        "is_on": device.state,
        "brightness": device.current_brightness,
        "color": current_color,
        "white": white,
        "hs_color": device.current_hs_color,
        "xyy_color": (
            (device.current_xyy_color.x, device.current_xyy_color.y, device.current_xyy_color.y_lum)
            if device.current_xyy_color
            else None
        ),
        "tunable_white": device.current_tunable_white,
        "color_temperature": device.current_color_temperature,
        "supports": {
            "brightness": device.supports_brightness,
            "color": device.supports_color,
            "rgbw": device.supports_rgbw,
            "hs_color": device.supports_hs_color,
            "xyy_color": device.supports_xyy_color,
            "tunable_white": device.supports_tunable_white,
            "color_temperature": device.supports_color_temperature,
        },
    }
