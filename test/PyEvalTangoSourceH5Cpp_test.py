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
# \file PyEvalTangoSourceTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import json
import binascii
import time

try:
    import SimpleServerSetUp
except Exception:
    from . import SimpleServerSetUp

try:
    import tango
except Exception:
    import PyTango as tango

from nxswriter.DecoderPool import DecoderPool
from nxswriter.DataSources import DataSource
from nxswriter.PyEvalSource import PyEvalSource
from nxswriter.DataSourcePool import DataSourcePool
from nxswriter.Errors import DataSourceSetupError
from nxswriter.Types import Converters, NTP

from nxstools import h5cppwriter as H5CppWriter


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


# test fix
class PyEvalTangoSourceH5CppTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._simps = SimpleServerSetUp.SimpleServerSetUp()

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
        # file handle
        self._simps.setUp()
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
    def test_getData_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = 'ds.result = 123.2'
        script2 = 'ds.result = ds.inp'
        script3 = 'ds.res = ds.inp + ds.inp2'
        dp = DataSourcePool()

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup(
            "<datasource><datasource type='CLIENT' name='inp'/>"
            "<result>%s</result></datasource>" % script),
            None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 123.2, "DevDouble", [])

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup(
            "<datasource><datasource type='CLIENT' name='inp'/>"
            "<result>%s</result></datasource>" % script2),
            None)
        gjson = '{"data":{"inp":"21"}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)), None)
        self.myAssertRaise(DataSourceSetupError, ds.setDataSources, dp)

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='inp' />
  </datasource>
  <result>%s</result>
</datasource>
""" % script2), None)
        gjson = '{"data":{"inp":21}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)), None)
        self.assertEqual(ds.setDataSources(dp), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 21, "DevLong64", [])

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='CLIENT' name='inp2'>
    <record name='rinp2' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % script3), None)
        gjson = '{"data":{"rinp":21,"rinp2":41}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)), None)
        self.assertEqual(ds.setDataSources(dp), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 62, "DevLong64", [])

        dp = DataSourcePool(
            json.loads(
                '{"datasources":{"CL":"nxswriter.ClientSource.ClientSource"}}'
            ))

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CL' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='CLIENT' name='inp2'>
    <record name='rinp2' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % script3), None)
        gjson = '{"data":{"rinp":21.1}}'
        ljson = '{"data":{"rinp2":41}}'
        self.assertEqual(ds.setDataSources(dp), None)
        self.assertEqual(
            ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 62.1, "DevDouble", [])

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='CLIENT' name='inp2'>
    <record name='rinp2' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % script3), None)
        gjson = '{"data":{"rinp":21.1}}'
        ljson = '{"data":{"rinp2":41}}'
        self.assertEqual(ds.setDataSources(dp), None)
        self.assertEqual(
            ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 62.1, "DevDouble", [])

    # setup test
    # \brief It tests default settings
    def test_getData_global_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = """
try:
    ds.res = ds.inp + ds.inp2
    print("BNB")
except Exception:
    try:
       ds.res = unicode(ds.inp) + unicode(ds.inp2)
    except Exception:
        try:
            ds.res = str(unicode(ds.inp))+ ds.inp2
        except Exception:
            ds.res = ds.inp2

