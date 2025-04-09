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

""" Definitions of tag evaluation classes """

import json

from .Element import Element
from .FElement import FElement
from .DataHolder import DataHolder


class EFile(FElement):

    """ file H5 element
    """

    def __init__(self, attrs, last, h5fileObject, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param h5fileObject: H5 file object
        :type h5fileObject: :class:`nxswriter.FileWriter.FTfile`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        FElement.__init__(self, "file", attrs, last, h5fileObject,
                          streams=streams)


class EDoc(Element):

    """ doc tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, "doc", attrs, last, streams=streams)

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if self._beforeLast():
            self._beforeLast().doc += "".join(xml[1])


class ESymbol(Element):

    """ symbol tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, "symbol", attrs, last, streams=streams)
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:    dictionary with symbols4
        self.symbols = {}

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting2
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if "name" in self._tagAttrs.keys():
            self.symbols[self._tagAttrs["name"]] = self.last.doc


class EDimensions(Element):

    """ dimensions tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, "dimensions", attrs, last, streams=streams)
        if "rank" in attrs.keys():
            self.last.setRank(attrs["rank"])


class ESelection(Element):

    """ selection tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, "selection", attrs, last, streams=streams)
        if "rank" in attrs.keys():
            self.last.setRank(attrs["rank"])


class EDim(Element):

    """ dim tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, "dim", attrs, last, streams=streams)
        if ("index" in attrs.keys()) and ("value" in attrs.keys()):
            self._beforeLast().setLength(attrs["index"], attrs["value"])
        #: (:obj:`str`) index attribute
        self.__index = None
        #: (:class:`nxswriter.DataSources.DataSource`) data source
        self.source = None
        #: (:obj:`list` <:obj:`str`>) tag content
        self.content = []
        if "index" in attrs.keys():
            self.__index = attrs["index"]

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if self.__index is not None and self.source:
            dt = self.source.getData()
            if dt and isinstance(dt, dict):
                dh = DataHolder(streams=self._streams, **dt)
                if dh:
                    self._beforeLast().setLength(self.__index,
                                                 str(dh.cast("string")))


class ESlab(Element):

    """ slab tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, "slab", attrs, last, streams=streams)
        if ("index" in attrs.keys()):
            offset = 0
            block = 1
            count = 1
            stride = 1
            if "offset" in attrs.keys() and attrs["offset"]:
                try:
                    offset = int(attrs["offset"])
                except Exception:
                    pass
            if "block" in attrs.keys() and attrs["block"]:
                try:
                    block = int(attrs["block"])
                except Exception:
                    pass
            if "count" in attrs.keys() and attrs["count"]:
                try:
                    count = int(attrs["count"])
                except Exception:
                    pass
            if "stride" in attrs.keys() and attrs["stride"]:
                try:
                    stride = int(attrs["stride"])
                except Exception:
                    pass
            self._beforeLast().setSelection(
                attrs["index"], [offset, block, count, stride])
        #: (:obj:`str`) index attribute
        self.__index = None
        #: (:class:`nxswriter.DataSources.DataSource`) data source
        self.source = None
        #: (:obj:`list` <:obj:`str`>) tag content
        self.content = []
        if "index" in attrs.keys():
            self.__index = attrs["index"]

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if self.__index is not None and self.source:
            dt = self.source.getData()
            if dt and isinstance(dt, dict):
                dh = DataHolder(streams=self._streams, **dt)
                if dh:
                    slab = json.loads(str(dh.cast("string")))
                    if isinstance(slab, list):
                        self._beforeLast().setSelection(self.__index, slab[:4])


class ESlice(Element):

    """ slice tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, "slice", attrs, last, streams=streams)
        if ("index" in attrs.keys()):
            added = False
            start = None
            stop = None
            step = None
            if "start" in attrs.keys() and attrs["start"]:
                try:
                    start = int(attrs["start"])
                    added = True
                except Exception:
                    pass
            if "stop" in attrs.keys() and attrs["stop"]:
                try:
                    stop = int(attrs["stop"])
                    added = True
                except Exception:
                    pass
            if "step" in attrs.keys() and attrs["step"]:
                try:
                    step = int(attrs["step"])
                    added = True
                except Exception:
                    pass
            if added:
                self._beforeLast().setSelection(
                    attrs["index"], slice(start, stop, step))
        #: (:obj:`str`) index attribute
        self.__index = None
        #: (:class:`nxswriter.DataSources.DataSource`) data source
        self.source = None
        #: (:obj:`list` <:obj:`str`>) tag content
        self.content = []
        if "index" in attrs.keys():
            self.__index = attrs["index"]

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if self.__index is not None and self.source:
            dt = self.source.getData()
            if dt and isinstance(dt, dict):
                dh = DataHolder(streams=self._streams, **dt)
                if dh:
                    lslice = json.loads(str(dh.cast("string")))
                    if isinstance(lslice, list):
                        self._beforeLast().setSelection(
                            self.__index, slice(*lslice))


class EFilter(Element):

    """ filter tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, "filter", attrs, last, streams=streams)
        index = 0
        try:
            if ("index" in attrs.keys()):
                index = int(attrs["index"])
        except Exception:
            pass
        try:
            filter_id = int(attrs["id"])
        except Exception:
            filter_id = 0
        try:
            name = attrs["name"]
        except Exception:
            name = ""
        try:
            cd_values = attrs["cd_values"]
        except Exception:
            cd_values = ""
        try:
            availability = attrs["availability"]
        except Exception:
            availability = ""

        if filter_id or name:
            self._beforeLast().filters[index] = (
                filter_id, name, cd_values, availability)
        #: (:obj:`int`) index attribute
        self.__index = index
