#!/bin/bash

# stop and remove the old my_sensor service and timer

sudo systemctl disable my_sensor.timer
sudo systemctl disable my_sensor.service

sudo systemctl stop my_sensor.timer
sudo systemctl stop my_sensor.service

sudo rm -f /etc/systemd/system/my_sensor.service  /etc/systemd/system/my_sensor.timer
sudo systemctl daemon-reload

# need to think about whether dkms is configured properly for auto upgrading asus-wmi-sensors module

