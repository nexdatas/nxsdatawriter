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
# \file VDEOdecoderTest.py
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

from nxswriter.DecoderPool import VDEOdecoder


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class VDEOdecoderTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        self.__name = 'LIMA_VIDEO_IMAGE'

        self.__imageUChar = numpy.array([[2, 5], [3, 4]], dtype='uint8')

        self.__data = self.encodeImage(self.__imageUChar)
        self.__dtype = "uint8"
        self.__res = numpy.array([1234, 5678, 45, 345], dtype=numpy.uint32)

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)

        self.__rnd = random.Random(self.__seed)

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
        endian = ord(struct.pack('=H', 1).decode()[-1])
        hsize = struct.calcsize('!IHHqiiHHHH')
        header = struct.pack('!IHHqiiHHHH', 0x5644454f, version, mode, -1,
                             width, height, endian, hsize, 0, 0)
        fimage = image.flatten()
        #  for uint32 and python2.6 one gets the struct.pack bug:
        #  test/VDEOdecoderTest.py:90:
        # DeprecationWarning: struct integer overflow masking is deprecated
        #
        #   workaround for SystemError:
        #   Objects/longobject.c:336: bad argument to internal function
        ffimage = [int(im) for im in fimage] if mode == 2 else fimage
        ibuffer = struct.pack(formatID[mode] * fimage.size, *ffimage)

        return [format, header + ibuffer]

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        dc = VDEOdecoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

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

    # load method test
    # \brief It tests default settings
    def test_load(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        data = {
            "uint8": [None, 0xff, None],
            "uint16": [None, 0xffff, None],
            "uint32": [None, 0xffffffff, None],
            "uint64": [None, 0xffffffffffffffff, None]
        }

        for k in data:
            mlen = [self.__rnd.randint(1, 80), self.__rnd.randint(1, 64)]
            data[k][2] = numpy.array(
                [[self.__rnd.randint(0, data[k][1]) for p in range(mlen[1])]
                 for row in range(mlen[0])], dtype=k)
            data[k][0] = self.encodeImage(data[k][2])

        for k in data:
            dc = VDEOdecoder()
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, None)
            self.assertEqual(dc.dtype, None)

            self.assertEqual(dc.load(data[k][0]), None)
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, data[k][0][0])
            self.assertEqual(dc.dtype, k)

    # shape method test
    # \brief It tests default settings
    def test_shape(self):
        # fun = sys._getframe().f_code.co_name

        data = {
            "uint8": [None, 0xff, None],
            "uint16": [None, 0xffff, None],
            "uint32": [None, 0xffffffff, None],
            "uint64": [None, 0xffffffffffffffff, None]
        }

        for k in data:
            mlen = [self.__rnd.randint(1, 80), self.__rnd.randint(1, 64)]
            data[k][2] = numpy.array(
                [[self.__rnd.randint(0, data[k][1]) for p in range(mlen[1])]
                 for row in range(mlen[0])], dtype=k)
            data[k][0] = self.encodeImage(data[k][2])

        for k in data:
            dc = VDEOdecoder()
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, None)
            self.assertEqual(dc.dtype, None)

            self.assertEqual(dc.shape(), None)
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, None)
            self.assertEqual(dc.dtype, None)

            self.assertEqual(dc.load(data[k][0]), None)
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, data[k][0][0])
            self.assertEqual(dc.dtype, k)
            self.assertEqual(dc.shape(), list(data[k][2].shape))
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, data[k][0][0])
            self.assertEqual(dc.dtype, k)

    # decode method test
    # \brief It tests default settings
    def test_load_wrong_len(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        data = (
            'VIDEO_IMAGE',
            '\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00')

        dc = VDEOdecoder()

        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.dtype, None)
        self.assertEqual(dc.shape(), None)
        self.assertEqual(dc.format, None)

        self.myAssertRaise(struct.error, dc.load, data)

    # decode method test
    # \brief It tests default settings
    def test_decode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        data = {
            "uint8": [None, 0xff, None],
            "uint16": [None, 0xffff, None],
            "uint32": [None, 0xffffffff, None],
            "uint64": [None, 0xffffffffffffffff, None]
        }

        for k in data:
            mlen = [self.__rnd.randint(1, 80), self.__rnd.randint(1, 64)]
            data[k][2] = numpy.array(
                [[self.__rnd.randint(0, data[k][1]) for p in range(mlen[1])]
                 for row in range(mlen[0])], dtype=k)
            data[k][0] = self.encodeImage(data[k][2])

        for k in data:
            dc = VDEOdecoder()
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, None)
            self.assertEqual(dc.dtype, None)

            self.assertEqual(dc.load(data[k][0]), None)
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, data[k][0][0])
            self.assertEqual(dc.dtype, k)

            res = dc.decode()

            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, data[k][0][0])
            self.assertEqual(dc.dtype, k)
            self.assertEqual(dc.shape(), list(data[k][2].shape))
            self.assertEqual(dc.name, self.__name)
            self.assertEqual(dc.format, data[k][0][0])
            self.assertEqual(dc.dtype, k)
            self.assertEqual(len(res), len(data[k][2]))
            for i in range(len(res)):
                for j in range(len(res[i])):
                    self.assertEqual(res[i][j], data[k][2][i][j])


if __name__ == '__main__':
    unittest.main()
