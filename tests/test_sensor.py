"""Tests for the Temperature mirror sensor, including its dynamic name."""
from homeassistant.core import HomeAssistant

from custom_components.temperature_proxy.const import UNIQUE_ID_SELECT, UNIQUE_ID_VALUE_SENSOR
from custom_components.temperature_proxy.helpers import async_get_entity_id

from .common import MockTemperatureSensor, register_mock_entity, select_source, setup_proxy_entry


async def test_sensor_unavailable_before_any_selection(hass: HomeAssistant) -> None:
    """With nothing selected, the value sensor is unavailable and keeps its default name."""
    entry = await setup_proxy_entry(hass, "Test Proxy")
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)

    state = hass.states.get(value_entity_id)
    assert state.state == "unavailable"
    assert state.attributes["friendly_name"] == "Test Proxy Temperature"


async def test_sensor_mirrors_selected_source_value_and_name(hass: HomeAssistant) -> None:
    """Once a source is selected, the sensor mirrors both its value and its name."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen", value="21.5"), "sensor"
    )
    entry = await setup_proxy_entry(hass, "Test Proxy")
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)

    await select_source(hass, select_entity_id, "sensor.kitchen")

    state = hass.states.get(value_entity_id)
    assert state.state == "21.5"
    assert state.attributes["tracked_sensor"] == "sensor.kitchen"
    assert state.attributes["friendly_name"] == "Test Proxy Kitchen"


async def test_name_falls_back_to_entity_id_without_prefix_when_source_has_no_friendly_name(
    hass: HomeAssistant,
) -> None:
    """If the source has no friendly_name attribute, fall back to its entity_id sans "sensor."."""
    hass.states.async_set(
        "sensor.nameless_probe", "12.3", {"device_class": "temperature"}
    )
    entry = await setup_proxy_entry(hass, "Test Proxy")
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)

    await select_source(hass, select_entity_id, "sensor.nameless_probe")

    state = hass.states.get(value_entity_id)
    assert state.state == "12.3"
    assert state.attributes["friendly_name"] == "Test Proxy nameless_probe"


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


async def test_sensor_switches_value_and_name_when_selection_changes(hass: HomeAssistant) -> None:
    """Switching the selector re-points the sensor at the newly chosen source."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen", value="21.5"), "sensor"
    )
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "garden", "Garden", value="9.0"), "sensor"
    )
    entry = await setup_proxy_entry(hass, "Test Proxy")
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    value_entity_id = async_get_entity_id(hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR)

    await select_source(hass, select_entity_id, "sensor.kitchen")
    assert hass.states.get(value_entity_id).state == "21.5"
    assert hass.states.get(value_entity_id).attributes["friendly_name"] == "Test Proxy Kitchen"

    await select_source(hass, select_entity_id, "sensor.garden")

    state = hass.states.get(value_entity_id)
    assert state.state == "9.0"
    assert state.attributes["friendly_name"] == "Test Proxy Garden"


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
