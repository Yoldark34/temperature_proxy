"""Shared test helpers for Temperature Proxy tests."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.temperature_proxy.const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MockTemperatureSensor(SensorEntity):
    """A fake sensor.* entity with device_class temperature."""

    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        unique_id: str,
        name: str,
        value: str | None = "20.0",
        unit: str = UnitOfTemperature.CELSIUS,
    ) -> None:
        self.hass = hass
        self.entity_id = f"sensor.{unique_id}"
        self._attr_name = name
        self._attr_device_class = "temperature"
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = value

    async def async_update_native_value(self, value: str | None) -> None:
        """Test helper: push a new reading and notify listeners."""
        self._attr_native_value = value
        self.async_write_ha_state()


class MockHumiditySensor(SensorEntity):
    """A fake sensor.* entity that is NOT a temperature sensor."""

    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, unique_id: str, name: str, value: str = "45") -> None:
        self.hass = hass
        self.entity_id = f"sensor.{unique_id}"
        self._attr_name = name
        self._attr_device_class = "humidity"
        self._attr_native_value = value


async def register_mock_entity(hass: HomeAssistant, entity: Entity, domain: str) -> None:
    """Register a bare entity directly, bypassing config entries."""
    component = EntityComponent(_LOGGER, domain, hass)
    await component.async_add_entities([entity])
    await hass.async_block_till_done()


async def setup_proxy_entry(
    hass: HomeAssistant, title: str = "Test Proxy", data: dict | None = None
) -> MockConfigEntry:
    """Create and set up a Temperature Proxy config entry."""
    entry = MockConfigEntry(domain=DOMAIN, title=title, data=data or {})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def select_source(hass: HomeAssistant, select_entity_id: str, source_entity_id: str) -> None:
    """Pick a source sensor through the select entity's service call."""
    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": select_entity_id, "option": source_entity_id},
        blocking=True,
    )
    # blocking=True only waits for the service handler coroutine itself;
    # the sensor/text entities react to the resulting state_changed event
    # via listeners that are not guaranteed to have finished executing yet.
    await hass.async_block_till_done()
