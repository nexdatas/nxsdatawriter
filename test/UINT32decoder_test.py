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
# \file UINT32decoderTest.py
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

from nxswriter.DecoderPool import UINT32decoder


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class UINT32decoderTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        self.__name = 'UINT32'

        self.__data = (
            'INT32', '\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')
        self.__dtype = "uint32"
        self.__res = numpy.array([1234, 5678, 45, 345], dtype=numpy.uint32)

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
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

    # constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        dc = UINT32decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

    # load method test
    # \brief It tests default settings
    def test_load(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        # data = {}
        dc = UINT32decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

        self.assertEqual(dc.load(self.__data), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)

    # shape method test
    # \brief It tests default settings
    def test_shape(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        # data = {}
        dc = UINT32decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)
        self.assertEqual(dc.shape(), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

        self.assertEqual(dc.load(self.__data), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)
        self.assertEqual(dc.shape(), [len(self.__data[1]) / 4, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)

    # decode method test
    # \brief It tests default settings
    def test_decode_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        dc = UINT32decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)
        self.assertEqual(dc.shape(), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

        self.assertEqual(dc.decode(), None)

        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)
        self.assertEqual(dc.shape(), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

        self.assertEqual(dc.load(self.__data), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)
        self.assertEqual(dc.shape(), [len(self.__data[1]) / 4, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)

        res = dc.decode()

        self.assertEqual(len(res), len(self.__res))
        for i in range(len(res)):
            self.assertEqual(res[i], self.__res[i])

        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)
        self.assertEqual(dc.shape(), [len(self.__data[1]) / 4, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)

    # decode method test
    # \brief It tests default settings
    def test_load_wrong_len(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        data = ('INT32', '\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00')

        dc = UINT32decoder()

        self.myAssertRaise(ValueError, dc.load, data)

        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)
        self.assertEqual(dc.shape(), None)

    # decode method test
    # \brief It tests default settings
    def test_decode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = [[None, None]] * 20

        for a in arr:

            mlen = self.__rnd.randint(1, 10)
            lt = [self.__rnd.randint(0, 0xffffffff) for c in range(mlen)]
            a[1] = numpy.array(lt, dtype=numpy.uint32)
            a[0] = ('INT32', struct.pack('I' * mlen, *lt))

            dc = UINT32decoder()
            self.assertEqual(dc.load(a[0]), None)

            res = dc.decode()

            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, a[0][0])
            self.assertEqual(dc.dtype, self.__dtype)
            self.assertEqual(dc.shape(), [mlen, 0])
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, a[0][0])
            self.assertEqual(dc.dtype, self.__dtype)
            self.assertEqual(len(res), len(a[1]))
            for i in range(len(res)):
                self.assertEqual(res[i], a[1][i])


if __name__ == '__main__':
    unittest.main()