"""
        script = script.replace("unicode", "str")
        dsp = DataSourcePool()
        dcp = DecoderPool()

        arr = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234000206, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
        }

        arr3 = {
            "ScalarEncoded": [
                "string",
                "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('UINT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr:
            self._simps.dp.write_attribute(k, arr[k][2])

        carr = {
            "int": [1243, "SCALAR", "DevLong64", []],
            "long": [-10000000000000000000000003, "SCALAR", "DevLong64", []],
            "float": [-1.223e-01, "SCALAR", "DevDouble", []],
            "str": ['My String', "SCALAR", "DevString", []],
            "unicode": [u'12\xf8\xff\xf4', "SCALAR", "DevString", []],
            "bool": ['true', "SCALAR", "DevBoolean", []],
        }

        for a in carr:
            for a2 in arr:
                ds = PyEvalSource()
                self.assertTrue(isinstance(ds, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds.getData)
                self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='TANGO' name='inp2'>
    <device name='%s' />
    <record name='%s' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % (self._simps.dp.dev_name(), a2, script)), None)
                if carr[a][2] == "DevString":
                    gjson = '{"data":{"rinp":"%s"}}' % (carr[a][0])
                else:
                    gjson = '{"data":{"rinp":%s}}' % (carr[a][0])

                self.assertEqual(ds.setDataSources(dsp), None)
                self.assertEqual(ds.setJSON(json.loads(gjson)), None)
                dt = ds.getData()
                v1 = Converters.toBool(carr[a][0]) if carr[
                    a][2] == "DevBoolean" else carr[a][0]
                v2 = Converters.toBool(arr[a2][2]) if arr[
                    a2][1] == "DevBoolean" else arr[a2][2]
                try:
                    vv = v1 + v2
                    error = (arr[a2][3] if len(arr[a2]) > 3 else 0)
                except Exception:
                    error = 0
                    try:
                        vv = str(v1) + str(v2)
                    except Exception:
                        vv = str(str(v1)) + v2
                if not ((a in ['str', 'unicode'] and
                         a2 in ['ScalarFloat', 'ScalarDouble']) or
                        (a2 in ['ScalarString', 'ScalarUChar'] and
                         a in ['float'])):
                    self.checkData(
                        dt, carr[a][1], vv, NTP.pTt[type(vv).__name__],
                        carr[a][3], error=error)

            if not PYTG_BUG_213:
                for a2 in arr3:
                    ds = PyEvalSource()
                    self.assertTrue(isinstance(ds, DataSource))
                    self.myAssertRaise(DataSourceSetupError, ds.getData)
                    self.assertEqual(ds.setup("""
    <datasource>
      <datasource type='CLIENT' name='inp'>
        <record name='rinp' />
      </datasource>
      <datasource type='TANGO' name='inp2'>
        <device name='%s'  encoding='%s'/>
        <record name='%s' />
      </datasource>
      <result name='res'>%s</result>
    </datasource>
    """ % (self._simps.dp.dev_name(), arr3[a2][2][0], a2, script)), None)
                    if carr[a][2] == "DevString":
                        gjson = '{"data":{"rinp":"%s"}}' % (carr[a][0])
                    else:
                        gjson = '{"data":{"rinp":%s}}' % (carr[a][0])

                    self.assertEqual(ds.setJSON(json.loads(gjson)), None)
                    self.assertEqual(ds.setDataSources(dsp), None)
                    ds.setDecoders(dcp)
                    dt = ds.getData()
                    v1 = Converters.toBool(carr[a][0]) if carr[
                        a][2] == "DevBoolean" else carr[a][0]
                    ud = dcp.get(arr3[a2][2][0])
                    ud.load(arr3[a2][2])
                    v2 = ud.decode()
                    try:
                        vv = v1 + v2
                    except Exception:
                        try:
                            vv = str(v1) + str(v2)
                        except Exception:
                            try:
                                vv = str(str(v1)) + v2
                            except Exception:
                                vv = v2

                    if type(vv).__name__ == 'ndarray':
                        self.checkData(
                            dt, 'SPECTRUM', vv, NTP.pTt[type(vv[0]).__name__],
                            [len(vv)])
                    else:
                        self.checkData(
                            dt, carr[a][1], vv, NTP.pTt[type(vv).__name__],
                            carr[a][3])

    # setup test
    # \brief It tests default settings
    def test_getData_global_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = """
if type(ds.inp[0]) == type(ds.inp2[0]):
    ds.res = list(ds.inp) + list(ds.inp2)
else:
    ds.res = [unicode(i) for i in ds.inp] + [unicode(i2) for i2 in ds.inp2]
