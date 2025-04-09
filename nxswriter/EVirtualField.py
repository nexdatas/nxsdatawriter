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


class EVirtualSourceView(Element):

    """ virtual source view tag element
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
        Element.__init__(self, "sourceview", attrs, last, streams=streams)
        #: (:obj:`list` <:obj:`str`>) tag content
        self.content = []

    def setRank(self, rank):
        """ sets dimension rank

        :param index: dimension rank
        :type index: :obj:`src`
        """
        self.last.setSourceRank(rank)

    def setLength(self, index, value):
        """ sets lengths dict element

        :param index: length index
        :type index: :obj:`int`
        :param value: length value
        :type value: :obj:`int` or :obj:`str`
        """
        self.last.setSourceLength(index, value)

    def setSelection(self, index, value):
        """ sets selection dict element

        :param index: selection index
        :type index: :obj:`int`
        :param value: selection value
        :type value: :obj:`int` or :obj:`str`
        """
        self.last.setSourceSelection(index, value)


class EVirtualDataMap(Element):

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
        #: (:obj:`str`) rank of the field
        self.rank = "0"
        #: (:obj:`str`) rank of the source field view
        self.srcrank = "0"
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:        shape of the field, i.e. {index: length}
        self.lengths = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:        selection of the field, i.e. {index: slice or hyperslab}
        self.selection = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:        shape of the source field, i.e. {index: length}
        self.srclengths = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:        source selection of the field,
        #:        i.e. {index: slice or hyperslab}
        self.srcselection = {}
        #: (:obj:`list` <:obj:`str`>) tag content
        self.content = []
        #: (:class:`nxswriter.DataSources.DataSource`) data source
        self.source = None
        #: (:obj:`str`) strategy, i.e. INIT, STEP, FINAL
        self.strategy = 'STEP'
        #: (:obj:`str`) trigger for asynchronous writting
        self.trigger = None
        self.error = ""
        # virtual layout map
        self.__vmap = {}

    def setLength(self, index, value):
        """ sets lengths dict element

        :param index: length index
        :type index: :obj:`int`
        :param value: length value
        :type value: :obj:`int` or :obj:`str`
        """
        self.lengths[index] = value

    def setRank(self, rank):
        """ sets dimension rank

        :param index: dimension rank
        :type index: :obj:`src`
        """
        self.rank = rank

    def setSourceRank(self, rank):
        """ sets dimension rank

        :param index: dimension rank
        :type index: :obj:`src`
        """
        self.srcrank = rank

    def setSelection(self, index, value):
        """ sets selection dict element

        :param index: selection index
        :type index: :obj:`int`
        :param value: selection value
        :type value: :obj:`int` or :obj:`str`
        """
        self.selection[index] = value

    def setSourceLength(self, index, value):
        """ sets source lengths dict element

        :param index: length index
        :type index: :obj:`int`
        :param value: length value
        :type value: :obj:`int` or :obj:`str`
        """
        self.srclengths[index] = value

    def setSourceSelection(self, index, value):
        """ sets source selection dict element

        :param index: selection index
        :type index: :obj:`int`
        :param value: selection value
        :type value: :obj:`int` or :obj:`str`
        """
        self.srcselection[index] = value

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

    def __getSourceShape(self):
        """ provides source shape

        :returns: object shape
        :rtype: :obj:`list` <:obj:`int` >
        """
        shape = []
        try:
            if int(self.srcrank) > 0:
                for i in range(int(self.srcrank)):
                    si = str(i + 1)
                    if self.srclengths and si in self.srclengths.keys() \
                       and self.srclengths[si] is not None:
                        if int(self.srclengths[si]) > 0:
                            shape.append(int(self.srclengths[si]))
                    else:
                        raise XMLSettingSyntaxError(
                            "Dimensions not defined")
                if len(shape) < int(self.srcrank):
                    raise XMLSettingSyntaxError(
                        "Too small dimension number")
        except XMLSettingSyntaxError:
            if self.srcrank and int(self.srcrank) >= 0:
                shape = [0] * (int(self.srcrank))
            else:
                shape = [0]
        return shape or None

    def __getSourceKey(self):
        """ provides source key

        :returns: object key
        :rtype: :obj:`list` <:obj:`int` >
        """
        key = []
        try:
            if int(self.srcrank) > 0:
                for i in range(int(self.srcrank)):
                    si = str(i + 1)
                    if self.srcselection and si in self.srcselection.keys() \
                       and self.srcselection[si] is not None:
                        key.append(self.srcselection[si])
                    else:
                        key.append(None)
        except XMLSettingSyntaxError:
            pass
        return key or None

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """

        shape = self.__getShape()
        if shape:
            self.__vmap["shape"] = shape
        key = self.__getKey()
        if key:
            self.__vmap["key"] = key
        srcshape = self.__getSourceShape()
        if srcshape is not None:
            self.__vmap["sourceshape"] = srcshape
        srckey = self.__getSourceKey()
        if srckey is not None:
            self.__vmap["sourcekey"] = srckey
        target = None
        filename = None
        fieldpath = None
        if "name" in self._tagAttrs.keys():
            self.__name = self._tagAttrs["name"]
        if "target" in self._tagAttrs.keys():
            if sys.version_info > (3,):
                target = self._tagAttrs["target"]
            else:
                target = self._tagAttrs["target"].encode()
            if target:
                self.__vmap["target"] = target
        if "filename" in self._tagAttrs.keys():
            if sys.version_info > (3,):
                filename = self._tagAttrs["filename"]
            else:
                filename = self._tagAttrs["filename"].encode()
            if filename:
                self.__vmap["filename"] = filename
        if "fieldpath" in self._tagAttrs.keys():
            if sys.version_info > (3,):
                fieldpath = self._tagAttrs["fieldpath"]
            else:
                fieldpath = self._tagAttrs["fieldpath"].encode()
            if fieldpath:
                self.__vmap["fieldpath"] = fieldpath
        if not self.source:
            self.last.appendVmap(self.__vmap)
        if self.source:
            if self.source.isValid():
                return self.strategy, self.trigger

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
                    self.last.appendVmap(val, self.__vmap)

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
        FElementWithAttr.__init__(self, "vds", attrs, last, streams=streams,
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
        #: (:obj:`str`) field data type
        self.__dtype = ""
        #: (:obj:`str`) field name
        self.__name = ""
        #: (:obj:`list` <:obj:`int` >) shape
        self.__shape = []
        #: (:obj:`list` <:obj:`dict` >) vmap list
        self.__vmaps = []

    def setRank(self, rank):
        """ sets dimension rank

        :param index: dimension rank
        :type index: :obj:`src`
        """
        self.rank = rank

    def setLength(self, index, value):
        """ sets lengths dict element

        :param index: length index
        :type index: :obj:`int`
        :param value: length value
        :type value: :obj:`int` or :obj:`str`
        """
        self.lengths[index] = value

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
                    self.__vmaps.append({"target": el.strip()})
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
        return self.__setStrategy(self.__name)

    def __cureKeys(self, key):
        tkey = []
        if isinstance(key, list):
            try:
                sk = list(set([len(ky) for ky in key]))
            except Exception:
                sk = []
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
                    stride.append(std)
                return FileWriter.FTHyperslab(offset, block, count, stride)
            for ky in key:
                if isinstance(ky, list) and len(ky) > 0 and len(ky) < 4:
                    tkey.append(slice(*ky))
                else:
                    if ky is None:
                        ky = slice(None)
                    tkey.append(ky)

            return tuple(tkey)
        return key

    def appendVmap(self, values, base=None):
        """ append virtual map items

        :param values: a list of map items to append
        :type values:  :obj:`str`  or :obj:`list`< :obj:`str` >
                        or  :obj:`list`< :obj:`dict` >
        :param base: base map item to append
        :type base: :obj:`dict`
        """
        if hasattr(values, "shape") and values.shape == tuple():
            values = str(values)
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
            if isinstance(base, dict):
                fval = dict(base)
            else:
                fval = {}
            if isinstance(vl, dict):
                fval.update(vl)
            else:
                fval.update({"target": vl.strip()})
            self.__vmaps.append(fval)
        return len(self.__vmaps)

    def __findShape(self, key, eshape=None, unlimited=True):
        if isinstance(key, FileWriter.FTHyperslab):
            if not unlimited:
                count = [(ct if ct != FileWriter.writer.unlimited() else 1)
                         for ct in key.count]

                block = [(ct if ct != FileWriter.writer.unlimited() else 1)
                         for ct in key.block]
            else:
                count = key.count
                block = key.block
            eshape = [bl * count[hi] for hi, bl in enumerate(block)]
        if isinstance(key, tuple):
            eshape = []
            for ky in key:
                if not unlimited and ky.stop == FileWriter.writer.unlimited():
                    eshape.append(1)
                elif isinstance(ky, slice) and ky.stop > 0:
                    start = ky.start if ky.start is not None else 0
                    step = ky.step if ky.step is not None else 1
                    eshape.append((ky.stop - start) // step)
                else:
                    eshape.append(1)
        return eshape

    def __createVDS(self):
        """ create the virtual field object
        """
        vlf = FileWriter.virtual_field_layout(
            self.__shape, self.__dtype)
        counter = 0
        for vmap in self.__vmaps:
            fieldpath = ""
            filename = ""
            edtype = vmap["dtype"] \
                if "dtype" in vmap else self.__dtype
            key = vmap["key"] if "key" in vmap else counter
            key = self.__cureKeys(key)
            if "shape" in vmap:
                eshape = vmap["shape"]
            elif isinstance(key, int):
                eshape = list(self.__shape)
                eshape[0] = 1
            else:
                eshape = [0] * len(self.__shape)
            fieldpath = vmap["fieldpath"] \
                if "fieldpath" in vmap else "/data"
            filename = vmap["filename"] if "filename" in vmap else None
            if "target" in vmap:
                target = vmap["target"]
                if target.startswith("h5file:/"):
                    target = target[8:]
                if "::" in target:
                    filename, fieldpath = target.split("::")
                elif ":/" in target:
                    filename, fieldpath = target.split(":/")
                else:
                    fieldpath = target
            obj = self._lastObject()
            while filename is None:
                par = obj.parent
                if par is None:
                    break
                if hasattr(par, "root") and hasattr(par, "name"):
                    filename = par.name
                    break
                else:
                    obj = par
            sourceshape = vmap["sourceshape"] \
                if "sourceshape" in vmap else None
            sourcekey = vmap["sourcekey"] \
                if "sourcekey" in vmap else None
            sourcekey = self.__cureKeys(sourcekey)
            if not any(eshape):
                eshape = self.__findShape(key, eshape, unlimited=False)
            ef = FileWriter.target_field_view(
                filename, fieldpath, eshape, edtype)
            if eshape:
                counter += eshape[0]
            else:
                counter += 1
            # print("KEY", key, sourcekey, sourceshape, eshape)
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
                    self.appendVmap(val)
            # print("VMAPS", self.__vmaps)
            # print("SHaPE", self.__shape)
            # print("TYPE", self.__dtype)
            # print("NAME", self.__name)
            if self.__vmaps and self.__shape and self.__dtype and self.__name:
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
