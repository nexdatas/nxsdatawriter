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
# \file TstDataSource.py
# unittests for field Tags running Tango Server
#
import numpy

from nxswriter.Types import NTP
from nxswriter.DataSources import DataSource


# test datasource
class TstDataSource(DataSource):

    # constructor
    # \brief It cleans all member variables
    def __init__(self, streams=None):
        # flag for running getData
        self.dataTaken = False
        # list of dimensions
        self.dims = []
        # if numpy  datasource
        self.numpy = True
        # validity
        self.valid = True
        # returned Data
        self.value = None
        # datasource name
        self._name = None
        # the current  static JSON object
        self.globalJSON = None
        # the current  dynamic JSON object
        self.localJSON = None
        # xml
        self.xml = None
        # decoder pool
        self.decoders = None
        # datasource pool
        self.datasources = None
        # stack
        self.stack = []
        # value 0D
        self.value0d = 1
        # streams
        self._streams = streams

    # sets the parameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
        self.stack.append("setup")
        self.stack.append(xml)
        self.xml = None

    # access to data
    # \brief It is an abstract method providing data
    def getData(self):
        self.stack.append("getData")
        if self.valid:
            self.dataTaken = True
            if self.value:
                return self.value
            elif len(self.dims) == 0:
                return {"rank": NTP.rTf[0], "value": self.value0d,
                        "tangoDType": "DevLong", "shape": [0, 0]}
            elif numpy:
                return {
                    "rank": NTP.rTf[len(self.dims)],
                    "value": numpy.ones(self.dims),
                    "tangoDType": "DevLong", "shape": self.dims}
            elif len(self.dims) == 1:
                return {"rank": NTP.rTf[1], "value": ([1] * self.dims[0]),
                        "tangoDType": "DevLong", "shape": [self.dims[0], 0]}
            elif len(self.dims) == 2:
                return {
                    "rank": NTP.rTf[2],
                    "value": ([[1] * self.dims[1]] * self.dims[0]),
                    "tangoDType": "DevLong", "shape": [self.dims[0], 0]}

    # checks if the data is valid
    # \returns if the data is valid
    def isValid(self):
        self.stack.append("isValid")
        return self.valid

    # self-description
    # \returns self-describing string
    def __str__(self):
        self.stack.append("__str__")
        return "Test DataSource"

    # sets JSON string
    # \brief It sets the currently used  JSON string
    # \param globalJSON static JSON string
    # \param localJSON dynamic JSON string
    def setJSON(self, globalJSON, localJSON=None):
        self.stack.append("setJSON")
        self.stack.append(globalJSON)
        self.stack.append(localJSON)
        self.globalJSON = globalJSON
        self.localJSON = localJSON

    # sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self.stack.append("setDecoders")
        self.stack.append(decoders)
        self.decoders = decoders

    # sets the datasources
    # \param pool datasource pool
    def setDataSources(self, pool):
        self.stack.append("setDataSources")
        self.stack.append(pool)
        self.datasources = pool
