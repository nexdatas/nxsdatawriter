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
# \file NTPTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct
import random
import binascii
import numpy


from nxswriter.Types import NTP
from nxswriter.Types import Converters

#

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class NTPTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "doc"
        self._fname = "test.h5"
        self._nxDoc = None
        self._eDoc = None
        self._fattrs = {"short_name": "test", "units": "m"}
        self._gname = "testDoc"
        self._gtype = "NXentry"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        # map of Python:Tango types
        self._pTt = {
            "int": "DevLong64", "long": "DevLong64", "float": "DevDouble",
            "str": "DevString", "unicode": "DevString",
            "bool": "DevBoolean"}

        # map of Numpy:Tango types
        self._npTt = {
            "int": "DevLong64", "int64": "DevLong64", "int32": "DevLong",
            "int16": "DevShort", "int8": "DevUChar", "uint": "DevULong64",
            "uint64": "DevULong64", "uint32": "DevULong",
            "uint16": "DevUShort", "uint8": "DevUChar", "float": "DevDouble",
            "float64": "DevDouble",
            "float32": "DevFloat", "float16": "DevFloat",
            "string": "DevString", "bool": "DevBoolean"}

        # map of NEXUS : numpy types
        self._nTnp = {
            "NX_FLOAT32": "float32", "NX_FLOAT64": "float64",
            "NX_FLOAT": "float64",
            "NX_NUMBER": "float64", "NX_INT": "int64", "NX_INT64": "int64",
            "NX_INT32": "int32", "NX_INT16": "int16", "NX_INT8": "int8",
            "NX_UINT64": "uint64", "NX_UINT32": "uint32",
            "NX_UINT16": "uint16", "NX_UINT8": "uint8",
            "NX_UINT": "uint64", "NX_POSINT": "uint64",
            "NX_DATE_TIME": "string", "ISO8601": "string",
            "NX_CHAR": "string", "NX_BOOLEAN": "bool"}

        # map of type : converting function
        self._convert = {
            "float16": float, "float32": float, "float64": float,
            "float": float, "int64": int, "int32": int,
            "int16": int, "int8": int, "int": int, "uint64": int,
            "uint32": int, "uint16": int,
            "uint8": int, "uint": int, "string": str,
            "bool": Converters.toBool}

        # map of tag attribute types
        self._aTn = {
            "signal": "NX_INT", "axis": "NX_INT", "primary": "NX_INT32",
            "offset": "NX_INT",
            "stride": "NX_INT", "file_time": "NX_DATE_TIME",
            "file_update_time": "NX_DATE_TIME", "restricts": "NX_INT",
            "ignoreExtraGroups": "NX_BOOLEAN",
            "ignoreExtraFields": "NX_BOOLEAN",
            "ignoreExtraAttributes": "NX_BOOLEAN", "minOccus": "NX_INT",
            "maxOccus": "NX_INT"
        }

        # map of vector tag attribute types
        self._aTnv = {"vector": "NX_FLOAT"}

        # map of rank : data format
        self._rTf = {0: "SCALAR", 1: "SPECTRUM", 2: "IMAGE", 3: "VERTEX"}

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
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

    # dictionary test
    # \brief It tests default settings
    def test_dict(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = NTP()
        self.assertTrue(isinstance(el, object))

        for it in self._pTt:
            self.assertEqual(el.pTt[it], self._pTt[it])
            self.assertEqual(NTP.pTt[it], self._pTt[it])

        for it in self._npTt:
            self.assertEqual(el.pTt[it], self._npTt[it])
            self.assertEqual(NTP.pTt[it], self._npTt[it])

        for it in self._nTnp:
            self.assertEqual(el.nTnp[it], self._nTnp[it])
            self.assertEqual(NTP.nTnp[it], self._nTnp[it])

        for it in self._convert:
            self.assertEqual(el.convert[it], self._convert[it])
            self.assertEqual(NTP.convert[it], self._convert[it])

        for it in self._aTn:
            self.assertEqual(el.aTn[it], self._aTn[it])
            self.assertEqual(NTP.aTn[it], self._aTn[it])

        for it in self._aTnv:
            self.assertEqual(el.aTnv[it], self._aTnv[it])
            self.assertEqual(NTP.aTnv[it], self._aTnv[it])

        for it in self._rTf:
            self.assertEqual(el.rTf[it], self._rTf[it])
            self.assertEqual(NTP.rTf[it], self._rTf[it])

    # arrayRank test
    # \brief It tests default settings
    def test_arrayRank(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        mlen = [self.__rnd.randint(1, 100), self.__rnd.randint(
            1, 50), self.__rnd.randint(1, 20), self.__rnd.randint(2, 10)]
        arr = [
            [12, 0],
            [[], 1],
            [[[]], 2],
            [[[[]]], 3],
            [[[[[]]]], 4],
            [[0], 1],
            [[[0]], 2],
            [[[[0]]], 3],
            [[[[[0]]]], 4],
            [[-0.243], 1],
            [[1] * mlen[0], 1],
            [[-2.1233] * mlen[1], 1],
            [[-2.1233 * self.__rnd.randint(2, 100)
              for c in range(mlen[2])], 1],
            [[[123.123] * mlen[0]], 2],
            [[[13.123]] * mlen[1], 2],
            [[[13.123 * self.__rnd.randint(2, 100)
              for c in range(mlen[2])]], 2],
            [[[13.123 * self.__rnd.randint(2, 100)]
              for c in range(mlen[2])], 2],
            [[[13.123 * self.__rnd.randint(2, 100) for c in range(mlen[1])]
              for cc in range(mlen[2])], 2],
            [[[[123.123] * mlen[0]]], 3],
            [[[[123.123]] * mlen[0]], 3],
            [[[[13.123]]] * mlen[1], 3],
            [[[[13.123 * self.__rnd.randint(2, 100)
              for c in range(mlen[2])]]], 3],
            [[[[13.123 * self.__rnd.randint(2, 100)]
              for c in range(mlen[2])]], 3],
            [[[[13.123 * self.__rnd.randint(2, 100)]]
              for c in range(mlen[2])], 3],
            [[[[13.123 * self.__rnd.randint(2, 100) for c in range(mlen[1])]
              for cc in range(mlen[2])]], 3],
            [[[[13.123 * self.__rnd.randint(2, 100) for c in range(mlen[1])]]
              for cc in range(mlen[2])], 3],
            [[[[13.123 * self.__rnd.randint(2, 100)
                for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccC in range(mlen[2])], 3],
            [[[[[123.123] * mlen[0]]]], 4],
            [[[[[123.123]] * mlen[0]]], 4],
            [[[[[123.123]]] * mlen[0]], 4],
            [[[[[13.123]]]] * mlen[1], 4],
            [[[[[13.123 * self.__rnd.randint(
                2, 100) for c in range(mlen[2])]]]],
             4],
            [[[[[13.123 * self.__rnd.randint(2, 100)]
              for c in range(mlen[2])]]], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100)]]
              for c in range(mlen[2])]], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100)]]]
              for c in range(mlen[2])], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100) for c in range(mlen[1])]
              for cc in range(mlen[2])]]], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100) for c in range(mlen[1])]]
              for cc in range(mlen[2])]], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100)]
                for c in range(mlen[1])]]
              for cc in range(mlen[2])], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]
               for ccc in range(mlen[3])]], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]]
              for ccc in range(mlen[3])], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccc in range(mlen[3])] for cccc in range(mlen[0])], 4],
        ]
        el = NTP()
        for a in arr:

            self.assertEqual(el.arrayRank(a[0]), a[1])
            self.assertEqual(el.arrayRank(numpy.array(a[0])), a[1])

    # arrayRank test
    # \brief It tests default settings
    def test_arrayRankRShape(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        mlen = [self.__rnd.randint(2, 100), self.__rnd.randint(
            2, 50), self.__rnd.randint(2, 20), self.__rnd.randint(2, 10)]
        arr = [
            [12, 0, [], "int"],
            [[], 1, [0], None],
            [[[]], 2, [0, 1], None],
            [[[[]]], 3, [0, 1, 1], None],
            [[[[[]]]], 4, [0, 1, 1, 1], None],
            [[0], 1, [1], "int"],
            [[[1.0]], 2, [1, 1], "float"],
            [[[["str"]]], 3, [1, 1, 1], "str"],
            [[[[[True]]]], 4, [1, 1, 1, 1], "bool"],
            [[False], 1, [1], "bool"],
            [[1] * mlen[0], 1, [mlen[0]], "int"],
            [["sdf"] * mlen[1], 1, [mlen[1]], "str"],
            [[-2.1233 * self.__rnd.randint(2, 100)
              for c in range(
              mlen[2])], 1, [mlen[2]], "float"],
            [[[123] * mlen[0]], 2, [mlen[0], 1], "int"],
            [[["text"]] * mlen[1], 2, [1, mlen[1]], "str"],
            [[[13.12 * self.__rnd.randint(2, 100)
              for c in range(
               mlen[
                   2])]], 2, [
                       mlen[2], 1], "float"],
            [[[13 * self.__rnd.randint(2, 100)]
              for c in range(
                mlen[2])], 2, [1, mlen[2]], "int"],
            [[["a" * self.__rnd.randint(2, 100)
               for c in range(mlen[1])] for cc in range(mlen[2])], 2,
             [mlen[1], mlen[2]], "str"],
            [[[[True] * mlen[0]]], 3, [mlen[0], 1, 1], "bool"],
            [[[[123.123]] * mlen[0]], 3, [1, mlen[0], 1], "float"],
            [[[["as"]]] * mlen[1], 3, [1, 1, mlen[1]], "str"],
            [[[[13 * self.__rnd.randint(2, 100)
                for c in range(mlen[2])]]], 3, [
             mlen[2], 1, 1], "int"],
            [[[[13.123 * self.__rnd.randint(2, 100)]
               for c in range(mlen[2])]], 3, [1, mlen[2], 1], "float"],
            [[[["ta" * self.__rnd.randint(1, 100)]]
              for c in range(mlen[2])], 3, [1, 1, mlen[2]], "str"],
            [[[[13.123 * self.__rnd.randint(2, 100)
                for c in range(mlen[1])]
               for cc in range(mlen[2])]], 3,
             [mlen[1], mlen[2], 1],
             "float"],
            [[[[13 * self.__rnd.randint(2, 100)
                for c in range(mlen[1])]]
              for cc in range(mlen[2])], 3,
             [mlen[1], 1, mlen[2]], "int"],
            [[[["w" * self.__rnd.randint(2, 100)
                for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccC in range(
                mlen[3])], 3, [mlen[1], mlen[2], mlen[3]], "str"],
            [[[[[False] * mlen[0]]]], 4, [mlen[0], 1, 1, 1], "bool"],
            [[[[[123.123]] * mlen[0]]], 4, [1, mlen[0], 1, 1], "float"],
            [[[[[123]]] * mlen[0]], 4, [1, 1, mlen[0], 1], "int"],
            [[[[["bleble"]]]] * mlen[1], 4, [1, 1, 1, mlen[1]], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[2])]]]], 4, [mlen[2], 1, 1, 1], "float"],
            [[[[[13 * self.__rnd.randint(2, 100)]
                for c in range(mlen[2])]]], 4, [1, mlen[2], 1, 1], "int"],
            [[[[["1" * self.__rnd.randint(2, 100)]]
               for c in range(mlen[2])]], 4, [1, 1, mlen[2], 1], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)]]]
              for c in range(mlen[2])], 4, [1, 1, 1, mlen[2]], "float"],
            [[[[[13 * self.__rnd.randint(
                2, 100) for c in range(
                    mlen[1])] for cc in range(mlen[2])]]], 4,
             [mlen[1], mlen[2], 1, 1], "int"],
            [[[[["t" * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]], 4,
             [mlen[1], 1, mlen[2], 1], "str"],
            [[[[[13.123 * self.__rnd.randint(
                2, 100)] for c in range(
                    mlen[1])]] for cc in range(mlen[2])], 4,
             [1, mlen[1], 1, mlen[2]], "float"],
            [[[[[13 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]
               for ccc in range(mlen[3])]], 4,
             [mlen[1], mlen[2], mlen[3], 1], "int"],
            [[[[["13" * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]]
              for ccc in range(mlen[3])], 4,
             [mlen[1], mlen[2], 1, mlen[3]], "str"],
            [[[[[13.00 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4,
             [mlen[1], 1, mlen[2], mlen[3]], "float"],
            [[[[[13 * self.__rnd.randint(2, 100)]
                for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4,
             [1, mlen[1], mlen[2], mlen[3]], "int"],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[0])] for cc in range(mlen[1])]
              for ccc in range(mlen[2])] for cccc in range(mlen[3])], 4,
             [mlen[0], mlen[1], mlen[2], mlen[3]], "float"],
        ]
        el = NTP()
        for a in arr:
            self.assertEqual(el.arrayRankRShape(a[0])[0], a[1])
            self.assertEqual(el.arrayRankRShape(a[0])[1], a[2])
#            self.assertEqual(el.arrayRankRShape(numpy.array(a[0]))[0], a[1])
#            self.assertEqual(el.arrayRankRShape(numpy.array(a[0]))[1], a[2])
            if a[3] is None:
                self.assertEqual(el.arrayRankRShape(a[0])[2], a[3])
                # self.assertEqual(el.arrayRankRShape(numpy.array(a[0]))[2],
                # a[3])
            else:
                self.assertEqual(el.arrayRankRShape(a[0])[2], a[3])
                # self.assertEqual(el.arrayRankRShape(numpy.array(a[0]))[2],
                # a[3])

    # arrayRank test
    # \brief It tests default settings
    def test_arrayRankRShape_np(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        mlen = [self.__rnd.randint(2, 100), self.__rnd.randint(
            2, 50), self.__rnd.randint(2, 20), self.__rnd.randint(2, 10)]
        arr = [
            [12, 0, [], "int64"],
            [[], 1, [0], None],
            [[[]], 2, [0, 1], None],
            [[[[]]], 3, [0, 1, 1], None],
            [[[[[]]]], 4, [0, 1, 1, 1], None],
            [[0], 1, [1], "int64"],
            [[[1.0]], 2, [1, 1], "float64"],
            [[[["str"]]], 3, [1, 1, 1], "str"],
            [[[[[True]]]], 4, [1, 1, 1, 1], "bool"],
            [[False], 1, [1], "bool"],
            [[1] * mlen[0], 1, [mlen[0]], "int64"],
            [["sdf"] * mlen[1], 1, [mlen[1]], "str"],
            [[-2.1233 * self.__rnd.randint(2, 100)
              for c in range(
                mlen[2])], 1, [mlen[2]], "float64"],
            [[[123] * mlen[0]], 2, [mlen[0], 1], "int64"],
            [[["text"]] * mlen[1], 2, [1, mlen[1]], "str"],
            [[[13.12 * self.__rnd.randint(2, 100)
               for c in range(
                mlen[2])]], 2, [mlen[2], 1], "float64"],
            [[[13 * self.__rnd.randint(2, 100)]
              for c in range(
                mlen[2])], 2, [1, mlen[2]], "int64"],
            [[["a" * self.__rnd.randint(2, 100) for c in range(mlen[1])]
              for cc in range(mlen[2])], 2,
             [mlen[1], mlen[2]], "str"],
            [[[[True] * mlen[0]]], 3, [mlen[0], 1, 1], "bool"],
            [[[[123.123]] * mlen[0]], 3, [1, mlen[0], 1], "float64"],
            [[[["as"]]] * mlen[1], 3, [1, 1, mlen[1]], "str"],
            [[[[13 * self.__rnd.randint(2, 100)
                for c in range(mlen[2])]]], 3, [
                    mlen[2], 1, 1], "int64"],
            [[[[13.123 * self.__rnd.randint(2, 100)]
              for c in range(mlen[2])]], 3, [1, mlen[2], 1], "float64"],
            [[[["ta" * self.__rnd.randint(1, 100)]]
              for c in range(mlen[2])], 3, [1, 1, mlen[2]], "str"],
            [[[[13.123 * self.__rnd.randint(2, 100) for c in range(mlen[1])]
              for cc in range(mlen[2])]], 3, [mlen[1], mlen[2], 1],
             "float64"],
            [[[[13 * self.__rnd.randint(2, 100) for c in range(mlen[1])]]
              for cc in range(mlen[2])], 3, [mlen[1], 1, mlen[2]],
             "int64"],
            [[[["w" * self.__rnd.randint(2, 100)
                for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccC in range(
                mlen[3])], 3, [mlen[1], mlen[2], mlen[3]], "str"],
            [[[[[False] * mlen[0]]]], 4, [mlen[0], 1, 1, 1], "bool"],
            [[[[[123.123]] * mlen[0]]], 4, [1, mlen[0], 1, 1], "float64"],
            [[[[[123]]] * mlen[0]], 4, [1, 1, mlen[0], 1], "int64"],
            [[[[["bleble"]]]] * mlen[1], 4, [1, 1, 1, mlen[1]], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[2])]]]], 4,
             [mlen[2], 1, 1, 1], "float64"],
            [[[[[13 * self.__rnd.randint(2, 100)]
                for c in range(mlen[2])]]], 4, [1, mlen[2], 1, 1], "int64"],
            [[[[["1" * self.__rnd.randint(2, 100)]]
              for c in range(mlen[2])]], 4, [1, 1, mlen[2], 1], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)]]]
              for c in range(mlen[2])], 4, [1, 1, 1, mlen[2]], "float64"],
            [[[[[13 * self.__rnd.randint(2, 100) for c in range(
                mlen[1])] for cc in range(mlen[2])]]], 4,
             [mlen[1], mlen[2], 1, 1], "int64"],
            [[[[["t" * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]], 4,
             [mlen[1], 1, mlen[2], 1], "str"],
            [[[[[13.123 * self.__rnd.randint(
                2, 100)] for c in range(
                    mlen[1])]] for cc in range(mlen[2])], 4,
             [1, mlen[1], 1, mlen[2]], "float64"],
            [[[[[13 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]
               for ccc in range(mlen[3])]], 4,
             [mlen[1], mlen[2], mlen[3], 1], "int64"],
            [[[[["13" * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]]
              for ccc in range(mlen[3])], 4,
             [mlen[1], mlen[2], 1, mlen[3]], "str"],
            [[[[[13.00 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4,
             [mlen[1], 1, mlen[2], mlen[3]], "float64"],
            [[[[[13 * self.__rnd.randint(2, 100)]
                for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4,
             [1, mlen[1], mlen[2], mlen[3]], "int64"],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[0])] for cc in range(mlen[1])]
              for ccc in range(mlen[2])] for cccc in range(mlen[3])], 4,
             [mlen[0], mlen[1], mlen[2], mlen[3]], "float64"],
        ]
        el = NTP()
        for a in arr:
            self.assertEqual(el.arrayRankRShape(numpy.array(a[0]))[0], a[1])
            self.assertEqual(el.arrayRankRShape(numpy.array(a[0]))[1], a[2])
            if a[3] is None:
                self.assertEqual(
                    el.arrayRankRShape(numpy.array(a[0]))[2], a[3])
            else:
                self.assertEqual(
                    el.arrayRankRShape(numpy.array(a[0]))[2], a[3])

    # \brief It tests default settings
    def test_arrayRankShape(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        mlen = [self.__rnd.randint(2, 100), self.__rnd.randint(
            2, 50), self.__rnd.randint(2, 20), self.__rnd.randint(2, 10)]
        arr = [
            [12, 0, [], "int"],
            [[], 1, [0], None],
            [[[]], 2, [1, 0], None],
            [[[[]]], 3, [1, 1, 0], None],
            [[[[[]]]], 4, [1, 1, 1, 0], None],
            [[0], 1, [1], "int"],
            [[[1.0]], 2, [1, 1], "float"],
            [[[["str"]]], 3, [1, 1, 1], "str"],
            [[[[[True]]]], 4, [1, 1, 1, 1], "bool"],
            [[False], 1, [1], "bool"],
            [[1] * mlen[0], 1, [mlen[0]], "int"],
            [["sdf"] * mlen[1], 1, [mlen[1]], "str"],
            [[-2.1233 * self.__rnd.randint(2, 100)
              for c in range(
              mlen[2])], 1, [mlen[2]], "float"],
            [[[123] * mlen[0]], 2, [1, mlen[0]], "int"],
            [[["text"]] * mlen[1], 2, [mlen[1], 1], "str"],
            [[[13.12 * self.__rnd.randint(2, 100)
              for c in range(mlen[2])]], 2, [1, mlen[2]], "float"],
            [[[13 * self.__rnd.randint(2, 100)]
              for c in range(
              mlen[2])], 2, [mlen[2], 1], "int"],
            [[["a" * self.__rnd.randint(2, 100)
               for c in range(mlen[1])] for cc in range(mlen[2])], 2,
             [mlen[2], mlen[1]], "str"],
            [[[[True] * mlen[0]]], 3, [1, 1, mlen[0]], "bool"],
            [[[[123.123]] * mlen[0]], 3, [1, mlen[0], 1], "float"],
            [[[["as"]]] * mlen[1], 3, [mlen[1], 1, 1], "str"],
            [[[[13 * self.__rnd.randint(2, 100)
                for c in range(mlen[2])]]], 3, [
             1, 1, mlen[2]], "int"],
            [[[[13.123 * self.__rnd.randint(2, 100)]
              for c in range(mlen[2])]], 3, [1, mlen[2], 1], "float"],
            [[[["ta" * self.__rnd.randint(1, 100)]]
              for c in range(mlen[2])], 3, [mlen[2], 1, 1], "str"],
            [[[[13.123 * self.__rnd.randint(2, 100) for c in range(mlen[1])]
              for cc in range(mlen[2])]], 3, [1, mlen[2], mlen[1]],
             "float"],
            [[[[13 * self.__rnd.randint(2, 100) for c in range(mlen[1])]]
              for cc in range(mlen[2])], 3, [mlen[2], 1, mlen[1]], "int"],
            [[[["w" * self.__rnd.randint(2, 100) for c in range(mlen[1])]
               for cc in range(mlen[2])]
              for ccC in range(mlen[3])], 3, [mlen[3], mlen[2], mlen[1]],
             "str"],
            [[[[[False] * mlen[0]]]], 4, [1, 1, 1, mlen[0]], "bool"],
            [[[[[123.123]] * mlen[0]]], 4, [1, 1, mlen[0], 1], "float"],
            [[[[[123]]] * mlen[0]], 4, [1, mlen[0], 1, 1], "int"],
            [[[[["bleble"]]]] * mlen[1], 4, [mlen[1], 1, 1, 1], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[2])]]]], 4, [1, 1, 1, mlen[2]], "float"],
            [[[[[13 * self.__rnd.randint(2, 100)]
                for c in range(mlen[2])]]], 4, [1, 1, mlen[2], 1], "int"],
            [[[[["1" * self.__rnd.randint(2, 100)]]
              for c in range(mlen[2])]], 4, [1, mlen[2], 1, 1], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)]]]
              for c in range(mlen[2])], 4, [mlen[2], 1, 1, 1], "float"],
            [[[[[13 * self.__rnd.randint(
                2, 100) for c in range(mlen[1])]
                for cc in range(mlen[2])]]], 4,
             [1, 1, mlen[2], mlen[1]], "int"],
            [[[[["t" * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]], 4,
             [1, mlen[2], 1, mlen[1]], "str"],
            [[[[[13.123 * self.__rnd.randint(
                2, 100)] for c in range(
                    mlen[1])]] for cc in range(mlen[2])], 4,
             [mlen[2], 1, mlen[1], 1], "float"],
            [[[[[13 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]
               for ccc in range(mlen[3])]], 4,
             [1, mlen[3], mlen[2], mlen[1]], "int"],
            [[[[["13" * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]]
              for ccc in range(mlen[3])], 4,
             [mlen[3], 1, mlen[2], mlen[1]], "str"],
            [[[[[13.00 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4,
             [mlen[3], mlen[2], 1, mlen[1]], "float"],
            [[[[[13 * self.__rnd.randint(2, 100)]
                for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4,
             [mlen[3], mlen[2], mlen[1], 1], "int"],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[0])] for cc in range(mlen[1])]
              for ccc in range(mlen[2])] for cccc in range(mlen[3])], 4,
             [mlen[3], mlen[2], mlen[1], mlen[0]], "float"],
        ]
        el = NTP()
        for a in arr:
            self.assertEqual(el.arrayRankShape(a[0])[0], a[1])
            self.assertEqual(el.arrayRankShape(a[0])[1], a[2])

            if a[3] is None:
                self.assertEqual(el.arrayRankShape(a[0])[2], a[3])
            else:
                self.assertEqual(el.arrayRankShape(a[0])[2], a[3])

    # \brief It tests default settings
    def test_arrayRankShape_np(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        mlen = [self.__rnd.randint(2, 100), self.__rnd.randint(
            2, 50), self.__rnd.randint(2, 20), self.__rnd.randint(2, 10)]
        arr = [
            [12, 0, [], "int64"],
            [[], 1, [0], None],
            [[[]], 2, [1, 0], None],
            [[[[]]], 3, [1, 1, 0], None],
            [[[[[]]]], 4, [1, 1, 1, 0], None],
            [[0], 1, [1], "int64"],
            [[[1.0]], 2, [1, 1], "float64"],
            [[[["str"]]], 3, [1, 1, 1], "str"],
            [[[[[True]]]], 4, [1, 1, 1, 1], "bool"],
            [[False], 1, [1], "bool"],
            [[1] * mlen[0], 1, [mlen[0]], "int64"],
            [["sdf"] * mlen[1], 1, [mlen[1]], "str"],
            [[-2.1233 * self.__rnd.randint(2, 100)
              for c in range(mlen[2])], 1, [mlen[2]], "float64"],
            [[[123] * mlen[0]], 2, [1, mlen[0]], "int64"],
            [[["text"]] * mlen[1], 2, [mlen[1], 1], "str"],
            [[[13.12 * self.__rnd.randint(2, 100)
              for c in range(mlen[2])]], 2, [1, mlen[2]], "float64"],
            [[[13 * self.__rnd.randint(2, 100)]
              for c in range(mlen[2])], 2, [mlen[2], 1], "int64"],
            [[["a" * self.__rnd.randint(2, 100)
               for c in range(mlen[1])] for cc in range(mlen[2])], 2,
             [mlen[2], mlen[1]], "str"],
            [[[[True] * mlen[0]]], 3, [1, 1, mlen[0]], "bool"],
            [[[[123.123]] * mlen[0]], 3, [1, mlen[0], 1], "float64"],
            [[[["as"]]] * mlen[1], 3, [mlen[1], 1, 1], "str"],
            [[[[13 * self.__rnd.randint(2, 100)
                for c in range(mlen[2])]]], 3, [1, 1, mlen[2]], "int64"],
            [[[[13.123 * self.__rnd.randint(2, 100)]
              for c in range(mlen[2])]], 3, [1, mlen[2], 1], "float64"],
            [[[["ta" * self.__rnd.randint(1, 100)]]
              for c in range(mlen[2])], 3, [mlen[2], 1, 1], "str"],
            [[[[13.123 * self.__rnd.randint(2, 100) for c in range(mlen[1])]
               for cc in range(mlen[2])]], 3, [1, mlen[2], mlen[1]],
             "float64"],
            [[[[13 * self.__rnd.randint(2, 100) for c in range(mlen[1])]]
              for cc in range(mlen[2])], 3, [mlen[2], 1, mlen[1]],
             "int64"],
            [[[["w" * self.__rnd.randint(2, 100)
                for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccC in range(
                  mlen[3])], 3, [mlen[3], mlen[2], mlen[1]], "str"],
            [[[[[False] * mlen[0]]]], 4, [1, 1, 1, mlen[0]], "bool"],
            [[[[[123.123]] * mlen[0]]], 4, [1, 1, mlen[0], 1], "float64"],
            [[[[[123]]] * mlen[0]], 4, [1, mlen[0], 1, 1], "int64"],
            [[[[["bleble"]]]] * mlen[1], 4, [mlen[1], 1, 1, 1], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[2])]]]], 4,
             [1, 1, 1, mlen[2]], "float64"],
            [[[[[13 * self.__rnd.randint(2, 100)]
                for c in range(mlen[2])]]], 4, [1, 1, mlen[2], 1], "int64"],
            [[[[["1" * self.__rnd.randint(2, 100)]]
              for c in range(mlen[2])]], 4, [1, mlen[2], 1, 1], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)]]]
              for c in range(mlen[2])], 4, [mlen[2], 1, 1, 1], "float64"],
            [[[[[13 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]]], 4,
             [1, 1, mlen[2], mlen[1]], "int64"],
            [[[[["t" * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]], 4,
             [1, mlen[2], 1, mlen[1]], "str"],
            [[[[[13.123 * self.__rnd.randint(2, 100)]
                for c in range(mlen[1])]] for cc in range(mlen[2])], 4,
             [mlen[2], 1, mlen[1], 1], "float64"],
            [[[[[13 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]
               for ccc in range(mlen[3])]], 4,
             [1, mlen[3], mlen[2], mlen[1]], "int64"],
            [[[[["13" * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])] for cc in range(mlen[2])]]
              for ccc in range(mlen[3])], 4,
             [mlen[3], 1, mlen[2], mlen[1]], "str"],
            [[[[[13.00 * self.__rnd.randint(2, 100)
                 for c in range(mlen[1])]] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4,
             [mlen[3], mlen[2], 1, mlen[1]], "float64"],
            [[[[[13 * self.__rnd.randint(2, 100)]
                for c in range(mlen[1])] for cc in range(mlen[2])]
              for ccc in range(mlen[3])], 4,
             [mlen[3], mlen[2], mlen[1], 1], "int64"],
            [[[[[13.123 * self.__rnd.randint(2, 100)
                 for c in range(mlen[0])] for cc in range(mlen[1])]
              for ccc in range(mlen[2])] for cccc in range(mlen[3])], 4,
             [mlen[3], mlen[2], mlen[1], mlen[0]], "float64"],
        ]
        el = NTP()
        for a in arr:
            self.assertEqual(el.arrayRankShape(numpy.array(a[0]))[0], a[1])
            self.assertEqual(el.arrayRankShape(numpy.array(a[0]))[1], a[2])

            if a[3] is None:
                self.assertEqual(
                    el.arrayRankShape(numpy.array(a[0]))[2], a[3])
            else:
                self.assertEqual(
                    el.arrayRankShape(numpy.array(a[0]))[2], a[3])

    # arrayRank test
    # \brief It tests default settings
    def test_createArray_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arrs = {}

        arrs["b"] = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
        }

        arrs["i"] = {
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarLong": ["int64", "DevLong", -124],
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
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
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
                value = arr[a][2]
                for c in ca:
                    if ca[c][k] is True:
                        for it in types[c]:
                            res = NTP().createArray(value, NTP.convert[it])
                            self.assertEqual(NTP.convert[it](value), res)
                    res = NTP().createArray(value)
                    self.assertEqual(value, res)

    # setup test
    # \brief It tests default settings
    def test_createArray_scalar_from_string(self):
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
                value = arr[a][2]
                for c in ca:
                    for it in types[c]:
                        if ca[c][k] is True:
                            res = NTP().createArray(value, NTP.convert[it])
                            self.assertEqual(NTP.convert[it](value), res)
                    res = NTP().createArray(value)
                    self.assertEqual(value, res)

    # setup test
    # \brief It tests default settings
    def test_createArray_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arrs = {}

        arrs["b"] = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0]],
        }

        arrs["i"] = {
            "SpectrumShort": ["int16", "DevShort", -13, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -14, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", -24, [1, 0]],
        }

        arrs["u"] = {
            "SpectrumUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 2, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 3, [1, 0]],
        }

        arrs["f"] = {
            "SpectrumFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", -2.456673e+02, [1, 0],
                               1e-14],
        }

        arrs["s"] = {
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
            # "State":[ "string", "DevState", tango._tango.DevState.ON],
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
                    arr[k][2] = [arr[k][2] * self.__rnd.randint(1, 3)
                                 for c in range(mlen[0])]
                else:
                    mlen = [self.__rnd.randint(1, 10)]
                    arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                                 for c in range(mlen[0])]

                arr[k][3] = [mlen[0], 0]

        for k in arrs:
            arr = arrs[k]
            for a in arr:

                value = arr[a][2]

                for c in ca:
                    for it in types[c]:
                        if ca[c][k] is True:
                            evalue = [NTP.convert[it](e) for e in value]
                            elc = NTP().createArray(value, NTP.convert[it])
                            self.assertEqual(len(evalue), len(elc))
                            for i in range(len(evalue)):
                                if types[c][it]:
                                    self.assertTrue(
                                        abs(evalue[i] - elc[i]) <=
                                        types[c][it])
                                else:
                                    self.assertEqual(evalue[i], elc[i])
                evalue = [e for e in value]
                elc = NTP().createArray(value)
                self.assertEqual(len(evalue), len(elc))
                for i in range(len(evalue)):
                    if k != "s":
                        self.assertTrue(
                            abs(evalue[i] - elc[i]) <= types[c][it])
                    else:
                        self.assertEqual(evalue[i], elc[i])

    # setup test
    # \brief It tests default settings
    def test_createArray_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arrs = {}

        arrs["b"] = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0]],
        }

        arrs["i"] = {
            "SpectrumShort": ["int16", "DevShort", -13, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -14, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", -24, [1, 0]],
        }

        arrs["u"] = {
            "SpectrumUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 2, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 3, [1, 0]],
        }

        arrs["f"] = {
            "SpectrumFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", -2.456673e+02,
                               [1, 0], 1e-14],
        }

        arrs["s"] = {
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
            # "State":[ "string", "DevState", tango._tango.DevState.ON],
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
                    arr[k][2] = [[arr[k][2] * self.__rnd.randint(0, 3)
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
                value = arr[a][2]

                for c in ca:
                    for it in types[c]:
                        if ca[c][k] is True:
                            elc = NTP().createArray(value, NTP.convert[it])
                            evalue = [[NTP.convert[it](e)
                                       for e in row]
                                      for row in value]

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

                elc = NTP().createArray(value)
                evalue = [[e for e in row] for row in value]

                for i in range(len(evalue)):
                    self.assertEqual(len(evalue[i]), len(elc[i]))
                    for j in range(len(evalue[i])):
                        if k != 's':
                            self.assertTrue(
                                abs(evalue[i][j] - elc[i][j]) <= types[c][it])
                        else:
                            self.assertEqual(evalue[i][j], elc[i][j])


if __name__ == '__main__':
    unittest.main()
