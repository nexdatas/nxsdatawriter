#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
# \package test nexdatas
# \file ServerSetUp.py
# class with server settings
#
import os
import sys
import subprocess

import time

try:
    import tango
except Exception:
    import PyTango as tango


try:
    import SimpleServer
except Exception:
    from . import SimpleServer


# test fixture
class SimpleServerSetUp(object):

    # constructor
    # \brief defines server parameters

    def __init__(self, device="stestp09/testss/s1r228", instance="S1"):
        # information about tango writer
        self.new_device_info_writer = tango.DbDevInfo()
        # information about tango writer class
        self.new_device_info_writer._class = "SimpleServer"
        # information about tango writer server
        self.new_device_info_writer.server = "SimpleServer/%s" % instance
        # information about tango writer name
        self.new_device_info_writer.name = device

        # server instance
        self.instance = instance
        self._psub = None
        # device proxy
        self.dp = None
        # device properties
        self.device_prop = {
            'DeviceBoolean': False,
            'DeviceShort': 12,
            'DeviceLong': 1234566,
            'DeviceFloat': 12.4345,
            'DeviceDouble': 3.453456,
            'DeviceUShort': 1,
            'DeviceULong': 23234,
            'DeviceString': "My Sting"
        }

        # class properties
        self.class_prop = {
            'ClassBoolean': True,
            'ClassShort': 1,
            'ClassLong': -123555,
            'ClassFloat': 12.345,
            'ClassDouble': 1.23445,
            'ClassUShort': 1,
            'ClassULong': 12343,
            'ClassString': "My ClassString",
        }

    # test starter
    # \brief Common set up of Tango Server
    def setUp(self):
        print("\nsetting up...")
        db = tango.Database()
        db.add_device(self.new_device_info_writer)
        db.add_server(
            self.new_device_info_writer.server, self.new_device_info_writer)
        db.put_device_property(
            self.new_device_info_writer.name, self.device_prop)
        db.put_class_property(
            self.new_device_info_writer._class, self.class_prop)

        path = os.path.dirname(os.path.abspath(SimpleServer.__file__))
        if os.path.isfile("%s/SimpleServer.py" % path):
            if sys.version_info > (3,):
                self._psub = subprocess.call(
                    "cd %s; python3 ./SimpleServer.py %s &" %
                    (path, self.instance), stdout=None,
                    stderr=None, shell=True)
            else:
                self._psub = subprocess.call(
                    "cd %s; python ./SimpleServer.py %s &" %
                    (path, self.instance), stdout=None,
                    stderr=None, shell=True)
            sys.stdout.write("waiting for simple server ")

        found = False
        cnt = 0
        dvname = self.new_device_info_writer.name
        while not found and cnt < 1000:
            try:
                sys.stdout.write(".")
                sys.stdout.flush()
                exl = db.get_device_exported(dvname)
                if dvname not in exl.value_string:
                    time.sleep(0.01)
                    cnt += 1
                    continue
                self.dp = tango.DeviceProxy(dvname)
                time.sleep(0.01)
                if self.dp.state() == tango.DevState.ON:
                    found = True
            except Exception:
                found = False
            cnt += 1
        print("")

    # test closer
    # \brief Common tear down oif Tango Server
    def tearDown(self):
        print("tearing down ...")
        db = tango.Database()
        db.delete_server(self.new_device_info_writer.server)
        if sys.version_info > (3,):
            with subprocess.Popen(
                    "ps -ef | grep 'SimpleServer.py %s' | grep -v grep" %
                    self.instance,
                    stdout=subprocess.PIPE, shell=True) as proc:

                pipe = proc.stdout
                res = str(pipe.read(), "utf-8").split("\n")
                for r in res:
                    sr = r.split()
                    if len(sr) > 2:
                        subprocess.call(
                            "kill -9 %s" % sr[1], stderr=subprocess.PIPE,
                            shell=True)
                pipe.close()
        else:
            pipe = subprocess.Popen(
                "ps -ef | grep 'SimpleServer.py %s' | grep -v grep" %
                self.instance,
                stdout=subprocess.PIPE, shell=True).stdout

            res = str(pipe.read()).split("\n")
            for r in res:
                sr = r.split()
                if len(sr) > 2:
                    subprocess.call(
                        "kill -9 %s" % sr[1], stderr=subprocess.PIPE,
                        shell=True)
            pipe.close()


if __name__ == "__main__":
    simps = SimpleServerSetUp()
    simps.setUp()
    print(simps.dp.status())
    simps.tearDown()