"""

        script = script.replace("unicode", "str")
        dsp = DataSourcePool()
        DecoderPool()

        carr = {
            "int": [1243, "SPECTRUM", "DevLong64", []],
            "long": [-10000000000000000000000003, "SPECTRUM", "DevLong64", []],
            "float": [-1.223e-01, "SPECTRUM", "DevDouble", []],
            "str": ['My String', "SPECTRUM", "DevString", []],
            "unicode": ["Hello", "SPECTRUM", "DevString", []],
            #   "unicode":[u'\x12\xf8\xff\xf4',"SPECTRUM","DevString",[]],
            "bool": ['true', "SPECTRUM", "DevBoolean", []],
        }

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
                arr[k][2] = [arr[k][2] * self.__rnd.randint(1, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0], 0]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in carr:

            if carr[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 3)]
                carr[k][0] = [
                    carr[k][0] * self.__rnd.randint(1, 3)
                    for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                carr[k][0] = [
                    ("true" if self.__rnd.randint(0, 1) else "false")
                    for c in range(mlen[0])]

            carr[k][3] = [mlen[0]]

        for k in carr:
            for k2 in arr:

                ds = PyEvalSource()
                self.assertTrue(isinstance(ds, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds.getData)
                self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='TANGO' name='inp2'>
    <device name='%s' />
    <record name='%s' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % (self._simps.dp.dev_name(), k2, script)), None)
                if carr[k][2] == "DevString":
                    gjson = '{"data":{"rinp":%s}}' % (
                        str(carr[k][0]).replace("'", "\""))
                elif carr[k][2] == "DevBoolean":
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + ''.join(
                            [a + ',' for a in carr[k][0]])[:-1] + "]")
                else:
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + ''.join(
                            [str(a) + ',' for a in carr[k][0]])[:-1] + "]")

                self.assertEqual(ds.setDataSources(dsp), None)
                self.assertEqual(ds.setJSON(json.loads(gjson)), None)
                dt = ds.getData()
                v1 = [Converters.toBool(a)
                      for a in carr[k][0]] if carr[k][2] == "DevBoolean" \
                    else carr[k][0]
                v2 = [Converters.toBool(a) for a in arr[k2][2]] if arr[
                    k2][1] == "DevBoolean" else arr[k2][2]
                if NTP.pTt[type(v1[0]).__name__] == str(type(v2[0]).__name__):
                    vv = v1 + v2
                    error = (arr[k2][4] if len(arr[k2]) > 4 else 0)
                else:
                    vv = [str(i) for i in v1] + [str(i2) for i2 in v2]
                    error = 0
                shape = [len(vv)]
                self.checkData(dt, carr[k][1], vv, NTP.pTt[
                               type(vv[0]).__name__], shape, error=error)

    # getData test
    # \brief It tests default settings with global json string
    def test_zzgetData_global_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = """
if type(ds.inp[0][0]) == type(ds.inp2[0][0]):
    ds.res = list(ds.inp) + list(ds.inp2)
else:
    ds.res = [[unicode(j) for j in i] for i in ds.inp] + \
        [[unicode(j2) for j2 in i2] for i2 in ds.inp2]
