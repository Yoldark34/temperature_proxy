"""Tests for the Source Sensor select entity."""
from homeassistant.core import HomeAssistant, State
from pytest_homeassistant_custom_component.common import mock_restore_cache

from custom_components.temperature_proxy.const import (
    UNIQUE_ID_SELECT,
    UNIQUE_ID_VALUE_SENSOR,
)
from custom_components.temperature_proxy.helpers import async_get_entity_id

from .common import (
    MockHumiditySensor,
    MockTemperatureSensor,
    register_mock_entity,
    select_source,
    setup_proxy_entry,
)


async def test_options_only_include_temperature_sensors(hass: HomeAssistant) -> None:
    """Only sensor.* entities with device_class temperature are offered."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen"), "sensor"
    )
    await register_mock_entity(
        hass, MockHumiditySensor(hass, "kitchen_humidity", "Kitchen Humidity"), "sensor"
    )

    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)

    assert hass.states.get(select_entity_id).attributes["options"] == ["sensor.kitchen"]


async def test_proxy_excludes_its_own_sensor_from_options(hass: HomeAssistant) -> None:
    """A proxy can never be pointed at its own mirrored value sensor."""
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    value_entity_id = async_get_entity_id(
        hass, "sensor", entry.entry_id, UNIQUE_ID_VALUE_SENSOR
    )

    options = hass.states.get(select_entity_id).attributes["options"]
    assert value_entity_id not in options


async def test_selecting_option_updates_state(hass: HomeAssistant) -> None:
    """Calling select.select_option updates the select's state."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen"), "sensor"
    )
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)

    await select_source(hass, select_entity_id, "sensor.kitchen")

    assert hass.states.get(select_entity_id).state == "sensor.kitchen"


async def test_option_cleared_when_source_removed(hass: HomeAssistant) -> None:
    """If the selected sensor disappears, the selection is cleared, not left dangling."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen"), "sensor"
    )
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    await select_source(hass, select_entity_id, "sensor.kitchen")

    hass.states.async_remove("sensor.kitchen")
    await hass.async_block_till_done()

    assert hass.states.get(select_entity_id).state == "unknown"
    assert "sensor.kitchen" not in hass.states.get(select_entity_id).attributes["options"]


async def test_newly_added_temperature_sensor_appears_in_options(hass: HomeAssistant) -> None:
    """A sensor added after setup shows up in the options without a restart."""
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    assert hass.states.get(select_entity_id).attributes["options"] == []

    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "garden", "Garden"), "sensor"
    )

    assert hass.states.get(select_entity_id).attributes["options"] == ["sensor.garden"]


async def test_selection_restored_after_restart(hass: HomeAssistant) -> None:
    """The select entity restores its last choice via RestoreEntity, no helper needed."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen"), "sensor"
    )
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    await select_source(hass, select_entity_id, "sensor.kitchen")

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    mock_restore_cache(hass, [State(select_entity_id, "sensor.kitchen")])

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(select_entity_id).state == "sensor.kitchen"


async def test_restore_ignored_if_sensor_no_longer_exists(hass: HomeAssistant) -> None:
    """A restored selection pointing at a sensor that's gone is dropped, not kept dangling."""
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    mock_restore_cache(hass, [State(select_entity_id, "sensor.long_gone")])

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(select_entity_id).state == "unknown"
