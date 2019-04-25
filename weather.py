"""
Weather from the roof of the 
Cambridge Dept of Computer Science and Technology

For more details about the source, please refer to
https://www.cl.cam.ac.uk/research/dtg/weather/

Incoming data looks like this:

    Cambridge Computer Laboratory Rooftop Weather at 08:01 PM on 16 Feb 19:

    Temperature:  9.2 C
    Pressure:     1022 mBar
    Humidity:     97 %
    Dewpoint:     8.7 C
    Wind:         0 knots from the S
    Sunshine:     0.0 hours (today)
    Rainfall:     0.0 mm since midnight

    Summary:      very humid, cool, calm

Quentin Stafford-Fraser
quentin@pobox.com
"""

from datetime import datetime, timedelta
import logging
import re
import requests

from homeassistant.components.weather import WeatherEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.util import Throttle

__version__ = '0.1'

DOMAIN = 'cambridge_dcst_weather'
URL = 'https://www.cl.cam.ac.uk/research/dtg/weather/current-obs.txt'

ATTRIBUTION = "Weather data from University of Cambridge Dept of Computer Science and Technology"

# Some regexes for parsing the input.
# Find key: value lines
KEY_VALUE_REGEX = re.compile(r"^(.+): \s+(.+)$", flags=re.MULTILINE)
HEADER_LINE_REGEX = re.compile(r"Cambridge Computer Laboratory Rooftop Weather at (.+ on .+):")

_LOGGER = logging.getLogger(__name__)

# Be nice to the computer lab
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=2)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Cambridge Weather platform."""
    weather = CambridgeWeather()
    add_entities([weather], True)


class CambridgeWeather(WeatherEntity):
    """Get the latest data."""

    def __init__(self):
        """Make a first call to initialize the data."""
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Cambridge DCST'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from the Computer Lab."""
        response = requests.get(URL, timeout=10)
        if response.status_code != 200:
            _LOGGER.warning("Invalid status code from Computer Lab")
            return

        text = response.text
        lines = text.split('\n')

        if not lines[0].startswith("Cambridge Computer Laboratory"):
            _LOGGER.warning("Invalid result format from Computer Lab")
            return

        # We store the received text values here, and parse each one separately
        self._rawdata = {}

        # Start with the capture time:
        try:
            self._rawdata["Capture time"] = HEADER_LINE_REGEX.findall(text)[0]
        except IndexError:
            _LOGGER.warning("Failed to find data capture time")
            return

        # Update the dict from the lines of the form 'key: value'.
        key_values = KEY_VALUE_REGEX.findall(text)
        self._rawdata.update(key_values)

    @property
    def temperature(self) -> float:
        """ Return the temperature """
        # The raw data will be of the form '12.3 C'
        return float(self._rawdata["Temperature"].split()[0])

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS
    
    @property
    def pressure(self) -> float:
        """ Return the pressure """
        # The raw data will be of the form '1024 mBar'
        return float(self._rawdata["Pressure"].split()[0])
    
    @property
    def humidity(self) -> float:
        """ Return the humidity """
        # The raw data will be of the form '65 %'
        return float(self._rawdata["Humidity"].split()[0])

    @property
    def wind_speed(self):
        """Return the wind speed."""
        # The raw data will be of the form '4 knots from the SSW'
        knots = float(self._rawdata["Wind"].split()[0])
        kmh = knots * 1.852
        return kmh

    @property
    def wind_bearing(self):
        """Return the approximate wind bearing."""
        # The raw data will be of the form '4 knots from the SSW'
        compass = self._rawdata["Wind"].split()[-1]
        compass_points = {
            "N":   0,
            "NNE": 22,
            "NE":  45,
            "ENE": 67,
            "E":   90,
            "ESE": 113,
            "SE":  135,
            "SSE": 157,
            "S":   180,
            "SSW": 202,
            "SW":  225,
            "WSW": 247,
            "W":   270,
            "WNW": 292,
            "NW":  315,
            "NNW": 337,
        }
        try:
            bearing = compass_points[compass]
        except IndexError:
            _LOGGER.warning("Could not recognise wind bearing '%s'", compass)
            bearing = 0
        return bearing

    @property
    def condition(self):
        """Return the current condition."""
        return self._rawdata['Summary']

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION
