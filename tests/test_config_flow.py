"""Tests for the Temperature Proxy config flow."""
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.temperature_proxy.const import DOMAIN


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """A valid name creates a config entry titled after that name."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Living Room Proxy"}
    )
    assert result2["type"] == "create_entry"
    assert result2["title"] == "Living Room Proxy"


async def test_user_flow_rejects_blank_name(hass: HomeAssistant) -> None:
    """A blank/whitespace-only name re-shows the form with an error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "   "}
    )
    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "name_required"}


async def test_multiple_instances_allowed(hass: HomeAssistant) -> None:
    """Several proxies can coexist, each as its own config entry."""
    for name in ("Proxy A", "Proxy B"):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        await hass.config_entries.flow.async_configure(
            result["flow_id"], {"name": name}
        )
    await hass.async_block_till_done()

    titles = {e.title for e in hass.config_entries.async_entries(DOMAIN)}
    assert titles == {"Proxy A", "Proxy B"}
