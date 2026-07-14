"""Sensor entities exposing the proxied temperature value and source name."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import SourceTrackingEntity
from .const import UNIQUE_ID_NAME_SENSOR, UNIQUE_ID_VALUE_SENSOR


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(
        [
            TemperatureProxyValueSensor(entry),
            TemperatureProxySourceNameSensor(entry),
        ]
    )


class TemperatureProxyValueSensor(SourceTrackingEntity, SensorEntity):
    """Mirrors the numeric state of the currently selected temperature sensor."""

    _attr_has_entity_name = True
    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_{UNIQUE_ID_VALUE_SENSOR}"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_value = None
        self._attr_available = False
        self._attr_extra_state_attributes = {"tracked_sensor": None}

    def _async_source_updated(self, source_state: State | None) -> None:
        self._attr_extra_state_attributes = {"tracked_sensor": self._source_entity_id}

        if source_state is None or source_state.state in (
            "unknown",
            "unavailable",
            "",
        ):
            self._attr_available = False
            self._attr_native_value = None
            return

        self._attr_available = True
        self._attr_native_value = source_state.state
        self._attr_native_unit_of_measurement = source_state.attributes.get(
            "unit_of_measurement", UnitOfTemperature.CELSIUS
        )


class TemperatureProxySourceNameSensor(SourceTrackingEntity, SensorEntity):
    """Mirrors the friendly name of the currently selected temperature sensor."""

    _attr_has_entity_name = True
    _attr_name = "Source Name"
    _attr_icon = "mdi:tag-text-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_{UNIQUE_ID_NAME_SENSOR}"
        self._attr_native_value = None
        self._attr_extra_state_attributes = {"tracked_sensor": None}

    def _async_source_updated(self, source_state: State | None) -> None:
        self._attr_extra_state_attributes = {"tracked_sensor": self._source_entity_id}

        if source_state is None:
            self._attr_native_value = None
            return

        self._attr_native_value = source_state.attributes.get(
            "friendly_name", self._source_entity_id
        )
