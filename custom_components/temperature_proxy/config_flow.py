"""Config flow for Temperature Proxy."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME

from .const import DOMAIN

DEFAULT_NAME = "Temperature Proxy"


class TemperatureProxyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Temperature Proxy. Multiple instances are allowed."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            if not name:
                errors["base"] = "name_required"
            else:
                return self.async_create_entry(title=name, data={})

        schema = vol.Schema(
            {vol.Required(CONF_NAME, default=DEFAULT_NAME): str}
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
