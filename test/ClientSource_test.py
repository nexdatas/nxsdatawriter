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
# \file ClientSourceTest.py
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


from nxswriter.DataSources import DataSource
from nxswriter.ClientSource import ClientSource
from nxswriter.Errors import DataSourceSetupError
from nxswriter.Types import Converters

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class ClientSourceTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

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

        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.name, None)

    # __str__ test
    # \brief It tests default settings
    def test_str_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        name = 'myrecord'
        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), " CLIENT record %s"
                         % (None))

        ds = ClientSource()
        ds.name = name
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), " CLIENT record %s"
                         % (name))

        ds = ClientSource()
        ds.name = name
        gjson = '{"data":{"myrecord":"1"}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)), None)
        self.assertEqual(ds.__str__(), " CLIENT record %s"
                         % (name))

        ds = ClientSource()
        ds.name = name
        ljson = '{"data":{"myrecord2":1}}'
        self.assertEqual(
            ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
        self.assertEqual(ds.__str__(), " CLIENT record %s"
                         % (name))

    # setup test
    # \brief It tests default settings
    def test_setup_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dname = 'writer'
        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.setup, "<datasource/>")

        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><record/></datasource>")

        ds = ClientSource()
        self.assertEqual(ds.name, None)
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><record name='%s'/></datasource>" % dname),
            None)
        self.assertEqual(ds.name, dname)

    # Data check
    # \brief It check the source Data
    # \param data  tested data
    # \param format data format
    # \param value data value
    # \param ttype data Tango type
    # \param shape data shape
    def checkData(self, data, format, value, ttype, shape):
        self.assertEqual(data["rank"], format)
        self.assertEqual(data["tangoDType"], ttype)
        self.assertEqual(data["shape"], shape)
        if format == 'SCALAR':
            self.assertEqual(data["value"], value)
        elif format == 'SPECTRUM':
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                self.assertEqual(data["value"][i], value[i])
        else:
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                self.assertEqual(len(data["value"][i]), len(value[i]))
                for j in range(len(value[i])):
                    self.assertEqual(data["value"][i][j], value[i][j])

    # getData test
    # \brief It tests default settings
    def test_getData_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        name = 'myrecord'
        name2 = 'myrecord2'
        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.getData(), None)
        ds.name = name
        self.assertEqual(ds.getData(), None)

        ds = ClientSource()
        ds.name = name
        gjson = '{"data":{"myrecord":"1"}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", "1", "DevString", [])

        ds = ClientSource()
        ds.name = name2
        gjson = '{"data":{"myrecord":"1"}}'
        ljson = '{"data":{"myrecord2":12}}'
        self.assertEqual(
            ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 12, "DevLong64", [])

        ds = ClientSource()
        ds.name = name2
        gjson = '{}'
        ljson = '{"data":{"myrecord2":12}}'
        self.assertEqual(
            ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 12, "DevLong64", [])

    # setup test
    # \brief It tests default settings
    def test_getData_global_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": [1243, "SCALAR", "DevLong64", []],
            "long": [-10000000000000000000000003, "SCALAR", "DevLong64", []],
            "float": [-1.223e-01, "SCALAR", "DevDouble", []],
            "str": ['My String', "SCALAR", "DevString", []],
            "unicode": [u'12\xf8\xff\xf4', "SCALAR", "DevString", []],
            "bool": ['true', "SCALAR", "DevBoolean", []],
        }

        for a in arr:
            ds = ClientSource()
            ds.name = a
            if arr[a][2] == "DevString":
                gjson = '{"data":{"%s":"%s"}}' % (a, arr[a][0])
            else:
                gjson = '{"data":{"%s":%s}}' % (a, arr[a][0])
            self.assertEqual(ds.setJSON(json.loads(gjson)), None)
            dt = ds.getData()
            if arr[a][2] == "DevBoolean":
                self.checkData(
                    dt, arr[a][1], Converters.toBool(arr[a][0]),
                    arr[a][2], arr[a][3])
            else:
                self.checkData(dt, arr[a][1], arr[a][0], arr[a][2], arr[a][3])

    # getData test
    # \brief It tests default settings
    def test_getData_local_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "none": ["null", None, "NoneType", []],
            "int": [-23243, "SCALAR", "DevLong64", []],
            "long": [10000023540000000000000003, "SCALAR", "DevLong64", []],
            "float": [121.223e-01, "SCALAR", "DevDouble", []],
            "str": ['My String 2', "SCALAR", "DevString", []],
            "unicode": [u'12\xf8\xff\xf4', "SCALAR", "DevString", []],
            "bool": ['true', "SCALAR", "DevBoolean", []],
        }

        for a in arr:
            ds = ClientSource()
            ds.name = a
            gjson = '{"data":{"myrecord":"1"}}'
            if arr[a][2] == "DevString":
                ljson = '{"data":{"%s":"%s"}}' % (a, arr[a][0])
            else:
                ljson = '{"data":{"%s":%s}}' % (a, arr[a][0])
            self.assertEqual(
                ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = ds.getData()
            if arr[a][2] == "NoneType":
                self.assertTrue(dt is None)
            elif arr[a][2] == "DevBoolean":
                self.checkData(
                    dt, arr[a][1], Converters.toBool(arr[a][0]),
                    arr[a][2], arr[a][3])
            else:
                self.checkData(dt, arr[a][1], arr[a][0], arr[a][2], arr[a][3])

    # setup test
    # \brief It tests default settings
    def test_getData_global_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": [1243, "SPECTRUM", "DevLong64", []],
            "long": [-10000000000000000000000003, "SPECTRUM", "DevLong64", []],
            "float": [-1.223e-01, "SPECTRUM", "DevDouble", []],
            "str": ['My String', "SPECTRUM", "DevString", []],
            "unicode": ["Hello", "SPECTRUM", "DevString", []],
            # "unicode":[u'\x12\xf8\xff\xf4',"SPECTRUM","DevString",[]],
            "bool": ['true', "SPECTRUM", "DevBoolean", []],
        }

        for k in arr:

            if arr[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arr[k][0] = [arr[k][0] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][0] = [("true" if self.__rnd.randint(0, 1) else "false")
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0]]

            ds = ClientSource()
            ds.name = k
            if arr[k][2] == "DevString":
                gjson = '{"data":{"%s":%s}}' % (
                    k, str(arr[k][0]).replace("'", "\""))
            elif arr[k][2] == "DevBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    k, '[' + ''.join([a + ',' for a in arr[k][0]])[:-1] + "]")
            else:
                gjson = '{"data":{"%s":%s}}' % (
                    k, '[' + ''.join([str(a)
                                      + ',' for a in arr[k][0]])[:-1] + "]")
            self.assertEqual(ds.setJSON(json.loads(gjson)), None)
            dt = ds.getData()
            if arr[k][2] == "DevBoolean":
                self.checkData(dt, arr[k][1], [Converters.toBool(a)
                               for a in arr[k][0]], arr[k][2], arr[k][3])
            else:
                self.checkData(dt, arr[k][1], arr[k][0], arr[k][2], arr[k][3])

    # setup test
    # \brief It tests default settings
    def test_getData_local_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": [1243, "SPECTRUM", "DevLong64", []],
            "long": [-10000000000000000000000003, "SPECTRUM", "DevLong64", []],
            "float": [-1.223e-01, "SPECTRUM", "DevDouble", []],
            "str": ['My String', "SPECTRUM", "DevString", []],
            "unicode": ["Hello", "SPECTRUM", "DevString", []],
            #            "unicode":[u'\x12\xf8\xff\xf4',"SPECTRUM","DevString",[]],
            "bool": ['true', "SPECTRUM", "DevBoolean", []],
        }

        for k in arr:

            if arr[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arr[k][0] = [arr[k][0] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][0] = [("true" if self.__rnd.randint(0, 1) else "false")
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0]]

            ds = ClientSource()
            ds.name = k
            if arr[k][2] == "DevString":
                ljson = '{"data":{"%s":%s}}' % (
                    k, str(arr[k][0]).replace("'", "\""))
            elif arr[k][2] == "DevBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    k, '[' + ''.join([a + ',' for a in arr[k][0]])[:-1] + "]")
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    k, '[' + ''.join([str(a)
                                      + ',' for a in arr[k][0]])[:-1] + "]")
            gjson = '{"data":{"myrecord":"1"}}'
            self.assertEqual(
                ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = ds.getData()
            if arr[k][2] == "DevBoolean":
                self.checkData(dt, arr[k][1], [Converters.toBool(a)
                               for a in arr[k][0]], arr[k][2], arr[k][3])
            else:
                self.checkData(dt, arr[k][1], arr[k][0], arr[k][2], arr[k][3])

    # getData test
    # \brief It tests default settings with global json string
    def test_getData_global_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": [1243, "IMAGE", "DevLong64", []],
            "long": [-10000000000000000000000003, "IMAGE", "DevLong64", []],
            "float": [-1.223e-01, "IMAGE", "DevDouble", []],
            "str": ['My String', "IMAGE", "DevString", []],
            "unicode": ["Hello", "IMAGE", "DevString", []],
            #            "unicode":[u'\x12\xf8\xff\xf4',"IMAGE","DevString",[]],
            "bool": ['true', "IMAGE", "DevBoolean", []],
        }

        for k in arr:

            if arr[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                arr[k][0] = [[arr[k][0] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][2] == 'DevBoolean':
                    arr[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                   else "false")
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]

            ds = ClientSource()
            ds.name = k
            if arr[k][2] == "DevString":
                gjson = '{"data":{"%s":%s}}' % (
                    k, str(arr[k][0]).replace("'", "\""))
            elif arr[k][2] == "DevBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    k, '[' + "".join(['['
                                      + ''.join([a + ',' for a in row])[:-1]
                                      + "]," for row in arr[k][0]])[:-1] + ']')
            else:
                gjson = '{"data":{"%s":%s}}' % (
                    k, '[' + "".join(['['
                                      + ''.join([str(a)
                                                 + ',' for a in row])[:-1]
                                      + "]," for row in arr[k][0]])[:-1] + ']')
            self.assertEqual(ds.setJSON(json.loads(gjson)), None)
            dt = ds.getData()
            if arr[k][2] == "DevBoolean":
                self.checkData(
                    dt, arr[k][1], [[Converters.toBool(a) for a in row]
                                    for row in arr[k][0]],
                    arr[k][2], arr[k][3])
            else:
                self.checkData(dt, arr[k][1], arr[k][0], arr[k][2], arr[k][3])

    # getData test
    # \brief It tests default settings with local json string
    def test_getData_local_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": [1243, "IMAGE", "DevLong64", []],
            "long": [-10000000000000000000000003, "IMAGE", "DevLong64", []],
            "float": [-1.223e-01, "IMAGE", "DevDouble", []],
            "str": ['My String', "IMAGE", "DevString", []],
            "unicode": ["Hello", "IMAGE", "DevString", []],
            "bool": ['true', "IMAGE", "DevBoolean", []],
        }

        for k in arr:

            if arr[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                arr[k][0] = [[arr[k][0] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])] for c in range(mlen[0])]
                arr[k][3] = [mlen[0], mlen[1]]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][2] == 'DevBoolean':
                    arr[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                   else "false")
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

                    arr[k][3] = [mlen[0], mlen[1]]

            ds = ClientSource()
            ds.name = k
            if arr[k][2] == "DevString":
                ljson = '{"data":{"%s":%s}}' % (
                    k, str(arr[k][0]).replace("'", "\""))
            elif arr[k][2] == "DevBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    k, '[' + "".join(['['
                                      + ''.join([a + ',' for a in row])[:-1]
                                      + "]," for row in arr[k][0]])[:-1] + ']')
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    k, '['
                    + "".join(['['
                               + ''.join([str(a)
                                          + ',' for a in row])[:-1] + "],"
                               for row in arr[k][0]])[:-1] + ']')
            gjson = '{"data":{"myrecord":"1"}}'
            self.assertEqual(
                ds.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = ds.getData()
            if arr[k][2] == "DevBoolean":
                self.checkData(dt, arr[k][1], [[Converters.toBool(a)
                                                for a in row]
                               for row in arr[k][0]], arr[k][2], arr[k][3])
            else:
                self.checkData(dt, arr[k][1], arr[k][0], arr[k][2], arr[k][3])

    # isValid test
    # \brief It tests default settings
    def test_isValid(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ClientSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.isValid(), True)


if __name__ == '__main__':
    unittest.main()
