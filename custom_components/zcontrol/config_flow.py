"""Config flow for ZControl® integration."""
from __future__ import annotations

import logging
from typing import Any

from pyzctrl.devices.connection import ZControlDeviceHTTPConnection
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_URL,
)
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    SUPPORTED_DEVICES_BY_MODEL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MODEL, default = next(iter(SUPPORTED_DEVICES_BY_MODEL))): vol.In(SUPPORTED_DEVICES_BY_MODEL.keys()),
        vol.Required(CONF_URL): cv.string,
        vol.Required(CONF_TIMEOUT, default = DEFAULT_TIMEOUT): vol.All(vol.Coerce(int), vol.Range(min=5)),
        vol.Required(CONF_SCAN_INTERVAL, default = DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=1))
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ZControl."""

    VERSION = 1

    async def _validate_user_input(self, data: dict[str, Any]) -> None:
        """Validate we can connect to the selected device."""

        device_class = SUPPORTED_DEVICES_BY_MODEL[data[CONF_MODEL]]
        url = cv.url(data[CONF_URL])
        timeout = int(data[CONF_TIMEOUT])

        device_connection = ZControlDeviceHTTPConnection(url, timeout)
        device = device_class(device_connection)
        await self.hass.async_add_executor_job(device.update)

        data[CONF_DEVICE_ID] = device.device_id
        _LOGGER.debug("Config: %s", data)


    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._validate_user_input(user_input)
            except ZControlDeviceHTTPConnection.ConnectionTimeoutError:
                errors["base"] = "timeout_connect"
            except ZControlDeviceHTTPConnection.ConnectionError:
                errors["base"] = "cannot_connect"
            else:
                model = user_input[CONF_MODEL]
                device_id = user_input[CONF_DEVICE_ID]

                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title = f"{model} ({device_id})",
                    data = user_input
                )

        return self.async_show_form(
            step_id = "user",
            data_schema = STEP_USER_DATA_SCHEMA,
            errors = errors
        )
