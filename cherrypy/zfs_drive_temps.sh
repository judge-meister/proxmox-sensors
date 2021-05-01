#!/bin/bash

export ZPOOL_SCRIPTS_AS_ROOT=1

/usr/sbin/zpool list | grep -v 'NAME' | awk -F' ' '{print $1}' | while read zp;
do
  if [ "$zp" != "no" ]
  then

  echo -e "\n"$zp":"
  /usr/sbin/zpool status $zp | egrep 'ata-' | awk -F' ' '{print $1}' | while read x; 
  do 
    d=$(ls -l /dev/disk/by-id/$x | awk -F' ' '{print $11}' | cut -d'/' -f3)
    t=$(/usr/sbin/smartctl -l scttempsts /dev/$d | grep Current | awk -F' ' '{print $3}')
  
    echo $d $t Celsius $x
  done

  fi
done

echo -e "\nOthers:"
zd=$(/usr/sbin/zpool list | grep -v NAME | awk -F' ' '{print $1}' | while read zp; do /usr/sbin/zpool status $zp | grep 'ata-'| awk -F' ' '{print $1}' | while read x; do d=$(ls -l /dev/disk/by-id/$x | awk -F' ' '{print $11}' | cut -d'/' -f3); echo " -e "$d; done; done)

for d in $(ls /dev/sd? | cut -d'/' -f3 | egrep -v ${zd});
do
    #d=$(ls -l /dev/disk/by-id/$x | awk -F' ' '{print $11}' | cut -d'/' -f3)
    t=$(/usr/sbin/smartctl -l scttempsts /dev/$d | grep Current | awk -F' ' '{print $3}')
    id=$(ls -l /dev/disk/by-id/ | grep 'ata-.*'${d}'$' | awk -F' ' '{print $9}')  
    echo $d $t Celsius $id
  
done

id=$(ls -l /dev/disk/by-id/ | grep 'nvme-.*' | grep -v -e 'eui\.' -e 'part' | awk -F' ' '{print $9}')
echo "nvme0 "$(/usr/sbin/smartctl -a /dev/nvme0 | grep Temperature: | awk -F' ' '{print $2}')" Celsius "$id

