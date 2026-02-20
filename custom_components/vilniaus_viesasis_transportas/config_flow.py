import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

DOMAIN = "vilniaus_transportas"

class VilniusTransportConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vilnius Transport."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step when user adds the integration via UI."""
        errors = {}
        if user_input is not None:
            # Sukuriame įrašą su maršruto pavadinimu kaip pavadinimu
            return self.async_create_entry(
                title=f"Maršrutas: {user_input['route']}", 
                data=user_input
            )

        # Forma, kurią matys vartotojas
        data_schema = vol.Schema({
            vol.Required("route", default="3G"): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
