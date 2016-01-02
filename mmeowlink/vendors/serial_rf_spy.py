#!/usr/bin/env python

################################################################################
# This is based on https://github.com/ps2/subg_rfspy with minor adjustments
#
# Copyright (c) 2015 Pete Schwamb
# The MIT License (MIT)
#
# Copyright (c) 2015 Pete Schwamb
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################


import os
import serial
import time
from .. exceptions import CommsException

class SerialRfSpy:
  CMD_GET_STATE = 1
  CMD_GET_VERSION = 2
  CMD_GET_PACKET = 3
  CMD_SEND_PACKET = 4
  CMD_SEND_AND_LISTEN = 5

  def __init__(self, ser):
    self.default_write_timeout = 1
    self.ser = ser
    self.buf = bytearray()

  def do_command(self, command, param="", timeout=0):
    self.send_command(command, param)
    return self.get_response(timeout=timeout)

  def send_command(self, command, param="", timeout=1):
    self.ser.write_timeout = timeout

    self.ser.write(chr(command))
    if len(param) > 0:
      self.ser.write(param)

    self.ser.write_timeout = self.default_write_timeout

  def get_response(self, timeout=0):
    start = time.time()
    while 1:
      bytesToRead = self.ser.inWaiting()
      if bytesToRead > 0:
        self.buf.extend(self.ser.read(bytesToRead))
      eop = self.buf.find(b'\x00',0)
      if eop >= 0:
        r = self.buf[:eop]
        del self.buf[:(eop+1)]
        return r
      if (timeout > 0) and (start + timeout < time.time()):
        return bytearray()
      time.sleep(0.005)

  def sync(self):
    self.send_command(self.CMD_GET_STATE)
    status = self.get_response(timeout=1)
    if status == "OK":
      print "subg_rfspy status: " + status

    self.send_command(self.CMD_GET_VERSION)
    version = self.get_response(timeout=1)
    if len(version) >= 3:
      print "Version: " + version

    if not status or not version:
      raise CommsException("Could not get subg_rfspy state or version. Have you got the right port/device and radio_type?")
