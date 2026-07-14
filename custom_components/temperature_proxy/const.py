"""Constants for the Temperature Proxy integration."""
from homeassistant.const import Platform

DOMAIN = "temperature_proxy"

PLATFORMS = [Platform.SELECT, Platform.SENSOR]

UNIQUE_ID_SELECT = "source_select"
UNIQUE_ID_VALUE_SENSOR = "value"
UNIQUE_ID_NAME_SENSOR = "source_name"

DEVICE_CLASS_TEMPERATURE = "temperature"
