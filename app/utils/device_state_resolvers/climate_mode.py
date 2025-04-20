# app/utils/device_state_resolvers/climate_mode.py

from xknx.devices.climate_mode import ClimateMode
from xknx.dpt.dpt_20 import HVACOperationMode, HVACControllerMode

def resolve_climate_mode_state(device: ClimateMode) -> dict:
    return {
        "name": device.name,
        "type": "climate_mode",
        "operation_mode": (
            device.operation_mode.name.lower()
            if isinstance(device.operation_mode, HVACOperationMode)
            else str(device.operation_mode)
        ),
        "controller_mode": (
            device.controller_mode.name.lower()
            if isinstance(device.controller_mode, HVACControllerMode)
            else str(device.controller_mode)
        ),
        "supports_operation_mode": device.supports_operation_mode,
        "supports_controller_mode": device.supports_controller_mode,
        "supported_operation_modes": [
            mode.name.lower() for mode in device.operation_modes
        ],
        "supported_controller_modes": [
            mode.name.lower() for mode in device.controller_modes
        ],
        "room_id": getattr(device, "room_id", None),
    }