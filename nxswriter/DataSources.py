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

""" Definitions of various datasources """

from .Types import NTP
import xml.etree.ElementTree as et
import sys


def _tostr(text):
    """ converts text  to str type

    :param text: text
    :type text: :obj:`bytes` or :obj:`unicode`
    :returns: text in str type
    :rtype: :obj:`str`
    """
    if isinstance(text, str):
        return text
    elif sys.version_info > (3,):
        return str(text, encoding="utf-8")
    else:
        return str(text)


class DataSource(object):

    """ Data source
    """

    def __init__(self, streams=None, name=None):
        """ constructor

        :brief: It cleans all member variables
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param name: datasource name
        :type name: :obj:`str`
        """
        #: (:class:`StreamSet` or :class:`tango.LatestDeviceImpl`) stream set
        self._streams = streams
        #: (:obj:`str`) datasoure name
        self._name = name

    def setup(self, xml):
        """ sets the parrameters up from xml

        :param xml:  datasource parameters
        :type xml: :obj:`str`
        """
        pass

    def getData(self):
        """ access to data

        :brief: It is an abstract method providing data
        """
        pass

    def isValid(self):
        """ checks if the data is valid

        :returns: True if the data is valid
        :rtype: :obj:`bool`
        """
        return True

    def __str__(self):
        """ self-description

        :returns: self-describing string
        :rtype: :obj:`str`
        """
        return "unknown DataSource"

    @classmethod
    def _toxml(cls, node):
        """ provides xml content of the whole node

        :param node: DOM node
        :type node: :class:`xml.dom.Node`
        :returns: xml content string
        :rtype: :obj:`str`
        """
        if sys.version_info > (3,):
            xml = _tostr(et.tostring(node, encoding='unicode', method='xml'))
        else:
            xml = _tostr(et.tostring(node, encoding='utf8', method='xml'))
        if xml.startswith("<?xml version='1.0' encoding='utf-8'?>"):
            xml = str(xml[39:])
        elif xml.startswith("<?xml version='1.0' encoding='utf8'?>"):
            xml = str(xml[38:])
        return xml

    @classmethod
    def _getText(cls, node):
        """ provides xml content of the node

        :param node: DOM node
        :type node: :class:`xml.dom.Node`
        :returns: xml content string
        :rtype: :obj:`str`
        """
        xml = cls._toxml(node)
        start = xml.find('>')
        end = xml.rfind('<')
        if start == -1 or end < start:
            return ""
        return xml[start + 1:end].replace("&lt;", "<").\
            replace("&gt;", ">").replace("&quot;", "\"").\
            replace("&amp;", "&")

    @classmethod
    def _getJSONData(cls, names, globalJSON, localJSON):
        """ provides access to the data

        :param names: data key names
        :type names: :obj:`list` < :obj:`str` > or :obj:`str`
        :param globalJSON: static JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>
        :param localJSON: dynamic JSON string
        :type localJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        :returns: dictionary with collected data
        :rtype: :obj:`dict` <:obj:`str`, any>
        """
        # backports for the older version
        names = names or []
        if not isinstance(names, list):
            names = [names]

        if globalJSON and 'data' not in globalJSON.keys():
            globalJSON = None

        if localJSON and 'data' not in localJSON.keys():
            localJSON = None

        rec = None
        for name in names:
            if localJSON and 'data' in localJSON \
                    and name in localJSON['data']:
                rec = localJSON['data'][str(name)]
            elif globalJSON and 'data' in globalJSON \
                    and name in globalJSON['data']:
                rec = globalJSON['data'][str(name)]
            if rec is not None:
                break
        if rec is None:
            return
        ntp = NTP()
        rank, shape, dtype = ntp.arrayRankShape(rec)

        if rank in NTP.rTf:
            if shape is None:
                shape = [1, 0]
            return {"rank": NTP.rTf[rank],
                    "tangoDType": NTP.pTt[dtype],
                    "value": rec,
                    "shape": shape}
