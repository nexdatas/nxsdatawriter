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

""" Types converters  """

import numpy
import sys


if sys.version_info > (3,):
    long = int


try:
    _npver = numpy.version.version.split(".")
    NPMAJOR = int(_npver[0])
    if NPMAJOR > 1:
        npstring = numpy.bytes_
    else:
        npstring = numpy.string_
except Exception:
    NPMAJOR = 1
    npstring = numpy.string_


def nptype(dtype):
    """ converts to numpy types

    :param dtype: h5 writer type type
    :type dtype: :obj:`str`
    :returns: nupy type
    :rtype: :obj:`str`
    """
    if str(dtype) in ['string', b'string']:
        return 'str'
    return dtype


class Converters(object):

    """ set of converters
    """

    @classmethod
    def toBool(cls, value):
        """ converts to bool

        :param value: variable to convert
        :type value: any
        :returns: result in bool type
        :rtype: :obj:`bool`
        """
        if type(value).__name__ == 'str' or type(value).__name__ == 'unicode':
            lvalue = value.strip().lower()
            if lvalue == 'false' or lvalue == '0':
                return False
            else:
                return True
        elif value:
            return True
        return False


class NTP(object):

    """ type converter
    """
    #: (:obj:`dict` <:obj:`str` ,:obj:`str` >) map of Python:Tango types
    pTt = {"long": "DevLong64", "str": "DevString",
           "unicode": "DevString", "bool": "DevBoolean",
           "int": "DevLong64", "int64": "DevLong64", "int32": "DevLong",
           "int16": "DevShort", "int8": "DevUChar", "uint": "DevULong64",
           "uint64": "DevULong64", "uint32": "DevULong",
           "uint16": "DevUShort",
           "uint8": "DevUChar", "float": "DevDouble", "float64": "DevDouble",
           "float32": "DevFloat", "float16": "DevFloat",
           "string": "DevString", "str": "DevString"}

    #: (:obj:`dict` <:obj:`str` , :obj:`str` >) map of NEXUS :  numpy types
    nTnp = {"NX_FLOAT32": "float32", "NX_FLOAT64": "float64",
            "NX_FLOAT": "float64", "NX_NUMBER": "float64",
            "NX_INT": "int64", "NX_INT64": "int64",
            "NX_INT32": "int32", "NX_INT16": "int16", "NX_INT8": "int8",
            "NX_UINT64": "uint64", "NX_UINT32": "uint32",
            "NX_UINT16": "uint16",
            "NX_UINT8": "uint8", "NX_UINT": "uint64", "NX_POSINT": "uint64",
            "NX_DATE_TIME": "string", "ISO8601": "string", "NX_CHAR": "string",
            "NX_BOOLEAN": "bool"}

    #: (:obj:`dict` <:obj:`str` , :obj:`type` or :obj:`types.MethodType` >) \
    #:      map of type : converting function
    convert = {"float16": float, "float32": float, "float64": float,
               "float": float, "int64": long, "int32": int,
               "int16": int, "int8": int, "int": int, "uint64": long,
               "uint32": long, "uint16": int,
               "uint8": int, "uint": int, "string": str, "str": str,
               "bool": Converters.toBool}

    #: (:obj:`dict` <:obj:`str` , :obj:`str` >) map of tag attribute types
    aTn = {"signal": "NX_INT", "axis": "NX_INT", "primary": "NX_INT32",
           "offset": "NX_INT", "stride": "NX_INT", "file_time": "NX_DATE_TIME",
           "file_update_time": "NX_DATE_TIME", "restricts": "NX_INT",
           "ignoreExtraGroups": "NX_BOOLEAN",
           "ignoreExtraFields": "NX_BOOLEAN",
           "ignoreExtraAttributes": "NX_BOOLEAN",
           "minOccus": "NX_INT", "maxOccus": "NX_INT"}

    #: (:obj:`dict` <:obj:`str` , :obj:`str` >) \
    #:     map of vector tag attribute types
    aTnv = {"vector": "NX_FLOAT"}

    #: (:obj:`dict` <:obj:`int` , :obj:`str` >) map of rank :  data format
    rTf = {0: "SCALAR", 1: "SPECTRUM", 2: "IMAGE", 3: "VERTEX"}

    def arrayRank(self, array):
        """ array rank

        :brief: It calculates the rank of the array
        :param array: given array
        :type array: any
        :returns: rank
        :rtype: :obj:`int`
        """
        rank = 0
        if hasattr(array, "__iter__") and not \
           isinstance(array, (str, bytes)):
            try:
                rank = 1 + self.arrayRank(array[0])
            except IndexError:
                if hasattr(array, "shape") and len(array.shape) == 0:
                    rank = 0
                else:
                    rank = 1
        return rank

    def arrayRankRShape(self, array):
        """ array rank, inverse shape and type

        :brief: It calculates the rank, inverse shape and type of
                the first element of the list array
        :param array: given array
        :type array: any
        :returns: (rank, inverse shape, type)
        :rtype: (:obj:`int` , :obj:`list` <:obj:`int` > , :obj:`str` )
        """
        rank = 0
        shape = []
        pythonDType = None
        if hasattr(array, "__iter__") and not \
           isinstance(array, (str, bytes)):
            try:
                rank, shape, pythonDType = self.arrayRankRShape(array[0])
                rank += 1
                shape.append(len(array))
            except IndexError:
                if hasattr(array, "shape") and len(array.shape) == 0:
                    rank = 0
                    if type(array) in [npstring, numpy.str_]:
                        pythonDType = "str"
                    elif hasattr(array, "dtype"):
                        pythonDType = str(array.dtype)
                    else:
                        pythonDType = type(array.tolist()).__name__
                else:
                    rank = 1
                    shape.append(len(array))

        else:
            if type(array) in [npstring, numpy.str_]:
                pythonDType = "str"
            elif hasattr(array, "dtype"):
                pythonDType = str(array.dtype)
            elif hasattr(array, "tolist"):
                pythonDType = type(array.tolist()).__name__
            else:
                pythonDType = type(array).__name__
        return (rank, shape, pythonDType)

    def arrayRankShape(self, array):
        """ array rank, shape and type

        :brief: It calculates the rank, shape and type of
                the first element of the list array
        :param array: given array
        :type array: any
        :returns: (rank, shape, type)
        :rtype: (:obj:`int` , :obj:`list` <:obj:`int` > , :obj:`str` )

        """
        rank, shape, pythonDType = self.arrayRankRShape(array)
        if shape:
            shape.reverse()
        return (rank, shape, pythonDType)

    def createArray(self, value, fun=None):
        """ creates python array from the given array with applied
            the given function to it elements

        :param value: given array
        :type array: any
        :param fun: applied function
        :type fun: :obj:`type` or :obj:`types.MethodType`
        :returns: created array
        :rtype: :obj:`list` <any>
        """
        if not hasattr(value, "__iter__") or \
           isinstance(value, (str, bytes)):
            return fun(value) if fun else value
        else:
            return [self.createArray(v, fun) for v in value]
