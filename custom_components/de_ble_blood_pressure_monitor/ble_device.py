"""Async Python library for Medisana BU 575 Blood Pressure Monitor."""

import asyncio
import logging
import struct
from typing import Optional, Callable, Any, Union
from datetime import datetime

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.WARNING)

# UUIDs
BP_SERVICE_UUID = "00001810-0000-1000-8000-00805f9b34fb"
BP_CHAR_UUID = "00002a35-0000-1000-8000-00805f9b34fb"

def decode_sfloat(raw: int) -> float:
    """Decode IEEE 11073 16-bit SFLOAT value."""
    exponent = (raw >> 12) & 0x0F
    if exponent >= 0x08:
        exponent = -((0x0F + 1) - exponent)
    
    mantissa = raw & 0x0FFF
    if mantissa >= 0x0800:
        mantissa = -((0x0FFF + 1) - mantissa)
    
    return mantissa * (10 ** exponent)

class BloodPressureMonitor:
    """Medisana BU 575 Blood Pressure Monitor interface."""
    
    def __init__(self, address_or_ble_device: Union[str, BLEDevice]):
        """Initialize monitor with address or BLEDevice."""
        if isinstance(address_or_ble_device, BLEDevice):
            self.address = address_or_ble_device.address
            self.ble_device = address_or_ble_device
        else:
            self.address = address_or_ble_device
            self.ble_device = None
            
        self.client: Optional[BleakClient] = None
        self._systolic = 0
        self._diastolic = 0
        self._map = 0  # Mean Arterial Pressure
        self._pulse = 0
        self._user_id = 0
        self._timestamp: Optional[datetime] = None
        self._measurement_complete = False
        self._callback: Optional[Callable[[str, Any], None]] = None
        
    def set_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Set callback for data updates."""
        self._callback = callback
        
    def _decode_measurement(self, data: bytearray) -> bool:
        """Decode blood pressure measurement data."""
        if len(data) < 19:
            return False
        
        # Флаги
        flags = data[0]
        timestamp_present = flags & 0x02
        pulse_rate_present = flags & 0x04
        user_id_present = flags & 0x08
        
        offset = 1
        
        # Систолическое давление
        systolic_raw = struct.unpack_from('<H', data, offset)[0]
        offset += 2
        self._systolic = int(decode_sfloat(systolic_raw))
        
        # Диастолическое давление
        diastolic_raw = struct.unpack_from('<H', data, offset)[0]
        offset += 2
        self._diastolic = int(decode_sfloat(diastolic_raw))
        
        # Среднее давление
        map_raw = struct.unpack_from('<H', data, offset)[0]
        offset += 2
        self._map = int(decode_sfloat(map_raw))
        
        # Временная метка
        if timestamp_present:
            year = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            month = data[offset]; offset += 1
            day = data[offset]; offset += 1
            hour = data[offset]; offset += 1
            minute = data[offset]; offset += 1
            offset += 1  # секунды (не используем)
            
            try:
                self._timestamp = datetime(year, month, day, hour, minute)
            except ValueError:
                self._timestamp = None
        
        # Пульс
        if pulse_rate_present:
            pulse_raw = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            self._pulse = int(decode_sfloat(pulse_raw))
        
        # ID пользователя
        if user_id_present and offset < len(data):
            self._user_id = data[offset]
        
        self._measurement_complete = True
        return True
    
    def _notification_handler(self, sender: int, data: bytearray) -> None:
        """Handle incoming notifications."""
        try:
            if self._decode_measurement(data):
                # Отправляем все обновления
                if self._callback:
                    self._callback("systolic", self._systolic)
                    self._callback("diastolic", self._diastolic)
                    self._callback("map", self._map)
                    self._callback("pulse", self._pulse)
                    self._callback("user_id", self._user_id)
                    if self._timestamp:
                        self._callback("timestamp", self._timestamp.isoformat())
                    self._callback("measurement_complete", True)
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
        """Disconnect from monitor."""
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
        """Systolic pressure (mmHg)."""
        return self._systolic
    
    @property
    def diastolic(self) -> int:
        """Diastolic pressure (mmHg)."""
        return self._diastolic
    
    @property
    def map(self) -> int:
        """Mean Arterial Pressure (mmHg)."""
        return self._map
    
    @property
    def pulse(self) -> int:
        """Heart rate (bpm)."""
        return self._pulse
    
    @property
    def user_id(self) -> int:
        """User ID (1 or 2)."""
        return self._user_id
    
    @property
    def timestamp(self) -> Optional[datetime]:
        """Measurement timestamp."""
        return self._timestamp
    
    @property
    def measurement_complete(self) -> bool:
        """Whether a complete measurement was received."""
        return self._measurement_complete
    
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
