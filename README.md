# proxmox-sensors

![Proxmox-Sensors](https://user-images.githubusercontent.com/70912431/115110622-448c4c00-9f74-11eb-81b8-9b10e0dcf176.png)

## Installers

install_asus_wmi_sensors.sh - will download, build and install the sensors modules for some X370/X470/B450/X399 Ryzen motherboards.

install_dark_mode.sh - will download and install the Dark theme for the Proxmox Web Interface.

install_cherrypy_app.sh - will install the sensors webapp based on the CherryPy framework.

Note: the installers presume that you have a working sudo configuration.

## Requirements

This repo needs python >= 3.7, pip3 installed.

The installer will install the PySensors and CherryPy python packages.
