"""The powervault integration models."""
from __future__ import annotations
from typing import TypedDict
from requests import Session
from dataclasses import dataclass
from powervaultpy import PowerVault

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


@dataclass
class PowervaultBaseInfo:
    """Base information for the powervault integration."""
    id: str
    model: str
    customer_name: str
    eprom_id: str

@dataclass
class PowervaultData:
    """Point in time data for the powervault integration."""
    charge: float
    metrics: dict



class PowervaultRuntimeData(TypedDict):
    """Run time data for the powerwall."""

    coordinator: DataUpdateCoordinator[PowervaultData] | None
    api_instance: PowerVault
    base_info: PowervaultBaseInfo
    api_changed: bool
    http_session: Session
