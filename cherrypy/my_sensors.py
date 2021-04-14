#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import socket
import cherrypy
import sensors
import time

from subprocess import getstatusoutput as unix
from cherrypy.lib import file_generator

pysensorconfig = {
    'k10temp-pci-00c3' : {
        'temp1': ('temp1_max'),
        'label': "AMD Ryzen 5 2600",
    },
    'nouveau-pci-0900' : {
        'temp1': ('temp1_max'),
        'label': "GT710",
    },
    'asuswmisensors-isa-0000' : {
        'fan1':(), 'fan2':(), 'fan3':(), 'fan4':(), 'temp1':(), 'temp2':(), 'temp3':(), 'temp4':()
    }
}

__page__ = '<!DOCTYPE html>\n'\
'<html>\n<head>\n'\
'<title>Proxmox Sensors</title><meta http-equiv="refresh" content="30">\n'\
'<link rev="stylesheet" type="text/css" href="./static/style.css" rel="stylesheet" media="screen,all">\n'\
'</head>\n'\
'<body>\n<h1>Proxmox Sensors</h1>\n'\
'%s\n'\
'</body>\n</html>'

__sensors_div__ = ' <div > <h3>Sensors: [%s]</h3> %s </div>'
__drives_div__ = ' <div > <h3>Drive Temps:</h3> %s </div>'
__zpool_div__ = ' <div > <h3>Zpool Status:</h3> %s </div>'
__usage_div__ = ' <div > <h3>Disk Usage:</h3> %s </div>'

def create_table(col1, col2, col3, col4):
    #html = '<table><tr>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n</tr></table>\n'
    column1 = '<div id="sensors" class="grid-item">%s%s</div>' % (col1, col2)
    column2 = '<div id="sensors" class="grid-item">%s%s</div>' % (col3, col4)
    html = '<div class="grid-container"> %s %s</div>'
    return html % (column1, column2)


#def get_sensors():
#    """call sensors"""
#    st, ret = unix('sensors | grep -v -e Voltage -e "Pump:" -e "OPT:" -e "Tsensor 1" -e VRM')
#    ret = ret.replace(chr(176),"&deg;")
#    html = '<pre>'
#    for line in ret.split('\n'):
#        html += line+'<br>'
#    html += '</pre>'
#    return html


def get_drive_temps(pwd):
    """run the drive temps script"""
    st, ret = unix(pwd+'/zfs_drive_temps.sh -t')
    if ret.startswith('\n'):
        ret = ret[1:]
    html = '<pre>\n'
    for line in ret.split('\n'):
        if line.find("Celsius") > -1:
            tempC = int(line.split()[1])
            html += "<meter max=75 min=0 value=%d high=40 low=30 optimum=19></meter> " % tempC
        html += line.replace(' Celsius', '&deg;C').replace('-',' ').replace('_',' ')+'<br>'
    html += '</pre>'
    return html


def get_zpool_status():
    """call zpool status"""
    st, ret = unix("su judge -c 'zpool status -c size'")
    html = '<pre>\n'
    cksum = False
    for line in ret.split('\n'):
        meter = "        "
        if line.find('state:') > -1:
            if line.find("ONLINE"):
                meter = "<meter id=\"bullet\" max=10 min=0 value=10 high=9 low=2 optimum=10></meter> "
            else:
                meter = "<meter id=\"bullet\"  max=10 min=0 value=10 high=9 low=2 optimum=0></meter> "
            html += line+" "+meter+"<br>"
        elif line.find("CKSUM") > -1:
            cksum = True
            html += "  "+line[1:]+'<br>'
        elif len(line.strip()) == 0:
            cksum = False
            html += '<br>'
        elif cksum:
            if line.find("ONLINE"):
                meter = "<meter id=\"bullet\" max=10 min=0 value=10 high=9 low=2 optimum=10></meter> "
            else:
                meter = "<meter id=\"bullet\" max=10 min=0 value=10 high=9 low=2 optimum=0></meter> "
            html += meter+line[1:]+"<br>"
        else:
            html += line+'<br>'
        print(len(line))
    html += '</pre>'
    return html


