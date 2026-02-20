DOMAIN = "vilniaus_transportas"
PLATFORMS = ["device_tracker"]

async def async_setup_entry(hass, entry):
    """Set up Vilnius Transport from a config entry."""
    # Perduodame maršruto informaciją į device_tracker
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


