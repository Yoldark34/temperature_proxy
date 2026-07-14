"""Global fixtures for Temperature Proxy tests."""
import pytest

pytest_plugins = "pytest_homeassistant_custom_component"  # pylint: disable=invalid-name


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):  # pylint: disable=unused-argument
    """Enable loading this custom integration in all tests."""
    yield
