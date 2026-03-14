"""DE BLE Blood Pressure Monitor integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    SCAN_INTERVAL,
)
from .ble_device import BloodPressureMonitor

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.WARNING)

PLATFORMS = ["sensor", "text_sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DE BLE Blood Pressure Monitor from a config entry."""
    address = entry.data[CONF_ADDRESS]
    
    coordinator = BPCoordinator(hass, address, entry.entry_id)
    await coordinator.async_setup()
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    async def _async_shutdown(event):
        await coordinator.async_shutdown()
    
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_shutdown)
    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    
    return unload_ok

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the DE BLE Blood Pressure Monitor integration."""
    hass.data.setdefault(DOMAIN, {})
    return True

class BPCoordinator:
    """Coordinator for Blood Pressure Monitor BLE."""
    
    def __init__(self, hass: HomeAssistant, address: str, entry_id: str) -> None:
        """Initialize coordinator."""
        self.hass = hass
        self.address = address
        self.entry_id = entry_id
        self.device: BloodPressureMonitor | None = None
        self._connected = False
        self._systolic = 0
        self._diastolic = 0
        self._map = 0
        self._pulse = 0
        self._user_id = 0
        self._timestamp = None
        self._measurement_complete = False
        self._cancel_scan: callable | None = None
        self._connecting = False
        self._shutdown = False
        
    async def async_setup(self) -> None:
        """Set up coordinator."""
        self.device = BloodPressureMonitor(self.address)
        self.device.set_callback(self._handle_update)
        
        await self._register_device()
        
        self._cancel_scan = async_track_time_interval(
            self.hass, self._try_connect, SCAN_INTERVAL
        )
        
        for _ in range(3):
            await self._try_connect()
            if self._connected:
                break
            await asyncio.sleep(1)
        
    async def _register_device(self) -> None:
        """Register device in device registry."""
        device_registry = dr.async_get(self.hass)
        device_registry.async_get_or_create(
            config_entry_id=self.entry_id,
            identifiers={(DOMAIN, self.address)},
            name="Blood Pressure Monitor",
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            connections={(dr.CONNECTION_BLUETOOTH, self.address)},
        )
    
    @callback
    def _handle_update(self, source: str, data: Any) -> None:
        """Handle updates from device."""
        if source == "systolic":
            self._systolic = data
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "systolic", data
            )
        elif source == "diastolic":
            self._diastolic = data
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "diastolic", data
            )
        elif source == "map":
            self._map = data
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "map", data
            )
        elif source == "pulse":
            self._pulse = data
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "pulse", data
            )
        elif source == "user_id":
            self._user_id = data
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "user_id", data
            )
        elif source == "timestamp":
            self._timestamp = data
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "timestamp", data
            )
        elif source == "measurement_complete":
            self._measurement_complete = data
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "measurement_complete", data
            )
        elif source == "connected":
            self._connected = True
            self._connecting = False
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "connected", None
            )
        elif source == "disconnected":
            self._connected = False
            self._connecting = False
            # НЕ обнуляем данные! Только отправляем статус
            async_dispatcher_send(
                self.hass, f"{DOMAIN}_{self.entry_id}_update", "disconnected", None
            )
    
    async def _try_connect(self, now=None) -> None:
        """Try to connect to device."""
        if self._shutdown or self._connected or self._connecting:
            return
            
        self._connecting = True
        
        try:
            if self.device:
                success = await self.device.async_connect()
                if not success:
                    self._connecting = False
        except Exception:
            self._connecting = False
    
    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        self._shutdown = True
        
        if self._cancel_scan:
            self._cancel_scan()
            self._cancel_scan = None
        
        if self.device:
            if self.device.connected:
                await self.device.async_disconnect()
            self.device = None
    
    @property
    def systolic(self) -> int:
        """Systolic pressure."""
        return self._systolic
    
    @property
    def diastolic(self) -> int:
        """Diastolic pressure."""
        return self._diastolic
    
    @property
    def map(self) -> int:
        """Mean Arterial Pressure."""
        return self._map
    
    @property
    def pulse(self) -> int:
        """Heart rate."""
        return self._pulse
    
    @property
    def user_id(self) -> int:
        """User ID."""
        return self._user_id
    
    @property
    def timestamp(self) -> str | None:
        """Measurement timestamp."""
        return self._timestamp
    
    @property
    def measurement_complete(self) -> bool:
        """Measurement complete status."""
        return self._measurement_complete
    
    @property
    def connected(self) -> bool:
        """Connection status."""
        return self._connected
