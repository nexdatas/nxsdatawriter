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
# \file DataHolderTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import numpy
import binascii
import time


from nxswriter.DataHolder import DataHolder
from nxswriter.Types import NTP, nptype
from nxswriter.DecoderPool import DecoderPool

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class DataHolderTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self.__data = {"rank": "SCALAR",
                       "value": "123", "tangoDType": "DevShort",
                       "shape": [1, 0],
                       "encoding": None, "decoders": None}

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # Exception tester
    # \param exception expected exception
    # \param method called method
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error = False
            method(*args, **kwargs)
        except Exception:
            error = True
        self.assertEqual(error, True)

    # Creates an encoded image from numpy array
    # \param image numpy array
    # \returns lima image
    def encodeImage(self, image):
        modes = {'uint8': 0, 'uint16': 1, 'uint32': 2, 'uint64': 3}
        formatID = {0: 'B', 1: 'H', 2: 'I', 3: 'Q'}
        format = 'VIDEO_IMAGE'
        mode = modes[str(image.dtype)]
        height, width = image.shape
        version = 1
        endian = sys.byteorder == u'big'
        hsize = struct.calcsize('!IHHqiiHHHH')
        header = struct.pack('!IHHqiiHHHH', 0x5644454f, version, mode, -1,
                             width, height, endian, hsize, 0, 0)
        fimage = image.flatten()
