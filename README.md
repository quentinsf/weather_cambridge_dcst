# Home Assistant Weather from the University of Cambridge

There is a weather station on the roof of the Department of Computer Science & Technology (formerly the Computer Lab), in the west part of Cambridge, UK.  For more information about it, see [the web page](https://www.cl.cam.ac.uk/research/dtg/weather/).

This is a custom component for [Home Assistant](https://home-assistant.io) that will let you use it as a standard weather source.

## Installation

Note that the directory layout for custom components changed in Home Assistant 0.88, so these instructions assume you're running a more recent version than that.

* In your Home Assistant config directory, create a folder called `custom_components`, if you don't already have one. 
* Within that, create a `cambridge_dcst` folder.
* Download or check out the `weather.py`, `__init__.py` and `manifest.json` files and put them there. An easy way is to change into that directory and do:

      curl -O https://raw.githubusercontent.com/quentinsf/weather_cambridge_dcst/master/manifest.json
      curl -O https://raw.githubusercontent.com/quentinsf/weather_cambridge_dcst/master/__init__.py
      curl -O https://raw.githubusercontent.com/quentinsf/weather_cambridge_dcst/master/weather.py


  So in your config directury you should have:

      config/custom_components/cambridge_dcst/weather.py
      config/custom_components/cambridge_dcst/__init__.py
      config/custom_components/cambridge_dcst/manifest.json

* Add the following lines to your `configuration.yaml`:

      weather:
       - platform: cambridge_dcst

You should then have a `weather.cambridge_dcst` entity.

* Restart Home Assistant

## Viewing the results

In the Lovelace UI, you can use a standard 'weather_forecast` card:

    - entity: weather.cambridge_dcst
      type: weather-forecast

## Getting updates

An easy way to keep this and other components up to date is to use the [custom updater](https://github.com/custom-components/custom_updater).  If you've got this in your system, you can put the following in your configuration:

    custom_updater:
      component_urls:
        - https://raw.githubusercontent.com/quentinsf/weather_cambridge_dcst/master/custom_updater.json

## Plotting the history

If, like me, you like plotting graphs of the values of some of the attributes, like temperature or pressure, you may need to extract them as a separate sensor before using them in, say, [the Lovelace history_graph card](https://www.home-assistant.io/lovelace/history-graph/).  You can use a template sensor to do that in your `configuration.yaml`, for example:

    sensor:
      - platform: template
        sensors:

          computer_lab_temperature:
            friendly_name: 'Outside temp (Computer Lab)'
            value_template: "{{ state_attr('weather.cambridge_dcst', 'temperature') }}"
            entity_id: weather.cambridge_dcst
            icon_template: mdi:thermometer
            unit_of_measurement: "°C"


Then you can use `sensor.computer_lab_temperature` elsewhere in your system, and its historic data will start to be recorded.
