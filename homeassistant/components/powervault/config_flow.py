"""Config flow for Powervault integration."""
from __future__ import annotations

import logging
from typing import Any

from powervaultpy import PowerVault
from powervaultpy.powervault import RequestError, ServerError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import selector

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_key"): str,
    }
)

STEP_PICK_UNIT_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("unit_id"): str,
    }
)


async def validate_unit(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    powervault = PowerVault(data["api_key"])

    account_id = None
    units = None
    try:
        account_response = await hass.async_add_executor_job(powervault.get_account)
        account_id = account_response["id"]
        units = await hass.async_add_executor_job(powervault.get_units, account_id)

    except RequestError:
        raise InvalidAuth
    except ServerError:
        raise CannotConnect

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth
    units_ = []
    for unit in units:
        units_.append(unit["id"])

    # Return info that you want to store in the config entry.
    return {"units": units_, "account_id": account_id}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Powervault."""

    VERSION = 1

    async def async_step_pick_unit(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Save the picked unit id
            self.unit_id = user_input["unit_id"]
            self.unit_name = user_input["unit_name"]

            # Now we can create the entity

            return self.async_create_entry(
                title=f"Powervault - {self.unit_name}",
                data={"api_key": self.api_key, "unit_id": self.unit_id},
            )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                self.account_info = info
                self.api_key = user_input["api_key"]
                data_schema = {
                    vol.Required("unit_name"): str,
                }
                data_schema["unit_id"] = selector(
                    {
                        "select": {
                            "options": info["units"],
                        }
                    }
                )

                return self.async_show_form(
                    step_id="pick_unit", data_schema=vol.Schema(data_schema)
                )

                # return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