"""
        script = script.replace("unicode", "str")
        dsp = DataSourcePool()
        DecoderPool()

        carr = {
            "int": [1243, "IMAGE", "DevLong64", []],
            "long": [-10000000000000000000000003, "IMAGE", "DevLong64", []],
            "float": [-1.223e-01, "IMAGE", "DevDouble", []],
            "str": ['My String', "IMAGE", "DevString", []],
            "unicode": ["Hello", "IMAGE", "DevString", []],
            #            "unicode":[u'\x12\xf8\xff\xf4',"IMAGE","DevString",[]],
            "bool": ['true', "IMAGE", "DevBoolean", []],
        }

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

        nl2 = self.__rnd.randint(1, 10)
        for k in carr:
            if carr[k][2] != "DevBoolean":
                mlen = [
                    self.__rnd.randint(1, 10), nl2, self.__rnd.randint(0, 3)]
                carr[k][0] = [[
                    carr[k][0] * self.__rnd.randint(1, 3)
                    for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), nl2]
                if carr[k][2] == 'DevBoolean':
                    carr[k][0] = [[
                        ("true" if self.__rnd.randint(0, 1) else "false")
                        for c in range(mlen[1])] for r in range(mlen[0])]

            carr[k][3] = [mlen[0], mlen[1]]

        for k in arr:
            mlen = [self.__rnd.randint(1, 10), nl2, self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[arr[k][2] * self.__rnd.randint(1, 3)
                              for r in range(mlen[1])]
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), nl2]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [
                        [
                            (True if self.__rnd.randint(0, 1) else False)
                            for c in range(mlen[1])
                        ]
                        for r in range(mlen[0])
                    ]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in carr:
            for k2 in arr:

                ds = PyEvalSource()
                self.assertTrue(isinstance(ds, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds.getData)
                self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='TANGO' name='inp2'>
    <device name='%s' />
    <record name='%s' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % (self._simps.dp.dev_name(), k2, script)), None)

                if carr[k][2] == "DevString":
                    gjson = '{"data":{"rinp":%s}}' % (
                        str(carr[k][0]).replace("'", "\""))
                elif carr[k][2] == "DevBoolean":
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + "".join(['[' + ''.join(
                            [a + ',' for a in row])[:-1] + "],"
                            for row in carr[k][0]])[:-1] + ']')
                else:
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + "".join(['[' + ''.join(
                            [str(a) + ',' for a in row])[:-1] + "],"
                            for row in carr[k][0]])[:-1] + ']')

                self.assertEqual(ds.setDataSources(dsp), None)
                self.assertEqual(ds.setJSON(json.loads(gjson)), None)
                dt = ds.getData()
                v1 = [[Converters.toBool(a) for a in row]
                      for row in carr[k][0]] if carr[k][2] == "DevBoolean" \
                    else carr[k][0]
                v2 = [[Converters.toBool(a) for a in row]
                      for row in arr[k2][2]] if arr[k2][1] == "DevBoolean" \
                    else arr[k2][2]
                if NTP.pTt[type(v1[0][0]).__name__] == \
                   str(type(v2[0][0]).__name__):
                    vv = v1 + v2
                    error = (arr[k2][4] if len(arr[k2]) > 4 else 0)
                else:
                    vv = [[str(j) for j in i]
                          for i in v1] + [[str(j2) for j2 in i2]
                                          for i2 in v2]
                    error = 0
                shape = [len(vv), len(vv[0])]
                self.checkData(dt, carr[k][1], vv, NTP.pTt[
                               type(vv[0][0]).__name__], shape, error=error)

    # isValid test
    # \brief It tests default settings
    def ttest_isValid(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = PyEvalSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.isValid(), True)

    # getData test
    # \brief It tests default settings
    def test_getData_common_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = 'ds.result = 123.2'
        script2 = 'ds.result = ds.inp'
        script3 = """commonblock["myres"] = ds.inp + ds.inp2
