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
# \file TangoSourceTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time

try:
    import tango
except Exception:
    import PyTango as tango

try:
    import SimpleServerSetUp
except Exception:
    from . import SimpleServerSetUp


from nxswriter.TangoSource import TgMember
from nxswriter.TangoSource import TgGroup
from nxswriter.DecoderPool import DecoderPool

import threading

import _thread as thread

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


#: (:obj:`bool`) tango bug #213 flag related to EncodedAttributes in python3
PYTG_BUG_213 = False
try:
    PYTGMAJOR, PYTGMINOR, PYTGPATCH = list(
        map(int, tango.__version__.split(".")[:3]))
    if PYTGMAJOR <= 9:
        if PYTGMAJOR == 9:
            if PYTGMINOR < 2:
                PYTG_BUG_213 = True
            elif PYTGMINOR == 2 and PYTGPATCH <= 4:
                PYTG_BUG_213 = True
        else:
            PYTG_BUG_213 = True
except Exception:
    pass


# test pool
class pool(object):

    def __init__(self):
        self.common = {}
        self.lock = threading.Lock()
        self.counter = 0


# test fixture
class TgGroupTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._simps = SimpleServerSetUp.SimpleServerSetUp()
        self._simps2 = SimpleServerSetUp.SimpleServerSetUp(
            "stestp09/testss/s2r228", "S2")

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

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
        self._simps.setUp()
        self._simps2.setUp()
        # file handle
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        self._simps2.tearDown()
        self._simps.tearDown()

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

        counter = self.__rnd.randint(-2, 100)

        gr = TgGroup()
        self.assertEqual(gr.counter, 0)
        self.assertEqual(gr.devices, {})
        self.assertEqual(type(gr.lock), thread.LockType)

        gr = TgGroup(counter)
        self.assertEqual(gr.counter, counter)
        self.assertEqual(gr.devices, {})
        self.assertEqual(type(gr.lock), thread.LockType)

    # constructor test
    # \brief It tests default settings
    def test_getDevice(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        counter = self.__rnd.randint(-2, 100)

        gr = TgGroup(counter)
        self.assertEqual(gr.counter, counter)
        self.assertEqual(gr.devices, {})
        self.assertEqual(type(gr.lock), thread.LockType)

        name1 = "device%s" % self.__rnd.randint(1, 9)
        dv1 = gr.getDevice(name1)
        self.assertEqual(dv1.device, name1)

        name2 = "ddevice%s" % self.__rnd.randint(1, 9)
        dv2 = gr.getDevice(name2)
        self.assertEqual(dv2.device, name2)

        dv1 = gr.getDevice(name1)
        self.assertEqual(dv1.device, name1)

        dv2 = gr.getDevice(name2)
        self.assertEqual(dv2.device, name2)

    # Data check
    # \brief It check the source Data
    # \param data  tested data
    # \param format data format
    # \param value data value
    # \param ttype data Tango type
    # \param shape data shape
    # \param shape data shape
    # \param encoding data encoding
    # \param encoding data encoding
    # \param decoders data decoders
    # \param error data error
    def checkData(self, data, format, value, ttype, shape, encoding=None,
                  decoders=None, error=0):
        self.assertEqual(data["rank"], format)
        self.assertEqual(data["tangoDType"], ttype)
        self.assertEqual(data["shape"], shape)
        if encoding is not None:
            self.assertEqual(data["encoding"], encoding)
        if decoders is not None:
            self.assertEqual(data["decoders"], decoders)
        if format == 'SCALAR':
            if error:
                self.assertTrue(abs(data["value"] - value) <= error)
            else:
                self.assertEqual(data["value"], value)
        elif format == 'SPECTRUM':
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                if error:
                    self.assertTrue(abs(data["value"][i] - value[i]) <= error)
                else:
                    self.assertEqual(data["value"][i], value[i])
        else:
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                self.assertEqual(len(data["value"][i]), len(value[i]))
                for j in range(len(value[i])):
                    if error:
                        self.assertTrue(
                            abs(data["value"][i][j] - value[i][j]) <= error)
                    else:
                        self.assertEqual(data["value"][i][j], value[i][j])

    # getData test
    # \brief It tests default settings
    def test_getData_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
        }

        arr1b = {
            "ScalarBoolean": ["bool", "DevBoolean", False],
            "ScalarUChar": ["uint8", "DevUChar", 13],
            "ScalarShort": ["int16", "DevShort", -112],
            "ScalarUShort": ["uint16", "DevUShort", 2345],
            "ScalarLong": ["int64", "DevLong", -255],
            "ScalarULong": ["uint64", "DevULong", 123],
            "ScalarLong64": ["int64", "DevLong64", 214],
            "ScalarULong64": ["uint64", "DevULong64", 244465],
            "ScalarFloat": ["float32", "DevFloat", 11.123, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -1.414532e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyFalse"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        counter = self.__rnd.randint(-2, 10)

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])
        for k in arr1b:
            self._simps2.dp.write_attribute(k, arr1b[k][2])

        arr = dict(arr1, **(arr2))
        arrb = dict(arr1b, **(arr2))

        dvn = 'stestp09/testss/s1r228'
        dvn2 = 'stestp09/testss/s2r228'
        gr = TgGroup(-100)
        dv = gr.getDevice(dvn)
        dv2 = gr.getDevice(dvn2)

        flip = True
        for k in arr:
            mb = TgMember(k)
            if flip:
                dv.setMember(mb)
            else:
                dv2.setMember(mb)
            flip = not flip

        if not PYTG_BUG_213:
            flip = True
            for k in arr3:
                mb = TgMember(k, encoding=arr3[k][2][0])
                if flip:
                    dv.setMember(mb)
                else:
                    dv2.setMember(mb)
                flip = not flip

        print("FETCH %s" % counter)
        gr.getData(counter)
        print("FETCH END")

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1b[k][2])
        for k in arr1b:
            self._simps2.dp.write_attribute(k, arr1[k][2])

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", arr[k][2], arr[k][1], [1, 0], None,
                    None, arr[k][3] if len(arr[k]) > 3 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", arrb[k][2], arrb[k][1], [1, 0],
                    None, None, arrb[k][3] if len(arr[k]) > 3 else 0)
            flip = not flip

        gr.getData(counter)

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(dt, "SCALAR", arr[k][2], arr[k][1], [1, 0],
                               None, None, arr[k][3] if len(arr[k]) > 3 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", arrb[k][2], arrb[k][1], [1, 0], None, None,
                    arrb[k][3] if len(arr[k]) > 3 else 0)
            flip = not flip

        gr.getData(counter + 1)

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(dt, "SCALAR", arrb[k][2], arrb[k][1], [
                    1, 0], None, None, arrb[k][3] if len(arr[k]) > 3 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(dt, "SCALAR", arr[k][2], arr[k][1], [
                    1, 0], None, None, arr[k][3] if len(arr[k]) > 3 else 0)
            flip = not flip

        if not PYTG_BUG_213:
            dp = DecoderPool()
            flip = True
            for k in arr3:
                print(k)
                if flip:
                    print(gr.getDevice(dvn).members[k])
                    dt = (gr.getDevice(dvn).members[k]).getValue(dp)
                else:
                    print(gr.getDevice(dvn2).members[k])
                    dt = (gr.getDevice(dvn2).members[k]).getValue(dp)
                self.checkData(dt, "SCALAR", arr3[k][2], arr3[k][1],
                               [1, 0], arr3[k][2][0], dp)
                flip = not flip

    # getData test
    # \brief It tests default settings
    def test_getData_spectrum(self):
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

        arrb = {
            "SpectrumBoolean": ["bool", "DevBoolean", False, [1, 0]],
            "SpectrumUChar": ["uint8", "DevUChar", 22, [1, 0]],
            "SpectrumShort": ["int16", "DevShort", 13, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 2434, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -112, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 123, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 114, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 11, [1, 0]],
            "SpectrumFloat": ["float32", "DevFloat", 10.124, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", -1.133173e+02, [1, 0],
                               1e-14],
            "SpectrumString": ["string", "DevString", "MyFalse", [1, 0]],
        }

        counter = self.__rnd.randint(-2, 10)

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
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arrb:
            if arrb[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arrb[k][2] = [arrb[k][2] * self.__rnd.randint(0, 3)
                              for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arrb[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                              for c in range(mlen[0])]
            arrb[k][3] = [mlen[0], 0]
            self._simps2.dp.write_attribute(k, arrb[k][2])

        dvn = 'stestp09/testss/s1r228'
        dvn2 = 'stestp09/testss/s2r228'
        gr = TgGroup(-100)
        dv = gr.getDevice(dvn)
        dv2 = gr.getDevice(dvn2)

        flip = True
        for k in arr:
            mb = TgMember(k)
            if flip:
                dv.setMember(mb)
            else:
                dv2.setMember(mb)
            flip = not flip

        gr.getData(counter)

        for k in arrb:
            self._simps.dp.write_attribute(k, arrb[k][2])
        for k in arr:
            self._simps2.dp.write_attribute(k, arr[k][2])

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3], None,
                    None, arr[k][4] if len(arr[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SPECTRUM", arrb[k][2], arrb[k][1], arrb[k][3],
                    None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            flip = not flip

        gr.getData(counter)

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3], None,
                    None, arr[k][4] if len(arr[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SPECTRUM", arrb[k][2], arrb[k][1], arrb[k][3],
                    None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            flip = not flip

        gr.getData(counter + 1)

        flip = True
        for k in arrb:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "SPECTRUM", arrb[k][2], arrb[k][1], arrb[k][3],
                    None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3], None,
                    None, arr[k][4] if len(arr[k]) > 4 else 0)
            flip = not flip

    # getData test
    # \brief It tests default settings
    def test_getData_image(self):
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

        arrb = {
            "ImageBoolean": ["bool", "DevBoolean", False, [1, 0]],
            "ImageUChar": ["uint8", "DevUChar", 12, [1, 0]],
            "ImageShort": ["int16", "DevShort", -245, [1, 0]],
            "ImageUShort": ["uint16", "DevUShort", 1452, [1, 0]],
            "ImageLong": ["int64", "DevLong", -235, [1, 0]],
            "ImageULong": ["uint64", "DevULong", 123, [1, 0]],
            "ImageLong64": ["int64", "DevLong64", 123, [1, 0]],
            "ImageULong64": ["uint64", "DevULong64", 19, [1, 0]],
            "ImageFloat": ["float32", "DevFloat", 1.2324, [1, 0], 1e-5],
            "ImageDouble": ["float64", "DevDouble", -1.423473e+02, [1, 0],
                            1e-14],
            "ImageString": ["string", "DevString", "MyTFAL", [1, 0]],
        }

        counter = self.__rnd.randint(-2, 10)

        for k in arr:
            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[
                    arr[k][2] * self.__rnd.randint(0, 3)
                    for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [[
                        (True if self.__rnd.randint(0, 1) else False)
                        for c in range(mlen[1])] for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arrb:
            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arrb[k][1] != "DevBoolean":
                arrb[k][2] = [[
                    arrb[k][2] * self.__rnd.randint(0, 3)
                    for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arrb[k][1] == 'DevBoolean':
                    arrb[k][2] = [[
                        (True if self.__rnd.randint(0, 1) else False)
                        for c in range(mlen[1])] for r in range(mlen[0])]

            arrb[k][3] = [mlen[0], mlen[1]]
            self._simps2.dp.write_attribute(k, arrb[k][2])

        dvn = 'stestp09/testss/s1r228'
        dvn2 = 'stestp09/testss/s2r228'
        gr = TgGroup(-10)
        dv = gr.getDevice(dvn)
        dv2 = gr.getDevice(dvn2)

        flip = True
        for k in arr:
            mb = TgMember(k)
            if flip:
                dv.setMember(mb)
            else:
                dv2.setMember(mb)
            flip = not flip

        gr.getData(counter)

        for k in arrb:
            self._simps.dp.write_attribute(k, arrb[k][2])
        for k in arr:
            self._simps2.dp.write_attribute(k, arr[k][2])

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3], None,
                    None, arr[k][4] if len(arr[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "IMAGE", arrb[k][2], arrb[k][1], arrb[k][3], None,
                    None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            flip = not flip

        gr.getData(counter)

        flip = True
        for k in arrb:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3], None,
                    None, arr[k][4] if len(arr[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "IMAGE", arrb[k][2], arrb[k][1], arrb[k][3], None,
                    None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            flip = not flip

        gr.getData(counter + 1)

        flip = True
        for k in arrb:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "IMAGE", arrb[k][2], arrb[k][1], arrb[k][3], None,
                    None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3], None,
                    None, arr[k][4] if len(arr[k]) > 4 else 0)
            flip = not flip

    # getData test
    # \brief It tests default settings
    def test_getData_command(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #  "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "GetShort": ["ScalarShort", "int16", "DevShort", -123],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "GetLong": ["ScalarLong", "int64", "DevLong", -124],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 234],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 234],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 23],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 12.234, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -2.456673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        arrb = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #   "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "GetShort": ["ScalarShort", "int16", "DevShort", -121],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1223],
            "GetLong": ["ScalarLong", "int64", "DevLong", -344],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 124],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 234],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 1345],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 2.123, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -1.1233213e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyFAADSD"],
        }

        counter = self.__rnd.randint(-2, 10)

        for k in arr:
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arrb[k][0], arrb[k][3])

        dvn = 'stestp09/testss/s1r228'
        dvn2 = 'stestp09/testss/s2r228'
        gr = TgGroup(-100)
        dv = gr.getDevice(dvn)
        dv2 = gr.getDevice(dvn2)

        flip = True
        for k in arr:
            mb = TgMember(k, "command")
            if flip:
                dv.setMember(mb)
            else:
                dv2.setMember(mb)
            flip = not flip

        gr.getData(counter)

        for k in arr:
            self._simps.dp.write_attribute(arrb[k][0], arrb[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arr[k][0], arr[k][3])

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", arr[k][3], arr[k][2], [1, 0], None, None,
                    arr[k][4] if len(arr[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0],
                    None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            flip = not flip

        gr.getData(counter)

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [1, 0],
                               None, None, arr[k][4] if len(arr[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0], None,
                    None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            flip = not flip

        gr.getData(counter + 1)

        flip = True
        for k in arrb:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0],
                    None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", arr[k][3], arr[k][2], [1, 0],
                    None, None, arr[k][4] if len(arr[k]) > 4 else 0)
            flip = not flip

    # getData test
    # \brief It tests default settings
    def test_getData_dev_prop(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #   "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -123],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -124],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 234],
            #   "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 234],
            #   "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 23],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat",
                            12.234],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -2.456673e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        arrb = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", False],
            #       "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 21],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -113],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1232],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -112],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 221],
            #   "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 414],
            #   "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 12],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat",
                            11.111],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -1.111673e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "Mywrew"],
        }

        counter = self.__rnd.randint(-2, 10)

        for k in arr:
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arrb[k][0], arrb[k][3])

        dvn = 'stestp09/testss/s1r228'
        dvn2 = 'stestp09/testss/s2r228'
        gr = TgGroup(-100)
        dv = gr.getDevice(dvn)
        dv2 = gr.getDevice(dvn2)

        flip = True
        for k in arr:
            mb = TgMember(k, "property")
            if flip:
                dv.setMember(mb)
            else:
                dv2.setMember(mb)
            flip = not flip

        gr.getData(counter)

        for k in arr:
            self._simps.dp.write_attribute(arrb[k][0], arrb[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arr[k][0], arr[k][3])

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(dt, "SCALAR", str(self._simps.device_prop[k]),
                               'DevString', [1, 0], None, None,
                               arr[k][4] if len(arr[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(dt, "SCALAR", str(self._simps.device_prop[k]),
                               'DevString', [1, 0], None, None,
                               arrb[k][4] if len(arrb[k]) > 4 else 0)
            flip = not flip

        gr.getData(counter)

        flip = True
        for k in arr:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", str(self._simps.device_prop[k]),
                    'DevString', [1, 0], None, None, arr[k][4]
                    if len(arrb[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", str(self._simps.device_prop[k]),
                    'DevString', [1, 0], None, None, arrb[k][4]
                    if len(arr[k]) > 4 else 0)
            flip = not flip

        gr.getData(counter + 1)

        flip = True
        for k in arrb:
            if flip:
                dt = (gr.getDevice(dvn).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", str(self._simps.device_prop[k]),
                    'DevString', [1, 0], None, None, arrb[k][4]
                    if len(arrb[k]) > 4 else 0)
            else:
                dt = (gr.getDevice(dvn2).members[k]).getValue()
                self.checkData(
                    dt, "SCALAR", str(self._simps.device_prop[k]),
                    'DevString', [1, 0], None, None, arr[k][4]
                    if len(arr[k]) > 4 else 0)
            flip = not flip


if __name__ == '__main__':
    unittest.main()
