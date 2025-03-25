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

""" Definitions of field tag evaluation classes """

import sys

# import numpy
import json

from .DataHolder import DataHolder
from .Element import Element
from .FElement import FElementWithAttr
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)

from nxstools import filewriter as FileWriter


class EVirtualPart(Element):

    """ layout map tag element
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
        Element.__init__(self, "part", attrs, last, streams=streams)
        #: (:obj:`str`) rank of the field
        self.rank = "0"
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:        shape of the field, i.e. {index: length}
        self.lengths = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:        selection of the field, i.e. {index: slice or hyperslab}
        self.selection = {}
        #: (:obj:`list` <:obj:`str`>) tag content
        self.content = []
        # (:obj:`int`) part index counting from 1
        self.__index = 0

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        part = {}

        part["shape"] = self.__getShape()
        part["key"] = self.__getKey()
        target = None
        filename = None
        fieldpath = None
        if "target" in self._tagAttrs.keys():
            if sys.version_info > (3,):
                target = self._tagAttrs["target"]
            else:
                target = self._tagAttrs["target"].encode()
            if target:
                part["target"] = target
        if "filename" in self._tagAttrs.keys():
            if sys.version_info > (3,):
                filename = self._tagAttrs["filename"]
            else:
                filename = self._tagAttrs["filename"].encode()
            if filename:
                part["filename"] = filename
        if "fieldpath" in self._tagAttrs.keys():
            if sys.version_info > (3,):
                fieldpath = self._tagAttrs["fieldpath"]
            else:
                fieldpath = self._tagAttrs["fieldpath"].encode()
            if fieldpath:
                part["fieldpath"] = fieldpath
        self.__index = self.last.appendPart(part)

    def __getShape(self):
        """ provides shape

        :returns: object shape
        :rtype: :obj:`list` <:obj:`int` >
        """
        shape = []
        try:
            if int(self.rank) > 0:
                for i in range(int(self.rank)):
                    si = str(i + 1)
                    if self.lengths and si in self.lengths.keys() \
                       and self.lengths[si] is not None:
                        if int(self.lengths[si]) > 0:
                            shape.append(int(self.lengths[si]))
                    else:
                        raise XMLSettingSyntaxError(
                            "Dimensions not defined")
                if len(shape) < int(self.rank):
                    raise XMLSettingSyntaxError(
                        "Too small dimension number")
        except XMLSettingSyntaxError:
            if self.rank and int(self.rank) >= 0:
                shape = [0] * (int(self.rank))
            else:
                shape = [0]
        return shape

    def __getKey(self):
        """ provides key

        :returns: object key
        :rtype: :obj:`list` <:obj:`int` >
        """
        key = []
        try:
            if int(self.rank) > 0:
                for i in range(int(self.rank)):
                    si = str(i + 1)
                    if self.selection and si in self.selection.keys() \
                       and self.selection[si] is not None:
                        key.append(self.selection[si])
                    else:
                        key.append(None)
        except XMLSettingSyntaxError:
            pass
        return key


class EVirtualLayout(Element):

    """ layout map tag element
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
        Element.__init__(self, "map", attrs, last, streams=streams)
        #: (:class:`nxswriter.DataSources.DataSource`) data source
        self.source = None
        #: (:obj:`list` <:obj:`str`>) tag content
        self.content = []
        #: (:obj:`str`) strategy, i.e. INIT, STEP, FINAL
        self.strategy = 'STEP'
        #: (:obj:`str`) trigger for asynchronous writting
        self.trigger = None
        self.error = ""

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """

    def run(self):
        """ runner

        :brief: During its thread run it fetches the data from the source
        """
        try:
            if self.source:
                dt = self.source.getData()
                if dt and isinstance(dt, dict):
                    dh = DataHolder(streams=self._streams, **dt)
                    val = dh.cast("string")
                    self.last.appendPart(val)

        except Exception:
            info = sys.exc_info()
            import traceback
            message = self.setMessage(
                str(info[1].__str__()) + "\n " + (" ").join(
                    traceback.format_tb(sys.exc_info()[2])))
            # message = self.setMessage(  sys.exc_info()[1].__str__()  )
            del info
            #: notification of error in the run method (defined in base class)
            self.error = message
            # self.error = sys.exc_info()
        finally:
            if self.error:
                if self._streams:
                    if self.canfail:
                        self._streams.warn(
                            "EField::run() - %s  " % str(self.error))
                    else:
                        self._streams.error(
                            "EField::run() - %s  " % str(self.error))


class EVirtualField(FElementWithAttr):

    """ virtual field H5 tag element
    """

    def __init__(self, attrs, last, streams=None,
                 reloadmode=False):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param reloadmode: reload mode
        :type reloadmode: :obj:`bool`
        """
        FElementWithAttr.__init__(self, "field", attrs, last, streams=streams,
                                  reloadmode=reloadmode)
        #: (:obj:`str`) rank of the field
        self.rank = "0"
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:        shape of the field, i.e. {index: length}
        self.lengths = {}
        #: (:obj:`str`) strategy, i.e. INIT, STEP, FINAL, POSTRUN
        self.strategy = 'FINAL'
        #: (:obj:`str`) trigger for asynchronous writing
        self.trigger = None
        self.__dtype = ""
        self.__name = ""
        self.__shape = []
        #: (:obj:`list`) part list
        self.parts = []

    def __typeAndName(self):
        """ provides type and name of the field

        :returns: (type, name) tuple
        """
        if "name" in self._tagAttrs.keys():
            nm = self._tagAttrs["name"]
            if "type" in self._tagAttrs.keys():
                tp = NTP.nTnp[self._tagAttrs["type"]]
            else:
                tp = "string"
            return tp, nm
        else:
            if self._streams:
                self._streams.error(
                    "FElement::__typeAndName() - Field without a name",
                    std=False)

            raise XMLSettingSyntaxError("Field without a name")

    def __getShape(self):
        """ provides shape

        :returns: object shape
        :rtype: :obj:`list` <:obj:`int` >
        """
        try:
            shape = self._findShape(
                self.rank, self.lengths,
                False, 0, True, checkData=True)
            return shape
        except XMLSettingSyntaxError:
            if self.rank and int(self.rank) >= 0:
                shape = [0] * (int(self.rank))
            else:
                shape = [0]
            return shape

    def __setAttributes(self):
        """ creates attributes

        :brief: It creates attributes in h5Object
        """
        self._setAttributes(["name"])
        self._createAttributes()

        if self.strategy == "POSTRUN":
            if sys.version_info > (3,):
                self.h5Object.attributes.create(
                    "postrun",
                    "string", overwrite=True)[...] \
                    = self.postrun.strip()
            else:
                self.h5Object.attributes.create(
                    "postrun".encode(),
                    "string".encode(), overwrite=True)[...] \
                    = self.postrun.encode().strip()

    def __setStrategy(self, name):
        """ provides strategy or fill the value in

        :param name: object name
        :returns: strategy or strategy,trigger it trigger defined
        """
        if self.source:
            if self.source.isValid():
                return self.strategy, self.trigger
        if sys.version_info > (3,):
            val = ("".join(self.content)).strip()
        else:
            val = ("".join(self.content)).strip().encode()
        if val:
            lval = val.split("\n")
            for el in lval:
                if el.strip():
                    self.parts.append({"target": el.strip()})
        return self.strategy, self.trigger

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj:`str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        :returns: (strategy, trigger)
        :rtype: (:obj:`str`, :obj:`str`)
        """

        # type and name
        self.__dtype, self.__name = self.__typeAndName()
        # shape
        self.__shape = self.__getShape()
        #: stored H5 file object (defined in base class)
        # self.h5Object = self.__createObject(
        # self.__dtype, self.__name, self.__shape)
        # create attributes
        # self.__setAttributes()

        # return strategy or fill the value in
        return self.__setStrategy(self.__name)

    def __cureKeys(self, key):
        tkey = []
        if isinstance(key, list):
            sk = list(set([len(ky) for ky in key]))
            if len(sk) == 1 and sk[0] == 4:
                offset = []
                block = []
                count = []
                stride = []
                for ky in key:
                    off, bl, cnt, std = ky
                    offset.append(off)
                    block.append(bl)
                    count.append(cnt)
                    stride.append(str)
                return FileWriter.FTHyperslab(offset, block, count, stride)
            for ky in key:
                if isinstance(ky, list) and len(ky) > 0 and len(ky) < 4:
                    tkey.append(slice(*ky))
                else:
                    tkey.append(ky)
            return tkey
        return key

    def appendPart(self, values):
        try:
            if isinstance(values, str):
                values = json.loads(values)
            if not isinstance(values, list):
                values = [values]
        except Exception:
            if hasattr(values, "flatten"):
                values = values.flatten()
            if isinstance(values, str):
                values = [values]
            val = values
            values = []
            for vl in val:
                try:
                    if isinstance(vl, str):
                        vl = json.loads(vl)
                    values.append(vl)
                except Exception:
                    values.append(str(vl).strip())
        for vl in values:
            if isinstance(vl, dict):
                self.parts.append(dict(vl))
            else:
                self.parts.append({"target": vl.strip()})
        return len(self.parts)

    def __createVDS(self):
        vlf = FileWriter.virtual_field_layout(
            self.__shape, self.__dtype)
        counter = 0
        for part in self.parts:
            fieldpath = ""
            filename = ""
            edtype = part["dtype"] \
                if "dtype" in part else self.__dtype
            eshape = part["shape"] \
                if "shape" in part else [1, *self.__shape[1:]]
            fieldpath = part["fieldpath"] \
                if "fieldpath" in part else "/data"
            filename = part["filename"] if "filename" in part else None
            if "target" in part:
                target = part["target"]
                if target.startswith("h5file:/"):
                    target = target[8:]
                if ":/" in target:
                    filename, fieldpath = target.split(":/")
                elif "::" in target:
                    filename, fieldpath = target.split("::")
                else:
                    fieldpath = target

            ef = FileWriter.target_field_view(
                filename, fieldpath, eshape, edtype)
            sourceshape = part["sourceshape"] \
                if "sourceshape" in part else None
            sourcekey = part["sourcekey"] \
                if "sourcekey" in part else None
            key = part["key"] if "key" in part else counter
            key = self.__cureKeys(key)
            sourcekey = self.__cureKeys(sourcekey)
            if eshape:
                counter += eshape[0]
            else:
                counter += 1
            vlf.add(key, ef, sourcekey, sourceshape)
        self.h5Object = self._lastObject().create_virtual_field(
            self.__name, vlf)

    def run(self):
        """ runner

        :brief: During its thread run it fetches the data from the source
        """
        try:
            if self.source:
                dt = self.source.getData()
                if dt and isinstance(dt, dict):
                    dh = DataHolder(streams=self._streams, **dt)
                    val = dh.cast("string")
                    self.appendPart(val)
            if self.parts and self.__shape and self.__dtype and self.__name:
                self.__createVDS()
                self.__setAttributes()
        except Exception:
            info = sys.exc_info()
            import traceback
            message = self.setMessage(
                str(info[1].__str__()) + "\n " + (" ").join(
                    traceback.format_tb(sys.exc_info()[2])))
            # message = self.setMessage(  sys.exc_info()[1].__str__()  )
            del info
            #: notification of error in the run method (defined in base class)
            self.error = message
            # self.error = sys.exc_info()
        finally:
            if self.error:
                if self._streams:
                    if self.canfail:
                        self._streams.warn(
                            "EField::run() - %s  " % str(self.error))
                    else:
                        self._streams.error(
                            "EField::run() - %s  " % str(self.error))
