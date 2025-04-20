from xknx.devices import (
    Light,
    Sensor,
    BinarySensor,
    Switch,
    Fan,
    Climate,
    ClimateMode,
    Cover,
    Weather,
    NumericValue,
    RawValue,
    ExposeSensor,
    Notification,
    Scene,
)
from xknx.devices.datetime import TimeDevice, DateDevice, DateTimeDevice

SUPPORTED_DEVICES = {
    "Light": Light,
    "Sensor": Sensor,
    "BinarySensor": BinarySensor,
    "Switch": Switch,
    "Fan": Fan,
    "Climate": Climate,
    "ClimateMode": ClimateMode,
    "Cover": Cover,
    "Weather": Weather,
    "NumericValue": NumericValue,
    "RawValue": RawValue,
    "TimeDevice": TimeDevice,
    "DateDevice": DateDevice,
    "DateTimeDevice": DateTimeDevice,
    "ExposeSensor": ExposeSensor,
    "Notification": Notification,
    "Scene": Scene,
}

__ALL__ = ["SUPPORTED_DEVICES"]
