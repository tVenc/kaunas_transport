import logging
import urllib.request
import time
import asyncio
from datetime import timedelta

from homeassistant.helpers.event import async_track_time_interval
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

URL = "https://www.stops.lt/vilnius/gps_full.txt"
UPDATE_INTERVAL = timedelta(seconds=30)
MAX_TRACKERS = 25 

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Nustatoma integracija iš Config Flow."""
    # Gauname maršrutą, kurį įvedei pridėdamas integraciją
    route = entry.data.get("route", "3G").upper()
    
    # Sukuriame sekimo objektą
    tracker = VilniusBusTracker(hass, route)
    
    # Paleidžiame periodinį atnaujinimą
    async_track_time_interval(hass, tracker.update_bus_data, UPDATE_INTERVAL)
    
    # Pirmas paleidimas iškart
    await tracker.update_bus_data()
    
    return True

class VilniusBusTracker:
    def __init__(self, hass, route):
        self.hass = hass
        self.route = route
        self._active_ids = set()

    async def update_bus_data(self, now=None):
        """Metodas duomenų gavimui ir apdorojimui."""
        try:
            # Kadangi urllib yra blokuojanti operacija, HA aplinkoje geriau naudoti executor
            text = await self.hass.async_add_executor_job(self._fetch_data)
            if not text:
                return

            lines = text.splitlines()
            found_buses = []

            for line in lines:
                if not line.strip(): continue
                parts = [p.strip() for p in line.split(",")]
                
                # Tikriname maršrutą (parts[1])
                if len(parts) >= 6 and parts[1].upper() == self.route:
                    found_buses.append(parts)

            current_iteration_ids = set()

            for index in range(MAX_TRACKERS):
                dev_id = f"vln_{self.route.lower()}_{index + 1}"
                
                if index < len(found_buses):
                    bus = found_buses[index]
                    try:
                        lng = int(bus[4]) / 1_000_000
                        lat = int(bus[5]) / 1_000_000
                        
                        attrs = {
                            "marsrutas": str(bus[1]),
                            "reiso_id": str(bus[2]),
                            "masinos_nr": str(bus[3]),
                            "greitis": f"{bus[6]} km/h" if len(bus) > 6 else "0 km/h",
                            "statusas": "važiuoja",
                            "friendly_name": f"{self.route} maršrutas ({index + 1})",
                            "icon": "mdi:bus"
                        }

                        # Naudojame oficialų HA device_tracker matomumą
                        self.hass.states.async_set(
                            f"device_tracker.{dev_id}",
                            "home",
                            {
                                "latitude": lat,
                                "longitude": lng,
                                "source_type": "gps",
                                "gps_accuracy": 0,
                                **attrs
                            }
                        )
                        current_iteration_ids.add(dev_id)
                    except (ValueError, IndexError):
                        continue
                else:
                    # Jei autobuso nebėra sąraše, nustatome 'not_home'
                    if dev_id in self._active_ids:
                        state = self.hass.states.get(f"device_tracker.{dev_id}")
                        old_attrs = dict(state.attributes) if state else {}
                        old_attrs["statusas"] = "neaktyvus"
                        
                        self.hass.states.async_set(
                            f"device_tracker.{dev_id}",
                            "not_home",
                            old_attrs
                        )

            self._active_ids = current_iteration_ids

        except Exception as e:
            _LOGGER.error("Klaida nuskaitant Vilniaus transporto duomenis (%s): %s", self.route, e)

    def _fetch_data(self):
        """Sinchroninis duomenų siuntimas."""
        try:
            timestamped_url = f"{URL}?t={int(time.time())}"
            req = urllib.request.Request(timestamped_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode("utf-8")
        except Exception as e:
            _LOGGER.error("Tinklo klaida: %s", e)
            return None
