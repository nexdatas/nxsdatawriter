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

""" Definitions of CLIENT datasource """

import sys
import xml.etree.ElementTree as et
from lxml.etree import XMLParser
from .DataSources import DataSource
from .Errors import DataSourceSetupError

try:
    try:
        import tango
    except Exception:
        import PyTango as tango
    #: (:obj:`str`) global variable if tango module installed
    PYTANGO_AVAILABLE = True
except ImportError as e:
    PYTANGO_AVAILABLE = False
    sys.stdout.write("PYTANGO not available: %s" % e)
    sys.stdout.flush()


class ClientSource(DataSource):

    """ Client data source
    """

    def __init__(self, streams=None, name=None):
        """ constructor

        :brief: It sets all member variables to None
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param name: datasource name
        :type name: :obj:`str`
        """
        DataSource.__init__(self, streams=streams, name=name)
        #: (:obj:`str`) data name
        self.name = None
        #: (:obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>)
        #: the current static JSON object
        self.__globalJSON = None
        #: (:obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>)
        #: the current dynamic JSON object
        self.__localJSON = None

    def setup(self, xml):
        """ sets the parrameters up from xml

        :param xml: datasource parameters
        :type xml: :obj:`str`
        :raises: :exc:`nxswriter.Errors.DataSourceSetupError` \
        :        if :obj:`name` is not defined
        """
        if sys.version_info > (3,):
            xml = bytes(xml, "UTF-8")
        root = et.fromstring(xml, parser=XMLParser(collect_ids=False))
        rec = root.find("record")
        if rec is not None:
            self.name = rec.get("name")
        if not self.name:
            if self._streams:
                self._streams.error(
                    "ClientSource::setup() - "
                    "Client record name not defined: %s" % xml,
                    std=False)
            raise DataSourceSetupError(
                "Client record name not defined: %s" % xml)

    def __str__(self):
        """ self-description

        :returns: self-describing string
        :rtype: :obj:`str`
        """
        return " CLIENT record %s" % (self.name)

    def setJSON(self, globalJSON, localJSON=None):
        """ sets JSON string

        :brief: It sets the currently used  JSON string
        :param globalJSON: static JSON string
        :type globalJSON: :obj:`dict` \
        :                 <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        :param localJSON: dynamic JSON string
        :type localJSON: :obj:`dict` \
                         <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        self.__globalJSON = globalJSON
        self.__localJSON = localJSON

    def getData(self):
        """ provides access to the data

        :returns: dictionary with collected data
        :rtype: {'rank': :obj:`str`, 'value': any, 'tangoDType': :obj:`str`, \
        :        'shape': :obj:`list` <int>, 'encoding': :obj:`str`, \
        :        'decoders': :obj:`str`} )
        """
        names = [self.name]
        if self.name:
            names.append(self.name.lower())
            if PYTANGO_AVAILABLE and "/" in self.name and \
               not self.name.startswith("tango://"):
                if ":" in self.name:
                    names.append("tango://%s" % (self.name.lower()))
                else:
                    db = tango.Database()
                    names.append("tango://%s:%s/%s" %
                                 (db.get_db_host().split(".")[0],
                                  db.get_db_port(), self.name.lower()))
        return self._getJSONData(names, self.__globalJSON, self.__localJSON)