ds.res = commonblock["myres"]
"""
        script4 = 'ds.res2 = commonblock["myres"]'
        dp = DataSourcePool()

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup(
            "<datasource><datasource type='CLIENT' name='inp'/>"
            "<result>%s</result></datasource>" % script),
            None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 123.2, "DevDouble", [])

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup(
            "<datasource><datasource type='CLIENT' name='inp'/>"
            "<result>%s</result></datasource>" % script2),
            None)
        gjson = '{"data":{"inp":"21"}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)), None)
        self.myAssertRaise(DataSourceSetupError, ds.setDataSources, dp)

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='inp' />
  </datasource>
  <result>%s</result>
</datasource>
""" % script2), None)
        gjson = '{"data":{"inp":21}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)), None)
        self.assertEqual(ds.setDataSources(dp), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 21, "DevLong64", [])

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='CLIENT' name='inp2'>
    <record name='rinp2' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % script3), None)
        gjson = '{"data":{"rinp":21,"rinp2":41}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)), None)
        self.assertEqual(ds.setDataSources(dp), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 62, "DevLong64", [])

        dp = DataSourcePool(
            json.loads(
                '{"datasources":{"CL":"nxswriter.ClientSource.ClientSource"}}'
            ))

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CL' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='CLIENT' name='inp2'>
    <record name='rinp2' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % script3), None)
        gjson = '{"data":{"rinp":21.1}}'
        ljson = '{"data":{"rinp2":41}}'
        self.assertEqual(ds.setDataSources(dp), None)
        self.assertEqual(
            ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 62.1, "DevDouble", [])

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='CLIENT' name='inp2'>
    <record name='rinp2' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % script3), None)
        gjson = '{"data":{"rinp":21.1}}'
        ljson = '{"data":{"rinp2":41}}'
        self.assertEqual(ds.setDataSources(dp), None)
        self.assertEqual(
            ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 62.1, "DevDouble", [])

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup("""
<datasource>
  <result name='res2'>%s</result>
</datasource>
""" % script4), None)
        gjson = '{"data":{"rinp":21.1}}'
        ljson = '{"data":{"rinp2":41}}'
        self.assertEqual(ds.setDataSources(dp), None)
        self.assertEqual(
            ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 62.1, "DevDouble", [])

    # getData test
    # \brief It tests default settings
    def test_getData_common_h5obj(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)

        f = H5CppWriter.create_file(fname, False)

        try:
            rt = f.root()
            script = 'ds.res2 = id(commonblock["__nxroot__"])'
            dp = DataSourcePool()
            dp.nxroot = rt
            dspid = id(dp.nxroot.h5object)

            ds = PyEvalSource()
            ds.setDataSources(dp)
            self.assertTrue(isinstance(ds, DataSource))
            self.myAssertRaise(DataSourceSetupError, ds.getData)
            self.assertEqual(ds.setup("""
<datasource>
 <result name='res2'>%s</result>
</datasource>""" % script), None)
            dt = ds.getData()
            self.checkData(dt, "SCALAR", dspid, "DevLong64", [])
        finally:
            f.close()
            os.remove(fname)

    # getData test
    # \brief It tests default settings
    def test_getData_common_h5(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)

        f = H5CppWriter.create_file(fname, False)

        try:
            rt = f.root()
            script = 'ds.res2 = id(commonblock["__root__"])'
            dp = DataSourcePool()
            dp.nxroot = rt
            dspid = id(dp.nxroot)

            ds = PyEvalSource()
            ds.setDataSources(dp)
            self.assertTrue(isinstance(ds, DataSource))
            self.myAssertRaise(DataSourceSetupError, ds.getData)
            self.assertEqual(ds.setup("""
<datasource>
 <result name='res2'>%s</result>
</datasource>""" % script), None)
            dt = ds.getData()
            self.checkData(dt, "SCALAR", dspid, "DevLong64", [])
        finally:
            f.close()
            os.remove(fname)

    # setup test
    # \brief It tests default settings
    def test_getData_common_global_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = """
try:
    ds.res = ds.inp + ds.inp2
    print("BNB")
except Exception:
    try:
       ds.res = unicode(ds.inp) + unicode(ds.inp2)
    except Exception:
        try:
            ds.res = str(unicode(ds.inp))+ ds.inp2
        except Exception:
            ds.res = ds.inp2
commonblock["myres"] = ds.res
"""
        script = script.replace("unicode", "str")
        script2 = 'ds.res2 = commonblock["myres"]'
        dsp = DataSourcePool()
        dcp = DecoderPool()

        arr = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234000206, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('UINT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr:
            self._simps.dp.write_attribute(k, arr[k][2])

        carr = {
            "int": [1243, "SCALAR", "DevLong64", []],
            "long": [-10000000000000000000000003, "SCALAR", "DevLong64", []],
            "float": [-1.223e-01, "SCALAR", "DevDouble", []],
            "str": ['My String', "SCALAR", "DevString", []],
            "unicode": [u'12\xf8\xff\xf4', "SCALAR", "DevString", []],
            "bool": ['true', "SCALAR", "DevBoolean", []],
        }

        for a in carr:
            for a2 in arr:
                ds = PyEvalSource()
                self.assertTrue(isinstance(ds, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds.getData)
                self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='TANGO' name='inp2'>
    <device name='%s' />
    <record name='%s' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % (self._simps.dp.dev_name(), a2, script)), None)
                if carr[a][2] == "DevString":
                    gjson = '{"data":{"rinp":"%s"}}' % (carr[a][0])
                else:
                    gjson = '{"data":{"rinp":%s}}' % (carr[a][0])

                self.assertEqual(ds.setDataSources(dsp), None)
                self.assertEqual(ds.setJSON(json.loads(gjson)), None)
                dt = ds.getData()
                v1 = Converters.toBool(carr[a][0]) if carr[
                    a][2] == "DevBoolean" else carr[a][0]
                v2 = Converters.toBool(arr[a2][2]) if arr[
                    a2][1] == "DevBoolean" else arr[a2][2]
                try:
                    vv = v1 + v2
                    error = (arr[a2][3] if len(arr[a2]) > 3 else 0)
                except Exception:
                    error = 0
                    try:
                        vv = str(v1) + str(v2)
                    except Exception:
                        vv = str(str(v1)) + v2
                if not ((a in ['str', 'unicode'] and
                         a2 in ['ScalarFloat', 'ScalarDouble']) or
                        (a2 in ['ScalarString', 'ScalarUChar'] and
                         a in ['float'])):
                    self.checkData(
                        dt, carr[a][1], vv, NTP.pTt[
                            type(vv).__name__], carr[a][3],
                        error=error)

                ds2 = PyEvalSource()
                self.assertTrue(isinstance(ds2, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds2.getData)
                self.assertEqual(ds2.setup("""
<datasource>
  <result name='res2'>%s</result>
</datasource>
""" % (script2)), None)
                self.assertEqual(ds2.setDataSources(dsp), None)
                dt = ds2.getData()
                if not ((a in ['str', 'unicode'] and
                         a2 in ['ScalarFloat', 'ScalarDouble']) or
                        (a2 in ['ScalarString', 'ScalarUChar'] and
                         a in ['float'])):
                    self.checkData(dt, carr[a][1], vv, NTP.pTt[
                        type(vv).__name__], carr[a][3], error=error)

            if not PYTG_BUG_213:
                for a2 in arr3:
                    ds = PyEvalSource()
                    self.assertTrue(isinstance(ds, DataSource))
                    self.myAssertRaise(DataSourceSetupError, ds.getData)
                    self.assertEqual(ds.setup("""
    <datasource>
      <datasource type='CLIENT' name='inp'>
        <record name='rinp' />
      </datasource>
      <datasource type='TANGO' name='inp2'>
        <device name='%s'  encoding='%s'/>
        <record name='%s' />
      </datasource>
      <result name='res'>%s</result>
    </datasource>
    """ % (self._simps.dp.dev_name(), arr3[a2][2][0], a2, script)), None)
                    if carr[a][2] == "DevString":
                        gjson = '{"data":{"rinp":"%s"}}' % (carr[a][0])
                    else:
                        gjson = '{"data":{"rinp":%s}}' % (carr[a][0])

                    self.assertEqual(ds.setJSON(json.loads(gjson)), None)
                    self.assertEqual(ds.setDataSources(dsp), None)
                    ds.setDecoders(dcp)
                    dt = ds.getData()
                    v1 = Converters.toBool(carr[a][0]) if carr[
                        a][2] == "DevBoolean" else carr[a][0]
                    ud = dcp.get(arr3[a2][2][0])
                    ud.load(arr3[a2][2])
                    v2 = ud.decode()
                    try:
                        vv = v1 + v2
                    except Exception:
                        try:
                            vv = str(v1) + str(v2)
                        except Exception:
                            try:
                                vv = str(str(v1)) + v2
                            except Exception:
                                vv = v2

                    if type(vv).__name__ == 'ndarray':
                        self.checkData(
                            dt, 'SPECTRUM', vv, NTP.pTt[type(vv[0]).__name__],
                            [len(vv)])
                    else:
                        self.checkData(
                            dt, carr[a][1], vv, NTP.pTt[type(vv).__name__],
                            carr[a][3])

                    ds2 = PyEvalSource()
                    self.assertTrue(isinstance(ds2, DataSource))
                    self.myAssertRaise(DataSourceSetupError, ds2.getData)
                    self.assertEqual(ds2.setup("""
    <datasource>
      <result name='res2'>%s</result>
    </datasource>
    """ % (script2)), None)
                    self.assertEqual(ds2.setDataSources(dsp), None)
                    dt = ds2.getData()
                    if type(vv).__name__ == 'ndarray':
                        self.checkData(
                            dt, 'SPECTRUM', vv, NTP.pTt[type(vv[0]).__name__],
                            [len(vv)])
                    else:
                        self.checkData(
                            dt, carr[a][1], vv, NTP.pTt[type(vv).__name__],
                            carr[a][3])

    # setup test
    # \brief It tests default settings
    def test_getData_common_global_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = """
if type(ds.inp[0]) == type(ds.inp2[0]):
    ds.res = list(ds.inp) + list(ds.inp2)
else:
    ds.res = [unicode(i) for i in ds.inp] + [unicode(i2) for i2 in ds.inp2]
commonblock["my1res"] = ds.res
"""

        script = script.replace("unicode", "str")
        script2 = 'ds.res2 = commonblock["my1res"]'
        dsp = DataSourcePool()
        DecoderPool()

        carr = {
            "int": [1243, "SPECTRUM", "DevLong64", []],
            "long": [-10000000000000000000000003, "SPECTRUM", "DevLong64", []],
            "float": [-1.223e-01, "SPECTRUM", "DevDouble", []],
            "str": ['My String', "SPECTRUM", "DevString", []],
            "unicode": ["Hello", "SPECTRUM", "DevString", []],
            #  "unicode":[u'\x12\xf8\xff\xf4',"SPECTRUM","DevString",[]],
            "bool": ['true', "SPECTRUM", "DevBoolean", []],
        }

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
                arr[k][2] = [arr[k][2] * self.__rnd.randint(1, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0], 0]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in carr:

            if carr[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 3)]
                carr[k][0] = [
                    carr[k][0] * self.__rnd.randint(1, 3)
                    for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                carr[k][0] = [("true" if self.__rnd.randint(0, 1) else "false")
                              for c in range(mlen[0])]

            carr[k][3] = [mlen[0]]

        for k in carr:
            for k2 in arr:

                ds = PyEvalSource()
                self.assertTrue(isinstance(ds, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds.getData)
                self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='TANGO' name='inp2'>
    <device name='%s' />
    <record name='%s' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % (self._simps.dp.dev_name(), k2, script)), None)
                if carr[k][2] == "DevString":
                    gjson = '{"data":{"rinp":%s}}' % (
                        str(carr[k][0]).replace("'", "\""))
                elif carr[k][2] == "DevBoolean":
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + ''.join([a + ','
                                       for a in carr[k][0]])[:-1] + "]")
                else:
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + ''.join([str(a) + ','
                                       for a in carr[k][0]])[:-1] + "]")

                self.assertEqual(ds.setDataSources(dsp), None)
                self.assertEqual(ds.setJSON(json.loads(gjson)), None)
                dt = ds.getData()
                v1 = [Converters.toBool(a)
                      for a in carr[k][0]] if carr[k][2] == "DevBoolean" \
                    else carr[k][0]
                v2 = [Converters.toBool(a) for a in arr[k2][2]] if arr[
                    k2][1] == "DevBoolean" else arr[k2][2]
                if NTP.pTt[type(v1[0]).__name__] == str(type(v2[0]).__name__):
                    vv = v1 + v2
                    error = (arr[k2][4] if len(arr[k2]) > 4 else 0)
                else:
                    vv = [str(i) for i in v1] + [str(i2) for i2 in v2]
                    error = 0
                shape = [len(vv)]
                self.checkData(dt, carr[k][1], vv, NTP.pTt[
                               type(vv[0]).__name__], shape, error=error)

                ds2 = PyEvalSource()
                self.assertTrue(isinstance(ds2, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds2.getData)
                self.assertEqual(ds2.setup("""
<datasource>
  <result name='res2'>%s</result>
</datasource>
""" % (script2)), None)

                self.assertEqual(ds.setDataSources(dsp), None)
                dt = ds.getData()
                self.checkData(dt, carr[k][1], vv, NTP.pTt[
                               type(vv[0]).__name__], shape, error=error)

    # getData test
    # \brief It tests default settings with global json string
    def test_zzgetData_common_global_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = """
if type(ds.inp[0][0]) == type(ds.inp2[0][0]):
    ds.res = list(ds.inp) + list(ds.inp2)
else:
    ds.res = [[unicode(j) for j in i] for i in ds.inp] + \
        [[unicode(j2) for j2 in i2] for i2 in ds.inp2]
commonblock["myre3"] = ds.res
"""
        script = script.replace("unicode", "str")
        script2 = 'ds.res2 = commonblock["myre3"]'
        dsp = DataSourcePool()
        DecoderPool()

        carr = {
            "int": [1243, "IMAGE", "DevLong64", []],
            "long": [-10000000000000000000000003, "IMAGE", "DevLong64", []],
            "float": [-1.223e-01, "IMAGE", "DevDouble", []],
            "str": ['My String', "IMAGE", "DevString", []],
            "unicode": ["Hello", "IMAGE", "DevString", []],
            #    "unicode":[u'\x12\xf8\xff\xf4',"IMAGE","DevString",[]],
            "bool": ['true', "IMAGE", "DevBoolean", []],
        }

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

        nl2 = self.__rnd.randint(1, 10)
        for k in carr:
            if carr[k][2] != "DevBoolean":
                mlen = [
                    self.__rnd.randint(1, 10), nl2, self.__rnd.randint(0, 3)]
                carr[k][0] = [[carr[k][0] * self.__rnd.randint(1, 3)
                               for r in range(mlen[1])]
                              for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), nl2]
                if carr[k][2] == 'DevBoolean':
                    carr[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                    else "false")
                                   for c in range(mlen[1])]
                                  for r in range(mlen[0])]

            carr[k][3] = [mlen[0], mlen[1]]

        for k in arr:
            mlen = [self.__rnd.randint(1, 10), nl2, self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[arr[k][2] * self.__rnd.randint(1, 3)
                              for r in range(mlen[1])]
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), nl2]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [
                        [
                            (
                                True if self.__rnd.randint(0, 1) else False)
                            for c in range(mlen[1])]
                        for r in range(mlen[0])
                    ]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in carr:
            for k2 in arr:

                ds = PyEvalSource()
                self.assertTrue(isinstance(ds, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds.getData)
                self.assertEqual(ds.setup("""
<datasource>
  <datasource type='CLIENT' name='inp'>
    <record name='rinp' />
  </datasource>
  <datasource type='TANGO' name='inp2'>
    <device name='%s' />
    <record name='%s' />
  </datasource>
  <result name='res'>%s</result>
</datasource>
""" % (self._simps.dp.dev_name(), k2, script)), None)

                if carr[k][2] == "DevString":
                    gjson = '{"data":{"rinp":%s}}' % (
                        str(carr[k][0]).replace("'", "\""))
                elif carr[k][2] == "DevBoolean":
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + "".join(['[' + ''.join(
                            [a + ',' for a in row])[:-1] + "],"
                            for row in carr[k][0]])[:-1] + ']')
                else:
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + "".join(['[' + ''.join(
                            [str(a) + ',' for a in row])[:-1] + "],"
                            for row in carr[k][0]])[:-1] + ']')

                self.assertEqual(ds.setDataSources(dsp), None)
                self.assertEqual(ds.setJSON(json.loads(gjson)), None)
                dt = ds.getData()
                v1 = [[Converters.toBool(a) for a in row]
                      for row in carr[k][0]] if carr[k][2] == "DevBoolean" \
                    else carr[k][0]
                v2 = [[Converters.toBool(a) for a in row]
                      for row in arr[k2][2]] if arr[k2][1] == "DevBoolean" \
                    else arr[k2][2]
                if NTP.pTt[type(v1[0][0]).__name__] == \
                   str(type(v2[0][0]).__name__):
                    vv = v1 + v2
                    error = (arr[k2][4] if len(arr[k2]) > 4 else 0)
                else:
                    vv = [[str(j) for j in i]
                          for i in v1] + [[str(j2) for j2 in i2]
                                          for i2 in v2]
                    error = 0
                shape = [len(vv), len(vv[0])]
                self.checkData(dt, carr[k][1], vv, NTP.pTt[
                               type(vv[0][0]).__name__], shape, error=error)

                ds2 = PyEvalSource()
                self.assertTrue(isinstance(ds2, DataSource))
                self.myAssertRaise(DataSourceSetupError, ds2.getData)
                self.assertEqual(ds2.setup("""
<datasource>
  <result name='res2'>%s</result>
</datasource>
""" % (script2)), None)

                self.assertEqual(ds.setDataSources(dsp), None)
                dt = ds.getData()
                self.checkData(dt, carr[k][1], vv, NTP.pTt[
                               type(vv[0][0]).__name__], shape, error=error)


if __name__ == '__main__':
    unittest.main()
