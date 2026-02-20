import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

# Turi būti identiškas manifest.json failui
DOMAIN = "vilniaus_viesasis_transportas"

class VilniusTransportConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vilnius Transport."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Čia vėliau galėsi pridėti maršruto patikrinimą
            return self.async_create_entry(
                title=f"Maršrutas: {user_input['route']}", 
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("route"): str,
            }),
            errors=errors,
        )
