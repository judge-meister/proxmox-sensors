#!/bin/bash

error_exit()
{
  echo $1
  exit 1
}

check_dependencies()
{
  which python3 >/dev/null
  [ $? -ne 0 ] && error_exit "python3 required"

  which pip3 >/dev/null
  [ $? -ne 0 ] && error_exit "pip3 required"

  # install the python requirements
  sudo pip3 -q install -r requirements.txt 
}

choice() # give the user a choice with a default option
{
  text=$1
  opts=$2
  dflt=$3
  t=0
  while [ $t -eq 0 ]
  do
    echo -n "$text"
    read ans
    [ "$ans" == "" ] && ans=$dflt
    [[ $opts =~ "$ans" ]] && t=1
  done
}

query() # ask user for an answer with a default option
{
  text=$1
  dflt=$2
  echo -n "$text"
  read ans
  [ "$ans" == "" ] && ans=$dflt
}

uninstall_service()
{
  install_dir=$(dirname $(grep ExecStart cherrypy/systemd/my_sensors.service | awk -F' ' '{print $2}'))

  sudo systemctl stop my_sensors.timer
  sudo systemctl stop my_sensors.service
  sudo systemctl disable my_sensors.timer 

  rm -f /etc/systemd/system/my_sensors.{timer,service}
}

remove_cherrypy()
{
  rm -f $install_dir/my_sensors.py $install_dir/zfs_drive_temps.sh $install_dir/error.log
  rm -rf $install_dir/static/style.css

  # check dir is empty before removing it.
  [[ -d $install_dir/static ]] && [[ -z "$(ls -A $install_dir/static)" ]] && rm -rf $install_dir/static
  [[ -d $install_dir ]] && [[ -z "$(ls -A $install_dir)" ]] && rm -rf $install_dir
}

install_cherrypy()
{
  # create a folder in opt and install to there
  sudo mkdir -p $location/static
  sudo install -m 755 -t $location  my_sensors.py zfs_drive_temps.sh
  sudo install -m 644 -t $location/static  static/style.css
}

install_service()
{
  # install systemd files
  sed 's#/opt/proxmox-sensors#'$location'#g' systemd/my_sensors.service systemd/temp.service
  sudo install -m 644 -t /etc/systemd/system systemd/my_sensors.timer
  sudo install -m 644 -T systemd/temp.service /etc/systems/system/my_sensors.service
  rm -f systemd/temp.service

  # start timer service
  sudo systemctl daemon-reload
  sudo systemctl start my_sensors.timer
  sudo systemctl enable my_sensors.timer
}

install_developer_mode()
{
  # use repo as run location
  location=$(pwd)/cherrypy
  install_service
}

# ----------
# START HERE
# ----------

root=$(pwd)
if [ "${root}" != "$(git rev-parse --show-toplevel 2>/dev/null)" ] && error_exit "Must run $0 from root of repo."

cd cherrypy

check_dependencies

if [ -f /etc/systemd/system/my_sensors.timer ] 
then
  choice "Uninstall pre-existing instance ? (y/n) [y] " "yn" "y"
  if [ "$ans" == "y" ]
  then
    uninstall_service
    cd $install_dir
    [ "$(git rev-parse --is-inside-work-tree &>/dev/null; echo "${?}")" != '0' ] && remove_cherrypy
    #[ "$install_dir" != "${root}/cherrypy" ] && remove_cherrypy
    cd -
  fi
fi

choice "Install as [u]ser or [d]eveloper mode ? [u] " "ud" "u"
install_type=$ans

case $install_type in

  u) query "Install location [/opt/proxmox-sensors]: " "/opt/proxmox-sensors" ;
     location=$ans ;
     install_cherrypy ; 
     install_service ;;

  d) install_developer_mode ;;
esac


