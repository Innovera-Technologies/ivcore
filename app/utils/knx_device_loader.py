# app/utils/knx_device_loader.py

from xknx import XKNX
from xknx.io import ConnectionConfig, ConnectionType
from .knx_supported_devices import *
from .knx_device_fields import *
from xknx.telegram import Telegram
from xknx.telegram.apci import GroupValueWrite, GroupValueResponse
from xknx.telegram import TelegramDecodedData
from xknx.core.group_address_dpt import GroupAddressDPT
from app.utils.device_state_resolvers import DEVICE_RESOLVERS
from app.core.ws_broadcaster import device_ws_broadcaster
import asyncio

ga_dpt_decoder = GroupAddressDPT()

def log_knx_telegrams(telegram: Telegram) -> None:
    raw_payload = telegram.payload
    src = telegram.source_address
    dst = telegram.destination_address

    decoded_value = None
    try:
        ga_dpt_decoder.set_decoded_data(telegram)
        if isinstance(telegram.decoded_data, TelegramDecodedData):
            decoded_value = telegram.decoded_data.value
    except Exception as e:
        decoded_value = f"Decode failed: {e}"

    print(f"📨 Telegram | {src} → {dst} | Raw: {raw_payload} | Decoded: {decoded_value}")

class RoomKNX:
    def __init__(self, room_id, ip, devices):
        self.room_id = room_id
        self.ip = ip
        self.devices_config = devices
        self.xknx = None
        self.devices = []

    async def initialize(self):
        config = ConnectionConfig(
            connection_type=ConnectionType.TUNNELING,
            gateway_ip=self.ip,
            gateway_port=3671,
        )
        self.xknx = XKNX(connection_config=config)
        self.xknx.telegram_queue.register_telegram_received_cb(log_knx_telegrams)
        await self.xknx.start()
        await self.load_devices()

    async def disconnect(self):
        if self.xknx is not None:
            await self.xknx.stop()
            self.xknx = None
            self.devices = []

    async def connect(self):
        if self.xknx is not None:
            await self.xknx.start()
            await self.load_devices()

    def _device_callback(self, device):
        device_type = device.__class__.__name__
        resolver = DEVICE_RESOLVERS.get(device_type)
        if resolver:
            state = resolver(device)
        else:
            state = {"warning": f"No resolver for {device_type}"}

        print(f"🔔 [{self.room_id}] {device.name} updated → {state}")
        
        # Send over websocket
        asyncio.create_task(
            device_ws_broadcaster.broadcast(self.room_id, device.name, state)
        )

    async def load_devices(self):
        self.devices = []
        for dev_conf in self.devices_config:
            device_type = dev_conf.get("type")
            if not device_type or device_type not in SUPPORTED_DEVICES:
                print(f"⚠️ Invalid or missing device type: {device_type}")
                continue

            device_class = SUPPORTED_DEVICES.get(device_type)
            allowed_fields = DEVICE_ALLOWED_FIELDS.get(device_type, set())

            dev_conf_clean = dev_conf.copy()

            if device_type in ["Sensor", "NumericValue"]:
                dev_conf_clean.setdefault("sync_state", True)

            filtered_conf = {
                k: v for k, v in dev_conf_clean.items() if k in allowed_fields
            }
            print(f"🧩 Final device conf for {device_type}: {filtered_conf}")

            print(f"➡️ Adding {device_type} to {self.room_id}: {filtered_conf}")
            device = device_class(
                self.xknx,
                device_updated_cb=self._device_callback,
                **filtered_conf
            )
            self.xknx.devices.async_add(device)
            self.devices.append(device)

            if len(filtered_conf) == 0:
                print(f"⚠️ No valid config fields found for {device_type} in {self.room_id}")

        print(f"✅ Room {self.room_id} initialized with {len(self.devices)} devices.")

    def get_device_by_name(self, name: str):
        for d in self.devices:
            if d.name == name:
                return d
        return None