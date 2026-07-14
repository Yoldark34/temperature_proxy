"""Constants for the Temperature Proxy integration."""
from homeassistant.const import Platform

DOMAIN = "temperature_proxy"

CONF_SOURCE_SENSOR = "source_sensor"

PLATFORMS = [Platform.SELECT, Platform.SENSOR]

UNIQUE_ID_SELECT = "source_select"
UNIQUE_ID_VALUE_SENSOR = "value"

DEVICE_CLASS_TEMPERATURE = "temperature"
