"""Support for powervault sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from powervaultpy import PowerVault

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, POWERVAULT_COORDINATOR
from .entity import PowervaultEntity
from .models import PowervaultRuntimeData

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the powerwall sensors."""
    powerwall_data: PowervaultRuntimeData = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = powerwall_data[POWERVAULT_COORDINATOR]
    assert coordinator is not None
    data = coordinator.data
    entities: list[PowervaultEntity] = [
        PowerWallChargeSensor(powerwall_data),
    ]

    if data.backup_reserve is not None:
        entities.append(PowerWallBackupReserveSensor(powerwall_data))

    for meter in data.meters.meters:
        entities.append(PowerWallExportSensor(powerwall_data, meter))
        entities.append(PowerWallImportSensor(powerwall_data, meter))
        entities.extend(
            PowerWallEnergySensor(powerwall_data, meter, description)
            for description in POWERWALL_INSTANT_SENSORS
        )

    async_add_entities(entities)

