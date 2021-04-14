#!/bin/bash

error_exit()
{
  echo $1
  exit 1
}
# check dependencies

which python3 >/dev/null
[ $? -ne 0 ] && error_exit "python3 required"

which pip3 >/dev/null
[ $? -ne 0 ] && error_exit "pip3 required"

# install the python requirements
sudo pip3 -q install -r requirements.txt 

# create a folder in opt and install to there
sudo mkdir -p /opt/proxmox-sensors/static
sudo install -m 755 -t /opt/proxmox-sensors  my_sensors.py zfs_drive_temps.sh
sudo install -m 644 -t /opt/proxmox-sensors/static  static/style.css

# install systemd files
sudo install -m 644 -t /etc/systemd/system  systemd/my_sensors.service systemd/my_sensors.timer
sudo systemctl daemon-reload

sudo systemctl start my_sensors.timer
sudo systemctl enable my_sensors.timer

