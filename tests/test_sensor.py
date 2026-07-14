"""Tests for the Temperature and Source Name mirror sensors."""
from homeassistant.core import HomeAssistant

from custom_components.temperature_proxy.const import (
    UNIQUE_ID_NAME_SENSOR,
    UNIQUE_ID_SELECT,
    UNIQUE_ID_VALUE_SENSOR,
)
from custom_components.temperature_proxy.helpers import async_get_entity_id

from .common import MockTemperatureSensor, register_mock_entity, select_source, setup_proxy_entry


async def test_sensors_unavailable_before_any_selection(hass: HomeAssistant) -> None:
    """With nothing selected, the value sensor is unavailable and the name sensor unknown."""
    entry = await setup_proxy_entry(hass)
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)
    name_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_NAME_SENSOR)

    assert hass.states.get(value_entity_id).state == "unavailable"
    assert hass.states.get(name_entity_id).state == "unknown"


async def test_sensors_mirror_selected_source(hass: HomeAssistant) -> None:
    """Once a source is selected, both sensors reflect its value/name."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen", value="21.5"), "sensor"
    )
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)
    name_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_NAME_SENSOR)

    await select_source(hass, select_entity_id, "sensor.kitchen")

    value_state = hass.states.get(value_entity_id)
    assert value_state.state == "21.5"
    assert value_state.attributes["tracked_sensor"] == "sensor.kitchen"
    assert hass.states.get(name_entity_id).state == "Kitchen"


async def test_value_sensor_tracks_live_updates_from_source(hass: HomeAssistant) -> None:
    """Changes to the underlying sensor propagate without re-selecting anything."""
    sensor = MockTemperatureSensor(hass, "kitchen", "Kitchen", value="21.5")
    await register_mock_entity(hass, sensor, "sensor")
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)
    await select_source(hass, select_entity_id, "sensor.kitchen")

    await sensor.async_update_native_value("18.2")
    await hass.async_block_till_done()

    assert hass.states.get(value_entity_id).state == "18.2"


async def test_sensors_switch_when_selection_changes(hass: HomeAssistant) -> None:
    """Switching the selector re-points both sensors at the newly chosen source."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen", value="21.5"), "sensor"
    )
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "garden", "Garden", value="9.0"), "sensor"
    )
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)
    name_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_NAME_SENSOR)

    await select_source(hass, select_entity_id, "sensor.kitchen")
    assert hass.states.get(value_entity_id).state == "21.5"

    await select_source(hass, select_entity_id, "sensor.garden")

    assert hass.states.get(value_entity_id).state == "9.0"
    assert hass.states.get(name_entity_id).state == "Garden"


async def test_value_sensor_unavailable_when_source_unavailable(hass: HomeAssistant) -> None:
    """If the underlying sensor becomes unavailable, the proxy value follows suit."""
    sensor = MockTemperatureSensor(hass, "kitchen", "Kitchen", value="21.5")
    await register_mock_entity(hass, sensor, "sensor")
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)
    await select_source(hass, select_entity_id, "sensor.kitchen")

    hass.states.async_set("sensor.kitchen", "unavailable")
    await hass.async_block_till_done()

    assert hass.states.get(value_entity_id).state == "unavailable"
