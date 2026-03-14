"""Sensor platform for DE BLE Blood Pressure Monitor."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPressure,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SystolicSensor(coordinator, entry),
        DiastolicSensor(coordinator, entry),
        MAPSensor(coordinator, entry),
        PulseSensor(coordinator, entry),  # Возвращаем PulseSensor
        UserIDSensor(coordinator, entry),
        TimestampSensor(coordinator, entry),
        MeasurementCompleteSensor(coordinator, entry),
        ConnectionSensor(coordinator, entry),
    ])

class SystolicSensor(SensorEntity):
    """Representation of systolic pressure sensor."""

    _attr_native_unit_of_measurement = UnitOfPressure.MMHG
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Systolic"
    _attr_icon = "mdi:heart"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_systolic"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "systolic":
                self._attr_native_value = data
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.systolic

class DiastolicSensor(SensorEntity):
    """Representation of diastolic pressure sensor."""

    _attr_native_unit_of_measurement = UnitOfPressure.MMHG
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Diastolic"
    _attr_icon = "mdi:heart-outline"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_diastolic"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "diastolic":
                self._attr_native_value = data
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.diastolic

class MAPSensor(SensorEntity):
    """Representation of Mean Arterial Pressure sensor."""

    _attr_native_unit_of_measurement = UnitOfPressure.MMHG
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Mean Arterial Pressure"
    _attr_icon = "mdi:heart-box"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_map"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "map":
                self._attr_native_value = data
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.map

class PulseSensor(SensorEntity):
    """Representation of pulse/heart rate sensor."""

    # Явно указываем "bpm" как строку
    _attr_native_unit_of_measurement = "bpm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Pulse"
    _attr_icon = "mdi:heart-pulse"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_pulse"  # Уникальный ID оставляем pulse
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "pulse":  # Слушаем событие "pulse" от координатора
                self._attr_native_value = data
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.pulse

class UserIDSensor(SensorEntity):
    """Representation of user ID sensor."""

    _attr_has_entity_name = True
    _attr_name = "User ID"
    _attr_icon = "mdi:account"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_user_id"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "user_id":
                self._attr_native_value = data
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.user_id

class TimestampSensor(SensorEntity):
    """Representation of measurement timestamp as sensor."""

    _attr_has_entity_name = True
    _attr_name = "Last Measurement Time"
    _attr_icon = "mdi:clock"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_timestamp"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "timestamp":
                self._attr_native_value = data
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> str | None:
        """Return the state."""
        return self.coordinator.timestamp

class MeasurementCompleteSensor(SensorEntity):
    """Representation of measurement complete status as sensor."""

    _attr_has_entity_name = True
    _attr_name = "Measurement Complete"
    _attr_icon = "mdi:check-circle"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_measurement_complete"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "measurement_complete":
                self._attr_native_value = data
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> str:
        """Return the state."""
        return "Complete" if self.coordinator.measurement_complete else "Waiting"

class ConnectionSensor(SensorEntity):
    """Representation of connection status."""

    _attr_has_entity_name = True
    _attr_name = "Connection Status"
    _attr_icon = "mdi:bluetooth-connect"
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_connection"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source in ["connected", "disconnected"]:
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> str:
        """Return the state."""
        if self.coordinator.connected:
            return "Connected"
        return "Disconnected"
    
    @property
    def icon(self) -> str:
        """Return icon based on connection state."""
        if self.coordinator.connected:
            return "mdi:bluetooth-connect"
        return "mdi:bluetooth-off"
