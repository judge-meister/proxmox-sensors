#!/bin/bash

# Clone the git repository: 

git clone https://github.com/electrified/asus-wmi-sensors.git

# Build the module 
cd asus-wmi-sensors

sudo make dkms

# Insert the module 

sudo modprobe asus-wmi-sensors

# Run ```sensors``` and you should see a ```asuswmisensors-isa-0000``` device and readouts as you see in the UEFI interface.

# Optional - consult your distro's documentation for info on how to make the module be loaded automatically at boot
grep '^asus-wmi-sensors$' /etc/modules > /dev/null
if test $? -ne 0
then
  echo asus-wmi-sensors | sudo tee -a /etc/modules
fi

