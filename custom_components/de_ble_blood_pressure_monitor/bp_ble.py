"""Async Python library for Blood Pressure Monitor."""

import asyncio
import logging
import struct
from typing import Optional, Callable, Any, Union

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.WARNING)

# UUIDs из вашего ESPHome конфига
BP_SERVICE_UUID = "00001810-0000-1000-8000-00805f9b34fb"
BP_CHAR_UUID = "00002a35-0000-1000-8000-00805f9b34fb"

class BloodPressureMonitor:
    """Blood Pressure Monitor interface for Medisana BU 575."""
    
    def __init__(self, address_or_ble_device: Union[str, BLEDevice]):
        """Initialize blood pressure monitor with address or BLEDevice."""
        if isinstance(address_or_ble_device, BLEDevice):
            self.address = address_or_ble_device.address
            self.ble_device = address_or_ble_device
        else:
            self.address = address_or_ble_device
            self.ble_device = None
            
        self.client: Optional[BleakClient] = None
        self._systolic: int = 0
        self._diastolic: int = 0
        self._map: int = 0
        self._pulse: int = 0
        self._user_id: int = 0
        self._measurement_time: str = ""
        self._callback: Optional[Callable[[str, Any], None]] = None
        
    def set_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Set callback for data updates."""
        self._callback = callback
        
    def _decode_sfloat(self, raw: int) -> float:
        """Decode IEEE 11073 16-bit SFLOAT value."""
        exponent = (raw >> 12) & 0x0F
        if exponent >= 0x08:
            exponent = -((0x0F + 1) - exponent)
        
        mantissa = raw & 0x0FFF
        if mantissa >= 0x0800:
            mantissa = -((0x0FFF + 1) - mantissa)
        
        return mantissa * (10 ** exponent)
        
    def _notification_handler(self, sender: int, data: bytearray) -> None:
        """Handle incoming notifications."""
        try:
            if len(data) < 19:
                return
                
            flags = data[0]
            timestamp_present = flags & 0x02
            pulse_rate_present = flags & 0x04
            user_id_present = flags & 0x08
            
            offset = 1
            
            # Читаем значения давления (систолическое, диастолическое, MAP)
            systolic_raw = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            diastolic_raw = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            map_raw = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            
            self._systolic = int(self._decode_sfloat(systolic_raw))
            self._diastolic = int(self._decode_sfloat(diastolic_raw))
            self._map = int(self._decode_sfloat(map_raw))
            
            if self._callback:
                self._callback("systolic", self._systolic)
                self._callback("diastolic", self._diastolic)
                self._callback("map", self._map)
            
            # Читаем временную метку если есть
            if timestamp_present and offset + 7 <= len(data):
                year = struct.unpack_from('<H', data, offset)[0]
                offset += 2
                month = data[offset]
                offset += 1
                day = data[offset]
                offset += 1
                hour = data[offset]
                offset += 1
                minute = data[offset]
                offset += 2  # пропускаем секунды
                
                self._measurement_time = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
                if self._callback:
                    self._callback("measurement_time", self._measurement_time)
            
            # Читаем пульс если есть
            if pulse_rate_present and offset + 2 <= len(data):
                pulse_raw = struct.unpack_from('<H', data, offset)[0]
                offset += 2
                self._pulse = int(self._decode_sfloat(pulse_raw))
                if self._callback:
                    self._callback("pulse", self._pulse)
            
            # Читаем ID пользователя если есть
            if user_id_present and offset < len(data):
                self._user_id = data[offset]
                if self._callback:
                    self._callback("user_id", self._user_id)
                    
        except Exception:
            pass
    
    def _disconnected_callback(self, client: BleakClient) -> None:
        """Handle disconnection."""
        self.client = None
        if self._callback:
            self._callback("disconnected", None)
    
    async def async_connect(self) -> bool:
        """Connect to blood pressure monitor and enable notifications."""
        try:
            if not self.ble_device:
                self.ble_device = await BleakScanner.find_device_by_address(
                    self.address, timeout=3.0
                )
                if not self.ble_device:
                    return False
            
            self.client = BleakClient(
                self.ble_device,
                disconnected_callback=self._disconnected_callback
            )
            
            await self.client.connect(timeout=8.0)
            await self.client.start_notify(
                BP_CHAR_UUID,
                self._notification_handler
            )
            
            if self._callback:
                self._callback("connected", None)
            
            return True
            
        except Exception:
            self.client = None
            return False
    
    async def async_disconnect(self) -> None:
        """Disconnect from blood pressure monitor."""
        if self.client and self.client.is_connected:
            try:
                await self.client.stop_notify(BP_CHAR_UUID)
                await self.client.disconnect()
            except Exception:
                pass
            finally:
                self.client = None
                if self._callback:
                    self._callback("disconnected", None)
    
    @property
    def systolic(self) -> int:
        """Current systolic pressure (mmHg)."""
        return self._systolic
    
    @property
    def diastolic(self) -> int:
        """Current diastolic pressure (mmHg)."""
        return self._diastolic
    
    @property
    def map(self) -> int:
        """Current mean arterial pressure (mmHg)."""
        return self._map
    
    @property
    def pulse(self) -> int:
        """Current heart rate (bpm)."""
        return self._pulse
    
    @property
    def user_id(self) -> int:
        """Current user ID."""
        return self._user_id
    
    @property
    def measurement_time(self) -> str:
        """Last measurement time."""
        return self._measurement_time
    
    @property
    def connected(self) -> bool:
        """Connection status."""
        return self.client is not None and self.client.is_connected
    
    @staticmethod
    async def discover_devices(timeout: float = 5.0) -> list[BLEDevice]:
        """Discover nearby blood pressure monitors."""
        devices = []
        
        def detection_callback(device: BLEDevice, advertisement_data):
            if advertisement_data and advertisement_data.service_uuids:
                if BP_SERVICE_UUID in advertisement_data.service_uuids:
                    devices.append(device)
        
        scanner = BleakScanner(detection_callback)
        await scanner.start()
        await asyncio.sleep(timeout)
        await scanner.stop()
        
        return devices