def get_usage():
    """get disk usage"""
    st, ret = unix("df -h | egrep 'zdata|zvideos|pve|Filesystem'")
    html = '<pre>\n'
    for line in ret.split('\n'):
        try:
            perc = int(line.split()[4].replace('%',''))
            html += "<meter max=100 min=0 value=%d high=75 low=50 optimum=19></meter> " % perc
        except ValueError:
            html += "         "
        html += line+'<br>'
    html += '</pre>'
    return html


def get_time():
    """return a current time stamp"""
    return time.asctime()


def pysensors():
    """use python sensors package to collect sensor data"""
    #print(f"Using sensors library {sensors.VERSION} ({sensors.LIB_FILENAME})")
    #print()

    html = '<pre>'
    #print(dir(sensors))
    sensors.init()
    try:
        #print(config)
        for chip in sensors.iter_detected_chips():
            if str(chip) in pysensorconfig:
                #print(chip)
                html += str(chip)+'<br>'
                #print('Adapter:', chip.adapter_name)
                #print(repr(config[str(chip)]))
                for feature in chip:
                    #print(config[chip])
                    if feature.name in pysensorconfig[str(chip)]:
                        if 'label' in pysensorconfig[str(chip)]:
                            label = pysensorconfig[str(chip)]['label']
                        else:
                            label = feature.label
                        #print(feature.name)
                        if feature.name.startswith('fan'):
                            #print("%-25s %4d RPM" % (label+':', feature.get_value()))
                            html += "%-25s %4d RPM " % (label+':', feature.get_value())
                            html += "<meter max=2000 min=0 value=%d high=1250 low=750 optimum=100></meter> <br>" % feature.get_value()
                        if feature.name.startswith('temp'):
                            #print("%-27s %4.1f C" % (label+':', feature.get_value()))
                            html += "%-27s %4.1f&deg;C " % (label+':', feature.get_value())
                            html += "<meter max=110.0 min=0.0 value=%f high=70.0 low=40.0 optimum=10.0></meter> </br>" % feature.get_value()
                            #f"{label!r}:"
                            #f" {feature.get_value():.1f}"
                        #)
                        for subfeature in feature:
                            if str(subfeature.name) in pysensorconfig[str(chip)][feature.name]:
                                #print(f"  {subfeature.name}: {subfeature.get_value():.1f}")
                                #print("     (%s: %4.1f C)" % (subfeature.name, subfeature.get_value()))
                                html += "     (%s: %4.1f&deg;C) <br>" % (subfeature.name, subfeature.get_value())
                #print()
                html += '<br>'
    finally:
        sensors.cleanup()
    return html


class CherrySensors(object):

    def __init__(self, pwd):
        self.pwd = pwd

    @cherrypy.expose
    def index(self):
        shtml = __sensors_div__ % (get_time(), pysensors())
        thtml = __drives_div__ % get_drive_temps(self.pwd)
        zhtml = __zpool_div__ % get_zpool_status()
        uhtml = __usage_div__ % get_usage()
        html = create_table(shtml, thtml, zhtml, uhtml)
        return self.redirect(html)

    def redirect(self, html):
        return __page__ % (html)


if __name__ == '__main__':

    print(sys.argv)
    if len(sys.argv) > 1:
        if sys.argv[1] == "debug":
            #print(get_sensors())
            get_zpool_status()
            sys.exit()

    pwd = '/root/proxmox_cherrypy' #os.getcwd()
    hostname = socket.gethostname()
    open(pwd+'/error.log', 'w').write('')

    conf = {'/static':{'tools.staticdir.on' : True, 
                       'tools.staticdir.dir': pwd+'/static'},
           }

    cherrypy.config.update({'server.socket_host': hostname,
                            'server.socket_port': 8080,
                            'server.thread_pool': 10,
                           })
    cherrypy.config.update({'log.access_file': '',
                            'log.error_file': pwd+'/error.log'})
    cherrypy.config.update({'log.screen': False})

    # run the webapp
    cherrypy.quickstart(CherrySensors(pwd), '/', conf)


