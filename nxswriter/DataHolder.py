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

""" definition of a data holder with casting methods """

import numpy

from .Types import NTP, nptype


class DataHolder(object):

    """ Holder for passing data
    """

    def __init__(self, rank, value, tangoDType, shape,
                 encoding=None, decoders=None, streams=None):
        """ constructor

        :param rank: format of the data, i.e. SCALAR, SPECTRUM, IMAGE, VERTEX
        :type rank: :obj:`str`
        :param value: value of the data. It may be also 1D and 2D array
        :type value: any
        :param tangoDType: type of the data
        :type tangoDType: :obj:`str`
        :param shape: shape of the data
        :type shape: :obj:`list` <:obj:`int`>
        :param encoding: encoding type of Tango DevEncoded varibles
        :type encoding: :obj:`str`
        :param decoders: poll with decoding classes
        :type decoders: :class:`nxswriter.DecoderPool.DecoderPool`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """

        #: (:obj:`str`) data format, i.e. SCALAR, SPECTRUM, IMAGE, VERTEX
        self.format = rank
        #: (any) data value
        self.value = value
        #: (:obj:`str`)  tango data type
        self.tangoDType = tangoDType
        #: (:obj:`list` <:obj:`int`>) data shape
        self.shape = shape
        #: (:obj:`str`)  encoding type of Tango DevEncoded varibles
        self.encoding = str(encoding) if encoding else None
        #: pool with decoding algorithm
        self.decoders = decoders

        #: (:class:`StreamSet` or :class:`tango.LatestDeviceImpl`) stream set
        self._streams = streams
        if str(self.tangoDType) == 'DevEncoded':
            self.__setupEncoded()

    def __setupEncoded(self):
        """ decode value
        """
        self.shape = None
        if self.encoding and self.decoders and \
                self.decoders.hasDecoder(self.encoding):
            decoder = self.decoders.get(self.encoding)
            decoder.load(self.value)
            self.shape = decoder.shape()
            if self.shape:
                self.value = decoder.decode()
                rank = NTP().arrayRank(self.value)
                if rank > 2:
                    if self._streams:
                        self._streams.error(
                            "DataHolder::__setupEncoded() - "
                            "Unsupported variables format",
                            std=False)

                    raise ValueError("Unsupported variables format")
                self.format = ["SCALAR", "SPECTRUM",
                               "IMAGE", "VERTEX"][rank]

            tp = decoder.dtype
            if tp in NTP.pTt.keys():

                self.tangoDType = NTP.pTt[tp]

        if self.value is None:
            if self._streams:
                self._streams.error(
                    "DataHolder::__setupEncoded() - "
                    "Encoding of DevEncoded variables not defined",
                    std=False)

            raise ValueError(
                "Encoding of DevEncoded variables not defined")

        if self.shape is None:
            if self._streams:
                self._streams.error(
                    "DataHolder::__setupEncoded() - "
                    "Encoding or Shape not defined",
                    std=False)

            raise ValueError("Encoding or Shape not defined")

    def cast(self, dtype):
        """ casts the data into given type

        :param dtype: given type of data
        :type dtype: :obj:`str`
        :returns: numpy array of defined type or list
                  for strings or value for SCALAR
        :rtype: :class:`numpy.ndarray`

        """
        if str(self.format).split('.')[-1] == "SCALAR":
            if dtype in NTP.pTt.keys() \
                    and NTP.pTt[dtype] == str(self.tangoDType):
                # workaround for bug python-pni #8
                if isinstance(self.value, str):
                    return str(self.value)
                else:
                    return self.value
            else:
                if self.value == "" and (
                        dtype not in ['str', 'string', 'bytes']):
                    return NTP.convert[dtype](0)
                else:
                    return NTP.convert[dtype](self.value)

        else:
            if dtype in NTP.pTt.keys() \
                    and NTP.pTt[dtype] == str(self.tangoDType) \
                    and (dtype not in ['str', 'string', 'bytes']):
                if type(self.value).__name__ == 'ndarray' and \
                        self.value.dtype.name == dtype:
                    return self.value
                else:
                    return numpy.array(self.value, dtype=dtype)
            elif dtype == "bool":
                return numpy.array(
                    NTP().createArray(self.value, NTP.convert[dtype]),
                    dtype=dtype)
            else:
                try:
                    return numpy.array(self.value, dtype=nptype(dtype))
                except Exception:
                    return numpy.array(
                        NTP().createArray(self.value, NTP.convert[dtype]),
                        dtype=nptype(dtype))
