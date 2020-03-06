# resol

SmarthomeNG-Plugin to read Resol datalogger: 
http://www.resol.de/index/produktdetail/kategorie/4/id/8/sprache/de
http://www.cosmo-info.de/fileadmin/user_upload/DL/COSMO-Solarregelung/COSMO-Multi.pdf

## Notes

This plugin is still __under development__! 
Many thank @MARKOV

## Prerequisite

The following python packages need to be installed on your system:
- none

## Installation

```
cd smarthome.py directory
cd plugins
git clone https://github.com/KHome/resol.git
```

### plugin.yaml

```
resol:
    class_name: Resol
    class_path: plugins.resol
    ip: 192.168.178.111    # ip of VBUS LAN
    cycle: 60
    port: 7053    # port of VBUS LAN usualy is 7053!
    password: xxx
```
More information of resol parameter and sources, see here: https://danielwippermann.github.io/resol-vbus/vbus-packets.html
Install Programm Resol Service Center to read offset und Bituse:
- They are provided in XML by RESOL as part of the RSC (Resol Service Center) download. Just download, install (on linux use wine, it will work) and get the required file for your installation from: {Install_dir}/eclipse/plugins/de.resol.servicecenter.vbus.resol_2.0.0/ -

### items.yaml

```yaml

resol:
    resol_source: '0x7821'
    resol_destination: '0x0010'
    resol_command: '0x0100'

    Solar_Temperatur_Kollektor_aussen_S1:
        type: num
        knx_dpt: 9
        visu: 'yes'
        visu_acl: ro
        sqlite: 'yes'
        cache: 'yes'
        enforce_updates: 'true'
        # knx_send: 15/0/0
        # knx_reply: 15/0/0
        json_variable: 'Temperatur Sensor 1'
        resol_offset: 0
        resol_bituse: 15
        resol_factor: '0.1'

    Solar_Temperatur_Heizkreis_Ruecklauf_ungemischt_S8:
        type: num
        knx_dpt: 9
        visu: 'yes'
        visu_acl: ro
        sqlite: 'yes'
        cache: 'yes'
        enforce_updates: 'true'
        # knx_send: 15/0/1
        # knx_reply: 15/0/1
        json_variable: 'Temperatur Sensor 8'
        resol_offset: 14
        resol_bituse: 15
        resol_factor: '0.1'

    Solar_Temperatur_Heizkreis_Ruecklauf_gemischt_S9:
        type: num
        knx_dpt: 9
        visu: 'yes'
        visu_acl: ro
        sqlite: 'yes'
        cache: 'yes'
        enforce_updates: 'true'
        # knx_send: 15/0/2
        # knx_reply: 15/0/2
        json_variable: 'Temperatur Sensor 9'
        resol_offset: 16
        resol_bituse: 15
        resol_factor: '0.1'

```