#  for uint32 and python2.6 one gets the struct.pack bug:
# test/VDEOdecoderTest.py:90: DeprecationWarning: struct integer overflow
# masking is deprecated
        ibuffer = struct.pack(formatID[mode] * fimage.size, *fimage)

        return [format, header + ibuffer]

    # default constructor test
    # \brief It tests default settings
    def test_default_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        el = DataHolder(**self.__data)
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.format, self.__data["rank"])
        self.assertEqual(el.value, self.__data["value"])
        self.assertEqual(el.tangoDType, self.__data["tangoDType"])
        self.assertEqual(el.shape, self.__data["shape"])
        self.assertEqual(el.encoding, self.__data["encoding"])
        self.assertEqual(el.decoders, self.__data["decoders"])

    # setup test
    # \brief It tests default settings
    def test_constructor_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+01, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
            # "State":[ "string", "DevState", tango._tango.DevState.ON],
        }

        for a in arr:

            data = {"rank": "SCALAR",
                    "value": arr[a][2],
                    "tangoDType": arr[a][1],
                    "shape": [1, 0],
                    "encoding": None,
                    "decoders": None}
            el = DataHolder(**data)

            self.assertTrue(isinstance(el, object))
            self.assertEqual(el.format, data["rank"])
            self.assertEqual(el.value, data["value"])
            self.assertEqual(el.tangoDType, data["tangoDType"])
            self.assertEqual(el.shape, data["shape"])
            self.assertEqual(el.encoding, data["encoding"])
            self.assertEqual(el.decoders, data["decoders"])

    # setup test
    # \brief It tests default settings
    def test_constructor_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0]],
            "SpectrumUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "SpectrumShort": ["int16", "DevShort", -123, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1234, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -124, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 234, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 234, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 23, [1, 0]],
            "SpectrumFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", -2.456673e+02, [1, 0],
                               1e-14],
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
        }

        for k in arr:

            if arr[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arr[k][2] = [arr[k][2] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0], 0]

        for a in arr:

            data = {"rank": "SPECTRUM",
                    "value": arr[a][2],
                    "tangoDType": arr[a][1],
                    "shape": arr[a][3],
                    "encoding": None,
                    "decoders": None}
            el = DataHolder(**data)

            self.assertTrue(isinstance(el, object))
            self.assertEqual(el.format, data["rank"])
            self.assertEqual(el.tangoDType, data["tangoDType"])
            self.assertEqual(el.shape, data["shape"])
            self.assertEqual(el.encoding, data["encoding"])
            self.assertEqual(el.decoders, data["decoders"])
            self.assertEqual(el.value, data["value"])

    # setup test
    # \brief It tests default settings
    def test_constructor_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "ImageBoolean": ["bool", "DevBoolean", True, [1, 0]],
            "ImageUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "ImageShort": ["int16", "DevShort", -123, [1, 0]],
            "ImageUShort": ["uint16", "DevUShort", 1234, [1, 0]],
            "ImageLong": ["int64", "DevLong", -124, [1, 0]],
            "ImageULong": ["uint64", "DevULong", 234, [1, 0]],
            "ImageLong64": ["int64", "DevLong64", 234, [1, 0]],
            "ImageULong64": ["uint64", "DevULong64", 23, [1, 0]],
            "ImageFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "ImageDouble": ["float64", "DevDouble", -2.456673e+02, [1, 0],
                            1e-14],
            "ImageString": ["string", "DevString", "MyTrue", [1, 0]],
        }

        for k in arr:

            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[arr[k][2] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [[(True if self.__rnd.randint(0, 1) else False)
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]

        for a in arr:

            data = {"rank": "IMAGE",
                    "value": arr[a][2],
                    "tangoDType": arr[a][1],
                    "shape": arr[k][3],
                    "encoding": None,
                    "decoders": None}
            el = DataHolder(**data)

            self.assertTrue(isinstance(el, object))
            self.assertEqual(el.format, data["rank"])
            self.assertEqual(el.tangoDType, data["tangoDType"])
            self.assertEqual(el.shape, data["shape"])
            self.assertEqual(el.encoding, data["encoding"])
            self.assertEqual(el.decoders, data["decoders"])
            self.assertEqual(el.value, data["value"])

    # setup test
    # \brief It tests default settings
    def test_constructor_encode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        dp = DecoderPool()
        spectrum = numpy.array([1234, 5678, 45, 345], dtype=numpy.uint32)
        image = numpy.array(
            [[2, 5, 4, 6], [3, 4, 3, 4], [3, 6, 7, 8]], dtype='uint8')

        arr = {
            "ScalarEncoded": [
                "UTF8", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b"),
                [1, 0], "SCALAR",
                b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b", "DevString"],
            "SpectrumEncoded": [
                "UINT32", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00'),
                [4, 0], "SPECTRUM", spectrum, "DevULong"],
            "ImageEncoded": ["LIMA_VIDEO_IMAGE", "DevEncoded",
                             self.encodeImage(image),
                             list(image.shape), "IMAGE", image, "DevUChar"],
        }

        for a in arr:

            data = {"rank": "SCALAR",
                    "value": arr[a][2],
                    "tangoDType": arr[a][1],
                    "shape": [1, 0],
                    "encoding": arr[a][0],
                    "decoders": dp}
            el = DataHolder(**data)

            self.assertTrue(isinstance(el, object))
            self.assertEqual(el.format, arr[a][4])
            self.assertEqual(el.tangoDType, arr[a][6])
            self.assertEqual(el.shape, arr[a][3])
            self.assertEqual(el.encoding, data["encoding"])
            self.assertEqual(el.decoders, data["decoders"])

            if el.shape == [1, 0]:
                self.assertEqual(el.value, arr[a][5])
            elif len(el.shape) == 2 and el.shape[1] == 0:
                self.assertEqual(len(el.value), len(arr[a][5]))
                self.assertEqual(len(el.value), el.shape[0])
                for i in range(el.shape[0]):
                    self.assertEqual(el.value[i], arr[a][5][i])
            elif len(el.shape) == 2 and el.shape[1] != 0:
                self.assertEqual(len(el.value), len(arr[a][5]))
                self.assertEqual(len(el.value), el.shape[0])
                for i in range(el.shape[0]):
                    self.assertEqual(len(el.value[i]), len(arr[a][5][i]))
                    self.assertEqual(len(el.value[i]), el.shape[1])
                    for j in range(el.shape[1]):
                        self.assertEqual(el.value[i][j], arr[a][5][i][j])
            else:
                print("WARNING %s %s" % (a, "Case not supported"))

    # setup test
    # \brief It tests default settings
    def test_constructor_encode_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        dp = DecoderPool()
        spectrum = numpy.array([1234], dtype=numpy.uint32)
        image = numpy.array([[2]], dtype='uint16')

        arr = {
            "ScalarEncoded": ["UTF8", "DevEncoded", ("UTF8", b"\xc3\xb3"),
                              [1, 0], "SCALAR", b"\xc3\xb3", "DevString"],
            "SpectrumEncoded": ["UINT32", "DevEncoded",
                                ('INT32', b'\xd2\x04\x00\x00'),
                                [1, 0], "SPECTRUM", spectrum, "DevULong"],
            "ImageEncoded": ["LIMA_VIDEO_IMAGE", "DevEncoded",
                             self.encodeImage(image),
                             list(image.shape), "IMAGE", image, "DevUShort"],
        }

        for a in arr:

            data = {"rank": "SCALAR",
                    "value": arr[a][2],
                    "tangoDType": arr[a][1],
                    "shape": [1, 0],
                    "encoding": arr[a][0],
                    "decoders": dp}
            el = DataHolder(**data)

            self.assertTrue(isinstance(el, object))
            self.assertEqual(el.format, arr[a][4])
            self.assertEqual(el.tangoDType, arr[a][6])
            self.assertEqual(el.shape, arr[a][3])
            self.assertEqual(el.encoding, data["encoding"])
            self.assertEqual(el.decoders, data["decoders"])

            self.assertEqual(el.value, arr[a][5])

    # setup test
    # \brief It tests default settings
    def test_cast_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arrs = {}

        arrs["b"] = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
        }

        arrs["i"] = {
            "ScalarShort": ["int16", "DevShort", 123],
            "ScalarLong": ["int64", "DevLong", 124],
            "ScalarLong64": ["int64", "DevLong64", 234],
        }

        arrs["u"] = {
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
        }

        arrs["f"] = {
            "ScalarFloat": ["float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", 2.456673e+02, 1e-14],
        }

        arrs["s"] = {
            "ScalarString": ["string", "DevString", "MyTrue"],
            # "State":[ "string", "DevState", tango._tango.DevState.ON],
        }

        types = {}

        types["i"] = ["int", "int8", "int16", "int32", "int64"]
        types["u"] = ["uint", "uint8", "uint16", "uint32", "uint64"]
        types["f"] = ["float", "float16", "float32", "float64"]
        types["s"] = ["string"]
        types["b"] = ["bool"]

        ca = {
            "i": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "u": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "f": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "s": {"i": True, "u": True, "f": True, "s": True, "b": True},
            "b": {"i": True, "u": True, "f": True, "s": True, "b": True}
        }

        for k in arrs:
            arr = arrs[k]
            for a in arr:
                data = {"rank": "SCALAR",
                        "value": arr[a][2],
                        "tangoDType": arr[a][1],
                        "shape": [1, 0],
                        "encoding": None,
                        "decoders": None}
                el = DataHolder(**data)

                self.assertTrue(isinstance(el, object))
                self.assertEqual(el.format, data["rank"])
                self.assertEqual(el.value, data["value"])
                self.assertEqual(el.tangoDType, data["tangoDType"])
                self.assertEqual(el.shape, data["shape"])
                self.assertEqual(el.encoding, data["encoding"])
                self.assertEqual(el.decoders, data["decoders"])
                for c in ca:
                    if ca[c][k] is True:
                        for it in types[c]:

                            self.assertEqual(
                                NTP.convert[it](el.value), el.cast(it))
                    else:
                        for it in types[c]:
                            self.myAssertRaise(ValueError, el.cast, it)

    # setup test
    # \brief It tests default settings
    def test_cast_scalar_from_string(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arrs = {}

        arrs["f"] = {
            "ScalarString1": ["string", "DevString", "12.3243"],
            "ScalarString2": ["string", "DevString", "-12.3243"],
            "ScalarString3": ["string", "DevString", "12.3243"],
        }

        arrs["i"] = {
            "ScalarString1": ["string", "DevString", "-1"],
            "ScalarString2": ["string", "DevString", "-125"],
            "ScalarString3": ["string", "DevString", "-124"],
        }

        arrs["u"] = {
            "ScalarString1": ["string", "DevString", "-1"],
            "ScalarString2": ["string", "DevString", "-125"],
            "ScalarString3": ["string", "DevString", "-124"],
        }

        arrs["s"] = {
            "ScalarString1": ["string", "DevString", "bnle"],
            "ScalarString2": ["string", "DevString", "What"],
            "ScalarString3": ["string", "DevString", "Cos"],
        }

        arrs["b"] = {
            "ScalarString1": ["string", "DevString", "True"],
            "ScalarString2": ["string", "DevString", "False"],
            "ScalarString3": ["string", "DevString", "true"],
        }

        types = {}

        types["i"] = ["int", "int8", "int16", "int32", "int64"]
        types["u"] = ["uint", "uint8", "uint16", "uint32", "uint64"]
        types["f"] = ["float", "float16", "float32", "float64"]
        types["s"] = ["string"]
        types["b"] = ["bool"]

        ca = {
            "i": {"i": True, "u": True, "f": False, "s": False, "b": False},
            "u": {"i": True, "u": True, "f": False, "s": False, "b": False},
            "f": {"i": True, "u": True, "f": True, "s": False, "b": False},
            "s": {"i": True, "u": True, "f": True, "s": True, "b": True},
            "b": {"i": True, "u": True, "f": True, "s": True, "b": True}
        }

        for k in arrs:
            arr = arrs[k]
            for a in arr:
                data = {"rank": "SCALAR",
                        "value": arr[a][2],
                        "tangoDType": arr[a][1],
                        "shape": [1, 0],
                        "encoding": None,
                        "decoders": None}
                el = DataHolder(**data)

                self.assertTrue(isinstance(el, object))
                self.assertEqual(el.format, data["rank"])
                self.assertEqual(el.value, data["value"])
                self.assertEqual(el.tangoDType, data["tangoDType"])
                self.assertEqual(el.shape, data["shape"])
                self.assertEqual(el.encoding, data["encoding"])
                self.assertEqual(el.decoders, data["decoders"])
                for c in ca:
                    for it in types[c]:
                        if ca[c][k] is True:
                            self.assertEqual(
                                NTP.convert[it](el.value), el.cast(it))
                        else:
                            self.myAssertRaise(ValueError, el.cast, it)

    # setup test
    # \brief It tests default settings
    def test_cast_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arrs = {}

        arrs["b"] = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0]],
        }

        arrs["i"] = {
            "SpectrumShort": ["int16", "DevShort", 3, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", 4, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 4, [1, 0]],
        }

        arrs["u"] = {
            "SpectrumUChar": ["uint8", "DevUChar", 3, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 2, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 3, [1, 0]],
        }

        arrs["f"] = {
            "SpectrumFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", 2.156673e+01, [1, 0],
                               1e-14],
        }

        arrs["s"] = {
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
            #  "State":[ "string", "DevState", tango._tango.DevState.ON],
        }

        types = {}

        types["i"] = {"int": 0, "int8": 0, "int16": 0, "int32": 0, "int64": 0}
        types["u"] = {"uint": 0, "uint8": 0,
                      "uint16": 0, "uint32": 0, "uint64": 0}
        types["f"] = {"float": 1e-5, "float16":
                      1e-01, "float32": 1e-5, "float64": 1e-14}
        types["s"] = {"string": 0}
        types["b"] = {"bool": 0}

        ca = {
            "i": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "u": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "f": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "s": {"i": True, "u": True, "f": True, "s": True, "b": True},
            "b": {"i": True, "u": True, "f": True, "s": True, "b": True}
        }

        for s in arrs:
            arr = arrs[s]
            for k in arr:

                if arr[k][1] != "DevBoolean":
                    mlen = [
                        self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                    arr[k][2] = [
                        arr[k][2] * self.__rnd.randint(1, 2)
                        for c in range(mlen[0])]
                else:
                    mlen = [self.__rnd.randint(1, 10)]
                    arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                                 for c in range(mlen[0])]

                arr[k][3] = [mlen[0], 0]

        for k in arrs:
            arr = arrs[k]
            for a in arr:
                data = {"rank": "SPECTRUM",
                        "value": arr[a][2],
                        "tangoDType": arr[a][1],
                        "shape": arr[a][3],
                        "encoding": None,
                        "decoders": None}
                el = DataHolder(**data)

                self.assertTrue(isinstance(el, object))
                self.assertEqual(el.format, data["rank"])
                self.assertEqual(el.value, data["value"])
                self.assertEqual(el.tangoDType, data["tangoDType"])
                self.assertEqual(el.shape, data["shape"])
                self.assertEqual(el.encoding, data["encoding"])
                self.assertEqual(el.decoders, data["decoders"])
                for c in ca:
                    for it in types[c]:
                        if ca[c][k] is True:
                            elc = el.cast(it)
                            evalue = numpy.array(
                                [NTP.convert[it](e) for e in el.value],
                                dtype=nptype(it))
                            self.assertEqual(len(evalue), len(elc))
                            for i in range(len(evalue)):
                                if types[c][it]:
                                    self.assertTrue(
                                        abs(evalue[i] - elc[i]) <=
                                        types[c][it])
                                else:
                                    self.assertEqual(evalue[i], elc[i])
                        else:
                            self.myAssertRaise(Exception, el.cast, it)

    # setup test
    # \brief It tests default settings
    def test_cast_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arrs = {}

        arrs["b"] = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0]],
        }

        arrs["i"] = {
            "SpectrumShort": ["int16", "DevShort", 3, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", 4, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 5, [1, 0]],
        }

        arrs["u"] = {
            "SpectrumUChar": ["uint8", "DevUChar", 7, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 2, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 3, [1, 0]],
        }

        arrs["f"] = {
            "SpectrumFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", 2.456673e+01, [1, 0],
                               1e-14],
        }

        arrs["s"] = {
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
            #  "State":[ "string", "DevState", tango._tango.DevState.ON],
        }

        types = {}

        types["i"] = {"int": 0, "int8": 0, "int16": 0, "int32": 0, "int64": 0}
        types["u"] = {"uint": 0, "uint8": 0,
                      "uint16": 0, "uint32": 0, "uint64": 0}
        types["f"] = {"float": 1e-5, "float16":
                      1e-01, "float32": 1e-5, "float64": 1e-14}
        types["s"] = {"string": 0}
        types["b"] = {"bool": 0}

        ca = {
            "i": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "u": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "f": {"i": True, "u": True, "f": True, "s": False, "b": True},
            "s": {"i": True, "u": True, "f": True, "s": True, "b": True},
            "b": {"i": True, "u": True, "f": True, "s": True, "b": True}
        }

        for s in arrs:
            arr = arrs[s]

            for k in arr:

                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                if arr[k][1] != "DevBoolean":
                    arr[k][2] = [[arr[k][2] * self.__rnd.randint(0, 2)
                                  for r in range(mlen[1])]
                                 for c in range(mlen[0])]
                else:
                    mlen = [
                        self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                    if arr[k][1] == 'DevBoolean':
                        arr[k][2] = [[(True if self.__rnd.randint(0, 1)
                                       else False)
                                      for c in range(mlen[1])]
                                     for r in range(mlen[0])]

                arr[k][3] = [mlen[0], mlen[1]]

        for k in arrs:
            arr = arrs[k]
            for a in arr:
                data = {"rank": "IMAGE",
                        "value": arr[a][2],
                        "tangoDType": arr[a][1],
                        "shape": arr[a][3],
                        "encoding": None,
                        "decoders": None}
                el = DataHolder(**data)

                self.assertTrue(isinstance(el, object))
                self.assertEqual(el.format, data["rank"])
                self.assertEqual(el.value, data["value"])
                self.assertEqual(el.tangoDType, data["tangoDType"])
                self.assertEqual(el.shape, data["shape"])
                self.assertEqual(el.encoding, data["encoding"])
                self.assertEqual(el.decoders, data["decoders"])
                for c in ca:
                    for it in types[c]:
                        if ca[c][k] is True:
                            elc = el.cast(it)
                            evalue = numpy.array([[NTP.convert[it](e)
                                                   for e in row]
                                                  for row in el.value],
                                                 dtype=nptype(it))

                            for i in range(len(evalue)):
                                self.assertEqual(len(evalue[i]), len(elc[i]))
                                for j in range(len(evalue[i])):
                                    if types[c][it]:
                                        self.assertTrue(
                                            abs(evalue[i][j] - elc[i][j]) <=
                                            types[c][it])
                                    else:
                                        self.assertEqual(
                                            evalue[i][j], elc[i][j])
                        else:
                            self.myAssertRaise(Exception, el.cast, it)


if __name__ == '__main__':
    unittest.main()
