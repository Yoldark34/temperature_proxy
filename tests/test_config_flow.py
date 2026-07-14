"""Tests for the Temperature Proxy config flow."""
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.temperature_proxy.const import CONF_SOURCE_SENSOR, DOMAIN

from .common import MockTemperatureSensor, register_mock_entity


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """Picking a name and a source sensor creates a config entry with both."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen"), "sensor"
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"name": "Living Room Proxy", CONF_SOURCE_SENSOR: "sensor.kitchen"},
    )
    assert result2["type"] == "create_entry"
    assert result2["title"] == "Living Room Proxy"
    assert result2["data"][CONF_SOURCE_SENSOR] == "sensor.kitchen"


async def test_user_flow_rejects_blank_name(hass: HomeAssistant) -> None:
    """A blank/whitespace-only name re-shows the form with an error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "   ", CONF_SOURCE_SENSOR: "sensor.kitchen"}
    )
    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "name_required"}


async def test_multiple_instances_allowed(hass: HomeAssistant) -> None:
    """Several proxies can coexist, each as its own config entry."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen"), "sensor"
    )

    for name in ("Proxy A", "Proxy B"):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        await hass.config_entries.flow.async_configure(
            result["flow_id"], {"name": name, CONF_SOURCE_SENSOR: "sensor.kitchen"}
        )
    await hass.async_block_till_done()

    titles = {e.title for e in hass.config_entries.async_entries(DOMAIN)}
    assert titles == {"Proxy A", "Proxy B"}
