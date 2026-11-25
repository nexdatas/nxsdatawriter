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
#

""" Definitions of PYEVAL datasource """

import threading
import copy
import xml.etree.ElementTree as et
from lxml.etree import XMLParser

from .Types import NTP

from .DataHolder import DataHolder
from .DataSources import DataSource
from .Errors import DataSourceSetupError


class Variables(object):

    """ Variables for PyEval datasource
    """


class PyEvalSource(DataSource):

    """ Python Eval data source
    """

    def __init__(self, streams=None, name=None):
        """ constructor

        :brief: It cleans all member variables
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param name: datasource name
        :type name: :obj:`str`
        """
        DataSource.__init__(self, streams=streams, name=name)
        #: (:obj:`str`) name of data
        self.__name = None
        #: (:obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>) \
        #:     the current  static JSON object
        self.__globalJSON = None
        #: (:obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>) \
        #:     the current  dynamic JSON object
        self.__localJSON = None
        #: (:class:`nxswriter.DataSourcePool.DataSourcePool`) datasource pool
        self.__pool = None
        #: (:obj:`dict` <:obj:`str`, (:obj:`str`,:obj:`str`) > ) \
        #:     datasources dictionary with {dsname: (dstype, dsxml)}
        self.__sources = {}
        #: (:obj:`dict` \
        #:     <:obj:`str`, (:class:`nxswriter.DataSources.DataSource`) > ) \
        #:  datasource dictionary {name: DataSource}
        self.__datasources = {}
        #: (:obj:`str`) python script
        self.__script = ""
        #: (:obj:`bool`) True if common block used
        self.__commonblock = False
        #: (:obj:`bool`) True if counter used
        self.__counter = False
        #: (:class:`threading.Lock`) lock for common block
        self.__lock = None
        #: (:obj:`dict` <:obj:`str`, any> ) \
        #:    common block variables
        self.__common = None
        #: ({"rank": :obj:`str`, "value": any, "tangoDType": :obj:`str`, \
        #:   "shape": :obj:`list`<int>, "encoding": :obj:`str`, \
        #:   "decoders": :obj:`str`} ) \
        #:    data format
        self.__result = {"rank": "SCALAR",
                         "value": None,
                         "tangoDType": "DevString",
                         "shape": [1, 0],
                         "encoding": None,
                         "decoders": None}

    def setup(self, xml):
        """ sets the parrameters up from xml

        :param xml:  datasource parameters
        :type xml: :obj:`str`
        """

        xml = bytes(xml, "UTF-8")
        root = et.fromstring(xml, parser=XMLParser(collect_ids=False))
        mds = root.find("datasource")
        inputs = []
        if mds is not None:
            inputs = root.findall(".//datasource")
            for inp in inputs:
                if "name" in inp.attrib and "type" in inp.attrib:
                    name = inp.get("name")
                    dstype = inp.get("type")
                    if len(name) > 0:
                        if len(name) > 3 and name[:2] == 'ds.':
                            name = name[3:]
                        self.__sources[name] = (dstype, self._toxml(inp))
                    else:
                        if self._streams:
                            self._streams.error(
                                "PyEvalSource::setup() - "
                                "PyEval input %s not defined" % name,
                                std=False)

                        raise DataSourceSetupError(
                            "PyEvalSource::setup() - "
                            "PyEval input %s not defined" % name)

                else:
                    if self._streams:
                        self._streams.error(
                            "PyEvalSource::setup() - "
                            "PyEval input name wrongly defined",
                            std=False)

                    raise DataSourceSetupError(
                        "PyEvalSource::setup() - "
                        "PyEval input name wrongly defined")
        res = root.find("result")
        if res is not None:
            self.__name = res.get("name") or 'result'
            if len(self.__name) > 3 and self.__name[:2] == 'ds.':
                self.__name = self.__name[3:]
            self.__script = self._getText(res)

        if len(self.__script) == 0:
            if self._streams:
                self._streams.error(
                    "PyEvalSource::setup() - "
                    "PyEval script %s not defined" % self.__name,
                    std=False)

            raise DataSourceSetupError(
                "PyEvalSource::setup() - "
                "PyEval script %s not defined" % self.__name)

        if "commonblock" in self.__script:
            self.__commonblock = True
        else:
            self.__commonblock = False

    def __str__(self):
        """ self-description

        :returns: self-describing string
        :rtype: :obj:`str`
        """
        return " PYEVAL %s" % (self.__script)

    def setJSON(self, globalJSON, localJSON=None):
        """ sets JSON string

        :brief: It sets the currently used  JSON string
        :param globalJSON: static JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>
        :param localJSON: dynamic JSON string
        :type localJSON: \
        :     :obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>
        """
        self.__globalJSON = globalJSON
        self.__localJSON = localJSON
        for source in self.__datasources.values():
            if hasattr(source, "setJSON"):
                source.setJSON(self.__globalJSON,
                               self.__localJSON)

    def getData(self):
        """ provides access to the data

        :returns:  dictionary with collected data
        :rtype: {'rank': :obj:`str`, 'value': any, 'tangoDType': :obj:`str`, \
        :        'shape': :obj:`list` <int>, 'encoding': :obj:`str`, \
        :        'decoders': :obj:`str`} )
        """
        if not self.__name:
            if self._streams:
                self._streams.error(
                    "PyEvalSource::getData() - PyEval datasource not set up",
                    std=False)

            raise DataSourceSetupError(
                "PyEvalSource::getData() - PyEval datasource not set up")

        if self.__commonblock:
            self.__pool.common['PYEVAL']["common"]["__counter__"] = \
                self.__pool.counter
        ds = Variables()
        for name, source in self.__datasources.items():
            if name in self.__script:
                dt = source.getData()
                value = None
                if dt:
                    dh = DataHolder(streams=self._streams, **dt)
                    if dh and hasattr(dh, "value"):
                        value = dh.value
                setattr(ds, name, value)

        setattr(ds, self.__name, None)

        if not self.__commonblock:
            exec(self.__script.strip(), {}, {"ds": ds})
            rec = getattr(ds, self.__name)
        else:
            rec = None
            with self.__lock:
                exec(self.__script.strip(), {}, {
                    "ds": ds, "commonblock": self.__common})
                rec = copy.deepcopy(getattr(ds, self.__name))
        ntp = NTP()
        rank, shape, dtype = ntp.arrayRankShape(rec)
        if rank in NTP.rTf:
            if shape is None:
                shape = [1, 0]

            return {"rank": NTP.rTf[rank],
                    "value": rec,
                    "tangoDType": NTP.pTt[dtype],
                    "shape": shape}

    def setDecoders(self, decoders):
        """ sets the used decoders

        :param decoders: pool to be set
        :type decoders: :class:`nxswriter.DecoderPool.DecoderPool`
        """
        self.__result["decoders"] = decoders
        for source in self.__datasources.values():
            if hasattr(source, "setDecoders"):
                source.setDecoders(decoders)

    def setDataSources(self, pool):
        """ sets the datasources

        :param pool: datasource pool
        :type pool: :class:`nxswriter.DataSourcePool.DataSourcePool`
        """
        self.__pool = pool
        pool.lock.acquire()
        try:
            if 'PYEVAL' not in self.__pool.common.keys():
                self.__pool.common['PYEVAL'] = {}
            if "lock" not in self.__pool.common['PYEVAL'].keys():
                self.__pool.common['PYEVAL']["lock"] = threading.Lock()
            self.__lock = self.__pool.common['PYEVAL']["lock"]
            if "common" not in self.__pool.common['PYEVAL'].keys():
                self.__pool.common['PYEVAL']["common"] = {}
                if self.__pool.nxroot is not None:
                    self.__pool.common['PYEVAL']["common"]["__nxroot__"] = \
                        self.__pool.nxroot.h5object
                    self.__pool.common['PYEVAL']["common"]["__root__"] = \
                        self.__pool.nxroot
                    self.__pool.common['PYEVAL']["common"]["__counter__"] = \
                        self.__pool.counter
            self.__common = self.__pool.common['PYEVAL']["common"]

        finally:
            pool.lock.release()

        for name, inp in self.__sources.items():
            if name in self.__script:
                if pool and pool.hasDataSource(inp[0]):
                    self.__datasources[name] = pool.get(inp[0])()
                    self.__datasources[name].setup(inp[1])
                    if hasattr(self.__datasources[name], "setJSON") \
                            and self.__globalJSON:
                        self.__datasources[name].setJSON(self.__globalJSON)
                    if hasattr(self.__datasources[name], "setDataSources"):
                        self.__datasources[name].setDataSources(pool)

                else:
                    if self._streams:
                        self._streams.error(
                            "PyEvalSource::setDataSources "
                            "- Unknown data source")
                        self.__datasources[name] = DataSource()
