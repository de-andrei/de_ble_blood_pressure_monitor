"""Text sensor platform for DE BLE Blood Pressure Monitor."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.text_sensor import TextSensorEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up text sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TimestampSensor(coordinator, entry),
    ])

class TimestampSensor(TextSensorEntity):
    """Representation of measurement timestamp."""

    _attr_has_entity_name = True
    _attr_name = "Last Measurement Time"
    _attr_icon = "mdi:clock"
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
