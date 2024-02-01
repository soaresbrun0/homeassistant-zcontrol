"""The ZControl® integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from pyzctrl.devices.connection import ZControlDeviceHTTPConnection

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_URL,
    Platform,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SUPPORTED_DEVICES_BY_MODEL
from .coordinator import ZControlDataUpdateCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ZControl® from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    entry_data = entry.data
    _LOGGER.debug('Config: %s', entry_data)

    device_id = entry_data[CONF_DEVICE_ID]
    device_class = SUPPORTED_DEVICES_BY_MODEL[entry_data[CONF_MODEL]]
    url = entry_data[CONF_URL]
    timeout = entry_data[CONF_TIMEOUT]
    scan_interval = timedelta(seconds = entry_data[CONF_SCAN_INTERVAL])

    device_connection = ZControlDeviceHTTPConnection(url, timeout)
    device = device_class(device_connection)
    coordinator = ZControlDataUpdateCoordinator(hass, device, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    if device.device_id is None:
        _LOGGER.error("Failed to connect to device '%s'", device_id)
        return False

    if device.device_id != device_id:
        _LOGGER.error("Connected to device '%s', but expected '%s'", device.device_id, device_id)
        return False

    _LOGGER.info("Connected to device '%s'", device_id)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
