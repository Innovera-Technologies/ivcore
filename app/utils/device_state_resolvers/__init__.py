from .climate import resolve_climate_state
from .binary_sensor import resolve_binary_sensor_state
from .climate_mode import resolve_climate_mode_state
from .cover import resolve_cover_state
from .date_time import resolve_datetime_state
from .expose_sensor import resolve_expose_sensor_state
from .fan import resolve_fan_state
from .light import resolve_light_state
from .notification import resolve_notification_state
from .numeric_value import resolve_numeric_value_state
from .scene import resolve_scene_state
from .sensor import resolve_sensor_state
from .switch import resolve_switch_state
from .weather import resolve_weather_state

DEVICE_RESOLVERS = {
    "Climate": resolve_climate_state,
    "BinarySensor": resolve_binary_sensor_state,
    "ClimateMode": resolve_climate_mode_state,
    "Cover": resolve_cover_state,
    "DateTime": resolve_datetime_state,
    "ExposeSensor": resolve_expose_sensor_state,
    "Fan": resolve_fan_state,
    "Light": resolve_light_state,
    "Notification": resolve_notification_state,
    "NumericValue": resolve_numeric_value_state,
    "Scene": resolve_scene_state,
    "Sensor": resolve_sensor_state,
    "Switch": resolve_switch_state,
    "Weather": resolve_weather_state,
}