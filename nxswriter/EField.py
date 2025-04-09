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

import numpy

from .DataHolder import DataHolder
from .FElement import FElementWithAttr
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)

from nxstools import filewriter as FileWriter


class EField(FElementWithAttr):

    """ field H5 tag element
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
        #: (:obj:`dict` <:obj:`int`, \
        #:        (:obj:`int`, :obj:`str`, :obj:`str`, :obj:`str`) >) \
        #:        index filter lists, i.e. \
        #:        {index: (filter_id, name, id, cd_values, availability)}
        self.filters = {}
        #: (:obj:`bool`) True if field is stored in STEP mode
        self.__extraD = False
        #: (:obj:`str`) strategy, i.e. INIT, STEP, FINAL, POSTRUN
        self.strategy = 'INIT'
        #: (:obj:`str`) trigger for asynchronous writing
        self.trigger = None
        #: (:obj:`int`) growing dimension
        self.grows = None
        #: (:obj:`str`) label for postprocessing data
        self.postrun = ""
        #: (:obj:`bool`) compression algorithm id
        self.compression = 0
        #: (:obj:`int`) compression rate
        self.compression_opts = []
        #: (:obj:`list` < :obj:`int` >) compression algorithm options
        self.rate = 2
        #: (:obj:`bool`) compression shuffle
        self.shuffle = True
        #: (:obj:`bool`) grew flag
        self.__grew = True

    def __isgrowing(self):
        """ checks if it is growing in extra dimension
        :brief: It checks if it is growing in extra dimension
                and setup internal variables
        """
        self.__extraD = False
        if self.source and self.source.isValid() and self.strategy == "STEP":
            self.__extraD = True
            if not self.grows:
                self.grows = 1
        else:
            self.grows = None

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

    def __getShape(self):
        """ provides shape

        :returns: object shape
        :rtype: :obj:`list` <:obj:`int` >
        """
        try:
            shape = self._findShape(
                self.rank, self.lengths,
                self.__extraD, self.grows, True, checkData=True)
            if self.grows and self.grows > len(shape):
                self.grows = len(shape)
            return shape
        except XMLSettingSyntaxError:
            if self.rank and int(self.rank) >= 0:
                shape = [0] * (int(self.rank) + int(self.__extraD))
            else:
                shape = [0]
            return shape

    def __createObject(self, dtype, name, shape):
        """ creates H5 object

        :param dtype: object type
        :type dtype: :obj:`str`
        :param name: object name
        :type name: :obj:`str`
        :param shape: object shape
        :type shape: :obj:`list` <:obj:`int` >
        :returns: H5 object
        :rtype: :class:`nxswriter.FileWriter.FTField`
        """

        if self._reloadmode:
            names = [kd.name for kd in self._lastObject()]
            if name in names:
                if sys.version_info < (3,):
                    name = name.encode()
                f = self._lastObject().open(name)
                return f

        chunk = [s if s > 0 else 1 for s in shape]
        minshape = [1 if s > 0 else 0 for s in shape]
        datafilter = None
        # create Filter

        datafilters = []
        if (self.compression and self.rate) or self.shuffle:
            datafilter = FileWriter.data_filter(self._lastObject())
            if (self.compression and self.rate):
                datafilter.rate = self.rate
                datafilter.options = tuple(self.compression_opts)
                datafilter.shuffle = self.shuffle
                datafilter.filterid = self.compression
            if self.shuffle:
                datafilter.shuffle = self.shuffle
            datafilters.append(datafilter)
        if self.filters:
            mindex = max(self.filters.keys())
            for ind in range(mindex):
                if ind in self.filters:
                    (filter_id, fname, cd_values, availability) = \
                        self.filters[ind]
                    datafilter = FileWriter.data_filter(self._lastObject())

                    datafilter.name = fname
                    datafilter.filterid = filter_id
                    datafilter.availability = availability
                    try:
                        if cd_values:
                            options = [int(vl) for vl in cd_values.split(",")]
                            datafilter.options = tuple(options)
                    except Exception:
                        if self._streams:
                            self._streams.error(
                                "EField::__createObject() - "
                                "Wrong filter cd_values ",
                                std=False)

                            raise Exception("Wrong filter cd_values")
                    datafilters.append(datafilter)

        if sys.version_info < (3,):
            name = name.encode()
            dtype = dtype.encode()

        try:
            if shape:
                if not chunk:
                    f = self._lastObject().create_field(
                        name, dtype, shape, [],
                        datafilter)
                elif self.canfail:
                    f = self._lastObject().create_field(
                        name, dtype, shape, chunk,
                        datafilter)
                else:
                    f = self._lastObject().create_field(
                        name, dtype, minshape or [1], chunk,
                        datafilter)
            else:
                if self.strategy in ['INIT', 'FINAL', None] and \
                   dtype in ["string", b"string", "unicode"]:
                    f = self._lastObject().create_field(
                        name, dtype)
                else:
                    if self.strategy in ['INIT', 'FINAL', None]:
                        mshape = [1]
                    else:
                        mshape = [0]
                    if datafilters:
                        f = self._lastObject().create_field(
                            name, dtype, mshape, [1], datafilters)
                    else:
                        f = self._lastObject().create_field(
                            name, dtype, mshape, [1])
        except Exception:
            info = sys.exc_info()
            import traceback
            message = str(info[1].__str__()) + "\n " + (" ").join(
                traceback.format_tb(sys.exc_info()[2]))
            if self._streams:
                self._streams.error(
                    "EField::__createObject() - "
                    "The field '%s' of '%s' type cannot be created: %s" %
                    (name, dtype, message),
                    std=False)

            raise XMLSettingSyntaxError(
                "The field '%s' of '%s' type cannot be created: %s" %
                (name, dtype, message))
        return f

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
        else:
            if sys.version_info > (3,):
                val = ("".join(self.content)).strip()
            else:
                val = ("".join(self.content)).strip().encode()
            if val:
                dh = self._setValue(int(self.rank), val)
                self.__growshape(dh.shape)
                self.h5Object[...] = dh.cast(self.h5Object.dtype)
            elif self.strategy != "POSTRUN":
                if self.h5Object.dtype != "string":
                    if self._streams:
                        self._streams.error(
                            "EField::__setStrategy() - "
                            "Warning: Invalid datasource for %s" % name,
                            std=False)

                    raise ValueError(
                        "Warning: Invalid datasource for %s" % name)

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

        # if it is growing in extra dimension
        self.__isgrowing()
        # type and name
        tp, nm = self.__typeAndName()
        # shape
        shape = self.__getShape()
        #: stored H5 file object (defined in base class)
        self.h5Object = self.__createObject(tp, nm, shape)
        # create attributes
        self.__setAttributes()

        # return strategy or fill the value in
        return self.__setStrategy(nm)

    def __writeData(self, holder):
        """ writes non-growing data

        :param holder: data holder
        :type holder: :class:`nxswriter.DataHolder.DataHolder`
        """
        try:
            self.h5Object[...] = holder.cast(self.h5Object.dtype)
        except Exception:
            if self._streams:
                self._streams.error(
                    "EField::__writedata() - "
                    "Storing single fields "
                    "not supported by pniio",
                    std=False)

            raise Exception("Storing single fields"
                            " not supported by pniio")

    def __writeScalarGrowingData(self, holder):
        """ writes growing scalar data

        :param holder: data holder
        :type holder: :class:`nxswriter.DataHolder.DataHolder`
        """

        arr = holder.cast(self.h5Object.dtype)
        if len(self.h5Object.shape) == 1:
            self.h5Object[self.h5Object.shape[0] - 1] = arr
        elif len(self.h5Object.shape) == 2:
            if self.grows == 2:
                self.h5Object[0, self.h5Object.shape[0] - 1] = arr
            else:
                self.h5Object[self.h5Object.shape[0] - 1, 0] = arr
        elif len(self.h5Object.shape) == 3:
            if self.grows == 3:
                self.h5Object[0, 0, self.h5Object.shape[0] - 1] = arr
            if self.grows == 2:
                self.h5Object[0, self.h5Object.shape[0] - 1, 0] = arr
            else:
                self.h5Object[self.h5Object.shape[0] - 1, 0, 0] = arr

    def __writeSpectrumGrowingData(self, holder):
        """ writes growing spectrum data

        :param holder: data holder
        :type holder: :class:`nxswriter.DataHolder.DataHolder`
        """

        # way around for a bug in pniio
        arr = holder.cast(self.h5Object.dtype)
        if self.grows == 1:
            if isinstance(arr, numpy.ndarray) \
                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                if len(self.h5Object.shape) == 2 \
                        and self.h5Object.shape[1] == 1:
                    self.h5Object[self.h5Object.shape[0] - 1, 0:len(arr)] = arr
                elif len(self.h5Object.shape) == 2:
                    self.h5Object[self.h5Object.shape[0] - 1, 0:len(arr)] = arr
                elif len(arr) > 1:
                    self.h5Object.grow(self.grows - 1, len(arr) - 1)
                    self.h5Object[self.h5Object.shape[0] - len(arr):
                                  (self.h5Object.shape[0])] = arr
                else:
                    self.h5Object[self.h5Object.shape[0] - 1] = arr
            else:
                if len(self.h5Object.shape) == 3:
                    self.h5Object[self.h5Object.shape[0] - 1, :, :] = arr
                elif len(self.h5Object.shape) == 2:
                    self.h5Object[self.h5Object.shape[0] - 1, 0:len(arr)] = arr
                elif hasattr(arr, "__iter__") and type(arr).__name__ != 'str' \
                        and len(arr) == 1:
                    self.h5Object[self.h5Object.shape[0] - 1] = arr
                elif hasattr(arr, "__iter__") and type(arr).__name__ != 'str' \
                        and len(arr) > 1:
                    self.h5Object.grow(self.grows - 1, len(arr) - 1)
                    self.h5Object[self.h5Object.shape[0] - len(arr):
                                  self.h5Object.shape[0]] = arr
                else:
                    if self._streams:
                        self._streams.error("Rank mismatch", std=False)
                    raise XMLSettingSyntaxError("Rank mismatch")

        else:
            if isinstance(arr, numpy.ndarray) \
                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                self.h5Object[0:len(arr), self.h5Object.shape[1] - 1] = arr
            else:
                if len(self.h5Object.shape) == 3:
                    if self.grows == 2:
                        self.h5Object[:, self.h5Object.shape[1] - 1, :] = arr
                    else:
                        self.h5Object[:, :, self.h5Object.shape[2] - 1] = arr
                else:
                    self.h5Object[0:len(arr), self.h5Object.shape[1] - 1] = arr

    def __writeImageGrowingData(self, holder):
        """ writes growing image data

        :param holder: data holder
        :type holder: :class:`nxswriter.DataHolder.DataHolder`
        """
        arr = holder.cast(self.h5Object.dtype)
        if self.grows == 1:
            if len(self.h5Object.shape) == 3:
                self.h5Object[self.h5Object.shape[0] - 1,
                              0:len(arr), 0:len(arr[0])] = arr
            elif len(self.h5Object.shape) == 2:
                if len(holder.shape) == 1:
                    self.h5Object[self.h5Object.shape[0] - 1, :] = arr[0]
                elif len(holder.shape) > 1 and holder.shape[0] == 1:
                    self.h5Object[self.h5Object.shape[0] - 1, :] \
                        = [c[0] for c in arr]
                elif len(holder.shape) > 1 and holder.shape[1] == 1:
                    self.h5Object[self.h5Object.shape[0] - 1, :] = arr[:, 0]
                elif len(holder.shape) > 1 and holder.shape[0] > 1:
                    self.h5Object.grow(self.grows - 1, holder.shape[0] - 1)
                    self.h5Object[self.h5Object.shape[0] - holder.shape[0]:
                                  self.h5Object.shape[0], :] = arr
                else:
                    self.h5Object[self.h5Object.shape[0] - 1, :] = arr[0]
            elif len(self.h5Object.shape) == 1:
                self.h5Object[self.h5Object.shape[0] - 1] = arr[0][0]
            else:
                if self._streams:
                    self._streams.error("Rank mismatch", std=False)
                raise XMLSettingSyntaxError("Rank mismatch")

        elif self.grows == 2:
            if len(self.h5Object.shape) == 3:
                self.h5Object[0: len(arr), self.h5Object.shape[1] - 1,
                              0: len(arr[0])] = arr
            elif len(self.h5Object.shape) == 2:
                self.h5Object[0: len(arr[0]),
                              self.h5Object.shape[1] - 1] = arr[0]
            else:
                if self._streams:
                    self._streams.error("Rank mismatch", std=False)
                raise XMLSettingSyntaxError("Rank mismatch")
        else:
            self.h5Object[0: len(arr), 0: len(arr[0]),
                          self.h5Object.shape[2] - 1] = arr

    def __writeVertexGrowingData(self, holder):
        """ writes growing vertex data

        :param holder: data holder
        :type holder: :class:`nxswriter.DataHolder.DataHolder`
        """
        arr = holder.cast(self.h5Object.dtype)
        if self.grows == 1:
            if len(self.h5Object.shape) == 3 and len(holder.shape) == 3:
                if len(holder.shape) > 1 and holder.shape[0] > 1:
                    self.h5Object.grow(self.grows - 1, holder.shape[0] - 1)
                    self.h5Object[
                        self.h5Object.shape[0] -
                        holder.shape[0]:self.h5Object.shape[0],
                        :, :] = arr
                else:
                    self.h5Object[self.h5Object.shape[0] - 1, :, :] = arr[0]
            elif len(self.h5Object.shape) == 2:
                self.h5Object[self.h5Object.shape[0] - 1, :] = arr[0][0]
            elif len(self.h5Object.shape) == 1:
                self.h5Object[self.h5Object.shape[0] - 1, :] = arr[0][0][0]
            else:
                if self._streams:
                    self._streams.error("Rank mismatch", std=False)
                raise XMLSettingSyntaxError("Rank mismatch")

        else:
            if self._streams:
                self._streams.error(
                    "Vertex growing data with grows>1 not supported",
                    std=False)
            raise XMLSettingSyntaxError(
                "Vertex growing data with grows>1 not supported")

    def __writeGrowingData(self, holder):
        """ writes growing data

        :param holder: data holder
        :type holder: :class:`nxswriter.DataHolder.DataHolder`
        """
        if str(holder.format).split('.')[-1] == "SCALAR":
            self.__writeScalarGrowingData(holder)
        elif str(holder.format).split('.')[-1] == "SPECTRUM":
            self.__writeSpectrumGrowingData(holder)
        elif str(holder.format).split('.')[-1] == "IMAGE":
            self.__writeImageGrowingData(holder)
        elif str(holder.format).split('.')[-1] == "VERTEX":
            self.__writeVertexGrowingData(holder)
        else:
            if self._streams:
                self._streams.error(
                    "Case with %s format not supported " %
                    str(holder.format).split('.')[-1],
                    std=False)

            raise XMLSettingSyntaxError(
                "Case with %s  format not supported " %
                str(holder.format).split('.')[-1])

    def __grow(self):
        """ grows the h5 field

        :brief: Ir runs the grow command of h5Object with grows-1 parameter

        """
        if self.grows and self.grows > 0 and hasattr(self.h5Object, "grow"):
            shape = self.h5Object.shape
            if self.grows and self.grows > len(shape):
                self.grows = len(shape)
            if not self.grows and self.__extraD:
                self.grows = 1

            self.h5Object.grow(self.grows - 1)

    def __growshape(self, shape):
        """ reshapes h5 object

        :param shape: required shape
        :type shape: :obj:`list` <:obj:`int` >
        """
        h5shape = self.h5Object.shape
        ln = len(shape)
        if ln > 0 and len(h5shape) > 0:
            j = 0
            for i in range(len(h5shape)):
                if not self.__extraD or (
                        self.grows - 1 != i and
                        not (i == 0 and self.grows == 0)):
                    if shape[j] - h5shape[i] > 0:
                        self.h5Object.grow(i, shape[j] - h5shape[i])
                    elif not h5shape[i]:
                        self.h5Object.grow(i, 1)
                    j += 1
                elif self.__extraD and len(shape) > j and shape[j] > 1:
                    if len(shape) == len(h5shape) and shape[-1] != 0:
                        j += 1

    def run(self):
        """ runner

        :brief: During its thread run it fetches the data from the source
        """
        self.__grew = False
        try:
            if self.source:
                dt = self.source.getData()
                dh = None
                if dt and isinstance(dt, dict):
                    dh = DataHolder(streams=self._streams, **dt)
                self.__grow()
                self.__grew = True
                if not dh:
                    message = self.setMessage("Data without value")
                    self.error = message
                elif not hasattr(self.h5Object, 'shape'):
                    message = self.setMessage("H5 Object not created")
                    self.error = message
                else:
                    if not self.__extraD:
                        self.__growshape(dh.shape)
                        self.__writeData(dh)
                    else:
                        if len(self.h5Object.shape) >= self.grows \
                           and (self.h5Object.shape[self.grows - 1] == 1 or
                                self.canfail):
                            self.__growshape(dh.shape)
                        self.__writeGrowingData(dh)
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

    def __fillMax(self):
        """ fills object with maximum value

        :brief: It fills object or an extend part of object by default value
        """
        shape = list(self.h5Object.shape)
        nptype = self.h5Object.dtype
        value = ''

        if self.grows and self.grows > len(shape):
            self.grows = len(shape)
        if not self.grows and self.__extraD:
            self.grows = 1
        if self.grows:
            shape.pop(self.grows - 1)

        shape = [s if s > 0 else 1 for s in shape]
        self.__growshape(shape)

        if nptype == "bool":
            value = False
        elif nptype != "string":
            try:
                value = numpy.iinfo(getattr(numpy, nptype)).max
            except Exception:
                try:
                    try:
                        value = numpy.finfo(getattr(numpy, nptype)).max.item()
                    except Exception:
                        value = numpy.asscalar(
                            numpy.finfo(getattr(numpy, nptype)).max)
                except Exception:
                    value = 0
        else:
            nptype = "str"

        dformat = 'SCALAR'
        if not self._scalar and shape and len(shape) > 0 and shape[0] >= 1:
            arr = numpy.empty(shape, dtype=nptype)
            arr.fill(value)
            if len(shape) == 1:
                dformat = 'SPECTRUM'
            else:
                dformat = 'IMAGE'
        else:
            arr = value

        dh = DataHolder(dformat, arr, NTP.pTt[self.h5Object.dtype],
                        shape, streams=self._streams)

        if not self.__extraD:
            self.__writeData(dh)
        else:
            if not self.__grew:
                self.__grow()
            self.__writeGrowingData(dh)

    def markFailed(self, error=None):
        """ marks the field as failed

        :brief: It marks the field as failed
        :param error: error string
        :type error: :obj:`str`
        """
        if self.h5Object is not None:
            if error:
                if isinstance(error, tuple):
                    serror = str(tuple([str(e) for e in error]))
                else:
                    serror = str(error)
                if "nexdatas_canfail_error" in \
                   [at.name for at in self.h5Object.attributes]:
                    olderror = \
                        self.h5Object.attributes["nexdatas_canfail_error"][...]
                    if olderror is not None:
                        serror = str(olderror) + "\n" + serror
                self.h5Object.attributes.create(
                    "nexdatas_canfail_error",
                    "string",
                    overwrite=True)[...] = serror
            self.h5Object.attributes.create(
                "nexdatas_canfail", "string", overwrite=True)[...] = "FAILED"
            if self._streams:
                self._streams.info(
                    "EField::markFailed() - %s marked as failed" %
                    (self.h5Object.name if hasattr(self.h5Object, "name")
                     else None))

            self.__fillMax()
