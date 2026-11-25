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


try:
    import tango
except Exception:
    import PyTango as tango

try:
    import SimpleServerSetUp
except Exception:
    from . import SimpleServerSetUp

try:
    from ProxyHelper import ProxyHelper
except Exception:
    from .ProxyHelper import ProxyHelper


from nxswriter.TangoSource import TgMember
from nxswriter.DecoderPool import DecoderPool
from nxswriter.Errors import DataSourceSetupError

import threading

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test pool
class pool(object):

    def __init__(self):
        self.common = {}
        self.lock = threading.Lock()
        self.counter = 0


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


# test fixture
class TgMemberTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._simps = SimpleServerSetUp.SimpleServerSetUp()

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
            import time
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

        self._dbhost = None
        self._dbport = None

    # test starter
    # \brief Common set up
    def setUp(self):
        self._simps.setUp()
        # file handle
        self._dbhost = self._simps.dp.get_db_host()
        self._dbport = self._simps.dp.get_db_port()
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
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

        name = "myname%s" % self.__rnd.randint(0, 9)
        memberType = self.__rnd.choice(["attribute", "command", "property"])
        encoding = "encoding%s" % self.__rnd.randint(0, 9)

        mb = TgMember(name)
        self.assertEqual(mb.name, name)
        self.assertEqual(mb.memberType, 'attribute')
        self.assertEqual(mb.encoding, None)

        mb = TgMember(name, memberType)
        self.assertEqual(mb.name, name)
        self.assertEqual(mb.memberType, memberType)
        self.assertEqual(mb.encoding, None)

        mb = TgMember(name, memberType, encoding)
        self.assertEqual(mb.name, name)
        self.assertEqual(mb.memberType, memberType)
        self.assertEqual(mb.encoding, encoding)

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
    def checkData(self, data, format, value, ttype, shape,
                  encoding=None, decoders=None, error=0):
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
    def test_getData_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dname = 'writer'
        device = 'stestp09/testss/s1r228'
        # ctype = 'command'
        # atype = 'attribute'
        # host = self._dbhost
        # port = '10000'
        # encoding = 'UTF8'
        # group = 'common_motors'

        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))

        mb = TgMember(dname)
        mb.getData(proxy)
        self.myAssertRaise(DataSourceSetupError, mb.getValue)

        mb = TgMember('ScalarString')
        mb.getData(proxy)
        dt = mb.getValue()
        self.checkData(dt, "SCALAR", "Hello!", "DevString", [1, 0], None, None)

        mb = TgMember('ScalarString')
        mb.getData(proxy)
        dt = mb.getValue()
        self.checkData(dt, "SCALAR", "Hello!", "DevString", [1, 0], None, None)

        dt = mb.getValue()
        self.checkData(dt, "SCALAR", "Hello!", "DevString", [1, 0], None, None)

        mb.reset()
        self.myAssertRaise(DataSourceSetupError, mb.getValue)

    # getData test
    # \brief It tests default settings
    def test_getData_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))
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

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32', b'\xd2\x04\x00\x00.\x16\x00\x00-'
                 b'\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])

        arr = dict(arr1, **(arr2))

        for k in arr:

            mb = TgMember(k)
            mb.getData(proxy)
            dt = mb.getValue()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [1, 0], None, None,
                arr[k][3] if len(arr[k]) > 3 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                mb = TgMember(k, encoding=arr3[k][2][0])
                mb.getData(proxy)
                dp = DecoderPool()
                dt = mb.getValue(dp)
                self.checkData(dt, "SCALAR", arr3[k][
                               2], arr3[k][1], [1, 0], arr3[k][2][0], dp)

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
        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))

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

        for k in arr:

            mb = TgMember(k)
            mb.getData(proxy)
            dt = mb.getValue()

            self.checkData(
                dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3], None, None,
                arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))
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
                    arr[k][2] = [
                        [(True if self.__rnd.randint(0, 1) else False)
                         for c in range(mlen[1])] for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arr:
            mb = TgMember(k)
            mb.getData(proxy)
            dt = mb.getValue()
            self.checkData(
                dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3],
                None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_command(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))
        arr = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
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

        for k in arr:
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arr:
            mb = TgMember(k, "command")
            mb.getData(proxy)
            dt = mb.getValue()
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2],
                           [1, 0], None, None,
                           arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_dev_prop(self):
        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))

        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            # "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -123],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -124],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 234],
            # "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 234],
            # "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 23],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 12.234],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -2.456673e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        for k in arr:
            mb = TgMember(k, "property")
            mb.getData(proxy)
            dt = mb.getValue()
            self.checkData(
                dt, "SCALAR", str(self._simps.device_prop[k]),
                'DevString', [1, 0], None, None,
                arr[k][4] if len(arr[k]) > 4 else 0)
            # self.checkData(dt,"SCALAR", arr[k][3],arr[k][2],[1,0],None,None,
            # arr[k][4] if len(arr[k])>4 else 0)

    # getData test
    # \brief It tests default settings
    def test_setData_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))
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

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32', b'\xd2\x04\x00\x00.\x16\x00\x00-'
                 b'\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])

        arr = dict(arr1, **(arr2))

        for k in arr:

            mb = TgMember(k)
            da = proxy.read_attribute(k)
            mb.setData(da)
            dt = mb.getValue()
            self.checkData(dt, "SCALAR", arr[k][2], arr[k][1], [1, 0],
                           None, None, arr[k][3] if len(arr[k]) > 3 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                mb = TgMember(k, encoding=arr3[k][2][0])
                da = proxy.read_attribute(k)
                mb.setData(da)
                dp = DecoderPool()
                dt = mb.getValue(dp)
                self.checkData(dt, "SCALAR", arr3[k][
                               2], arr3[k][1], [1, 0], arr3[k][2][0], dp)

    # getData test
    # \brief It tests default settings
    def test_setData_spectrum(self):
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
            "SpectrumDouble": ["float64", "DevDouble", -2.456673e+02,
                               [1, 0], 1e-14],
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
        }
        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))

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

        for k in arr:

            mb = TgMember(k)
            da = proxy.read_attribute(k)
            mb.setData(da)
            dt = mb.getValue()

            self.checkData(
                dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3],
                None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_setData_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))
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
            "ImageDouble": ["float64", "DevDouble", -2.456673e+02,
                            [1, 0], 1e-14],
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
                    arr[k][2] = [
                        [(True if self.__rnd.randint(0, 1) else False)
                         for c in range(mlen[1])] for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arr:
            mb = TgMember(k)
            da = proxy.read_attribute(k)
            mb.setData(da)
            dt = mb.getValue()
            self.checkData(
                dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3],
                None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_setData_command(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))
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

        for k in arr:
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arr:
            mb = TgMember(k, "command")
            cd = proxy.command_query(k)
            da = proxy.command_inout(k)
            mb.setData(da, cd)
            dt = mb.getValue()
            self.checkData(
                dt, "SCALAR", arr[k][3], arr[k][2], [
                    1, 0], None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_setData_dev_prop(self):
        device = 'stestp09/testss/s1r228'
        proxy = tango.DeviceProxy(device)
        self.assertTrue(ProxyHelper.wait(proxy, 10000))

        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            # "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -123],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -124],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 234],
            # "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 234],
            # "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 23],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 12.234],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -2.456673e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        prop = self._simps.dp.get_property(list(arr.keys()))
        for k in prop.keys():
            prop[k] = [arr[k][3]]
        self._simps.dp.put_property(prop)

        for k in arr:
            mb = TgMember(k, "property")
            da = proxy.get_property(k)[k]
            mb.setData(da)
            dt = mb.getValue()
            self.checkData(
                dt, "SCALAR", str(arr[k][3]),
                'DevString', [1, 0], None, None,
                arr[k][4] if len(arr[k]) > 4 else 0)
# self.checkData(dt,"SCALAR", arr[k][3],arr[k][2],[1,0],None,None,
# arr[k][4] if len(arr[k])>4 else 0)


if __name__ == '__main__':
    unittest.main()
