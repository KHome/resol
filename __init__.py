#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.          http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################
  
import socket
import logging
import time

logger = logging.getLogger(__name__)

class Resol():

    def __init__(self, smarthome, ip, port, password=None, cycle=60):
        self._sh = smarthome
        self._items = []
        self._ip = ip
        self._port = int(port)
        self._cycle = int(cycle)
        self._password = password
        self._to_do = True

    def run(self):
        #logging.warning("run function")
        self.alive = True
        self._sh.scheduler.add('sock', self.sock, prio=5, cycle=self._cycle, offset=2)
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)
#
    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'resol_offset' in item.conf:
          logger.debug("ELTERN Source: " + str(item.return_parent().conf['resol_source']))
          if 'resol_bituse' in item.conf:
            self._items.append(item)
            return self.update_item
          else:
            logger.error("resol_offset found in: " + str(item) + " but no bitsize given, specify bitsize in item with resol_bitsize = ")

    def update_item(self, item, caller=None, source=None, dest=None):
        #logging.warning("update function")
        if caller != 'Resol2':
          #logger.warning("update item: {0}".format(item.id()))
          value = str(int(item()))
          #logger.warning(value)

    def sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self._ip, self._port))
        #self.result = dict()
        self.login()
        self.load_data()
        try:
          self.sock.shutdown(0)
        except:
          pass
        self.sock.close()
        self.sock = None

# Logs in onto the DeltaSol BS Plus over LAN. Also starts (and maintains) the
# actual stream of data.
    def login(self):
        dat = self.recv()
        #logger.debug("DATA: " + str(dat))

        #Check if device answered
        if dat != "+HELLO\n":
          logger.warning("WRONG REPLY FROM VBUS LAN: " + str(dat))
          return False

        #Send Password
        self.send("PASS %s\n" % self._password)

        dat = self.recv()
        #logger.debug("DATA 2: " + str(dat))

        return dat.startswith("+OK")

    def load_data(self):
        #Request Data
        global new_data
        self.send("DATA\n")
        dat = self.recv()
    
        #Check if device is ready to send Data
        if not dat.startswith("+OK"):
          logger.warning("Vbus Lan is not ready, reply: " + str(dat))
          return
        buf = self.readstream()
        msgs = self.splitmsg(buf)
        for msg in msgs:
          if "PV1" == self.get_protocolversion(msg):
            self.parse_payload(msg)

    # Receive 1024 bytes from stream
    def recv(self):
        dat = self.sock.recv(1024).decode('Cp1252')
        return dat
    
    # Sends given bytes over the stream. Adds debug
    def send(self, dat):
        self.sock.send(dat.encode('utf-8'))
    
    # Read Data until minimum 1 message is received
    def readstream(self):
        data = self.recv()
        while data.count(chr(0xAA)) < 4:
          data += self.recv()
        return data
    
    #Split Messages on Sync Byte
    def splitmsg(self, buf):
        return buf.split(chr(0xAA))[1:-1]
    
    # Format 1 byte as String
    def format_byte(self, byte):
        return hex(ord(byte))[0:2] + '0' + hex(ord(byte))[2:] if len(hex(ord(byte))) < 4 else hex(ord(byte))
    
    # Extract protocol Version from msg
    def get_protocolversion(self, msg):
        if hex(ord(msg[4])) == '0x10': return "PV1"
        if hex(ord(msg[4])) == '0x20': return "PV2"
        if hex(ord(msg[4])) == '0x30': return "PV3"
        return "UNKNOWN"
    
    # Extract Destination from msg NOT USED AT THE MOMENT
    def get_destination(self, msg):
        return self.format_byte(msg[1]) + self.format_byte(msg[0])[2:]
    
    #Extract source from msg NOT USED AT THE MOMENT
    def get_source(self, msg):
        return self.format_byte(msg[3]) + self.format_byte(msg[2])[2:]
    
    # Extract command from msg NOT USED AT THE MOMENT
    def get_command(self, msg):
        return self.format_byte(msg[6]) + self.format_byte(msg[5:6])[2:]
    
    # Get count of frames in msg
    def get_frame_count(self, msg):
        return self.gb(msg, 7, 8)
    
    # Extract payload from msg
    def get_payload(self, msg):
        payload = ''
        for i in range(self.get_frame_count(msg)):
          payload += self.integrate_septett(msg[9+(i*6):15+(i*6)])
        return payload
    
    # parse payload and set item value
    def parse_payload(self, msg):
        command = self.get_command(msg)
        source = self.get_source(msg)
        destination = self.get_destination(msg)
        logger.debug("command: " + str(command))
        logger.debug("source: " + str(source))
        logger.debug("destination: " + str(destination))
        payload = self.get_payload(msg)
        for item in self._items:
            if 'resol_source' in item.return_parent().conf:
                if item.return_parent().conf['resol_source'] != self.get_source(msg):
                    logger.debug("source if item " + str(item) + " does not match msg source " + str(item.return_parent().conf['resol_source']) + " not matches msg source: " + str(self.get_source(msg)))
                    continue
            if 'resol_destination' in item.return_parent().conf:
                if item.return_parent().conf['resol_destination'] != self.get_destination(msg):
                    logger.debug("destination if item " + str(item) + " does not match msg destination " + str(item.return_parent().conf['resol_destination']) + " not matches msg destination: " + str(self.get_destination(msg)))
                    continue
            if 'resol_command' in item.return_parent().conf:
                if item.return_parent().conf['resol_command'] != self.get_command(msg):
                    logger.debug("destination if item " + str(item) + " does not match msg destination " + str(item.return_parent().conf['resol_command']) + " not matches msg destination: " + str(self.get_command(msg)))
                    continue
            end = int(item.conf['resol_offset']) + (int(item.conf['resol_bituse']) + 1) / 8
            #logger.debug("Start: " + str(item.conf['resol_offset']) + " ENDE: " + str(end))
            wert = self.gb(payload, int(item.conf['resol_offset']), int(end)) * float(item.conf['resol_factor'] if 'resol_factor' in item.conf else 1)
            #logger.warning("payload: of item " + str(item) + ": " + str(wert))
            self._sh.return_item(str(item))(wert,'resolplugin','mysource','mydest')

    def integrate_septett(self, frame):
        data = ''
        septet = ord(frame[4])
    
        for j in range(4):
          if septet & (1 << j):
              data += chr(ord(frame[j]) | 0x80)
          else:
              data += frame[j]
    
        return data
    
    # Gets the numerical value of a set of bytes (respect Two's complement by value Range)
    def gb(self, data, begin, end):  # GetBytes
        wbg = sum([0xff << (i * 8) for i, b in enumerate(data[begin:end])])
        s = sum([ord(b) << (i * 8) for i, b in enumerate(data[begin:end])])
        
        
        if s >= wbg/2:
          s = -1 * (wbg - s)
        return s
