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
# \file PyEvalSourceTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import json
import binascii


from nxswriter.DataSources import DataSource
from nxswriter.PyEvalSource import PyEvalSource
from nxswriter.DataSourcePool import DataSourcePool
from nxswriter.Errors import DataSourceSetupError
from nxswriter.Types import Converters, NTP

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class PyEvalSourceTest(unittest.TestCase):

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

    # constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), " PYEVAL %s" % (""))

    # setup test
    # \brief It tests default settings
    def test_setup_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dname = 'writer'
        script = 'ds.result = 0'
        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.setup, "<datasource/>")

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><result/></datasource>")

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><result name ='writer'/></datasource>")

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><result name='%s'>ds.%s = 0 </result>"
                     "</datasource>" % (dname, dname)), None)
        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup(
                "<datasource><result>%s</result></datasource>" % script), None)
        self.assertEqual(ds.__str__(), " PYEVAL %s" % (script))

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><datasource/><result>%s</result></datasource>"
            % script)

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><datasource type='CLIENT'/><result>%s</result>"
            "</datasource>" % script)

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><datasource name='INP'/><result>%s</result>"
            "</datasource>" % script)

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup(
                "<datasource><datasource type='CLIENT' name='INP'/>"
                "<result>%s</result></datasource>" % script),
            None)

        ds = PyEvalSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.setup("""<datasource>
   <datasource type='CLIENT' name='INP'/>
   <datasource type='TANGO' name='INP2'/>
   <result>%s</result>
</datasource>
"""
                                  % script), None)

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

        script = 'ds.result = 123.2'
        script1 = 'ds.result = commonblock["__counter__"]'
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
        self.assertEqual(ds.setDataSources(dp), None)
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.getData)
        self.assertEqual(ds.setup(
            "<datasource>"
            "<result>%s</result></datasource>" % script1),
            None)
        dp.counter = 134
        dt = ds.getData()
        self.checkData(dt, "SCALAR", 134, "DevLong64", [])

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
if type(ds.inp) is type(ds.inp2):
    ds.res = ds.inp + ds.inp2
else:
    ds.res = unicode(ds.inp) + unicode(ds.inp2)
"""
        script = script.replace("unicode", "str")
        dp = DataSourcePool()

        arr = {
            "int": [1243, "SCALAR", "DevLong64", []],
            "long": [-10000000000000000000000003, "SCALAR", "DevLong64", []],
            "float": [-1.223e-01, "SCALAR", "DevDouble", []],
            "str": ['My String', "SCALAR", "DevString", []],
            "unicode": [u'12\xf8\xff\xf4', "SCALAR", "DevString", []],
            "bool": ['true', "SCALAR", "DevBoolean", []],
        }

        arr2 = {
            "int": [1123, "SCALAR", "DevLong64", []],
            "long": [-11231000000000000000000003, "SCALAR", "DevLong64", []],
            "float": [-1.113e-01, "SCALAR", "DevDouble", []],
            "str": ['My funy', "SCALAR", "DevString", []],
            "unicode": [u'\xf812\xff\xf4', "SCALAR", "DevString", []],
            "bool": ['false', "SCALAR", "DevBoolean", []],
        }

        for a in arr:
            for a2 in arr2:

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
""" % script), None)
                if arr[a][2] == "DevString":
                    gjson = '{"data":{"rinp":"%s"}}' % (arr[a][0])
                else:
                    gjson = '{"data":{"rinp":%s}}' % (arr[a][0])
                if arr2[a2][2] == "DevString":
                    gjson2 = '{"data":{"rinp2":"%s"}}' % (arr2[a2][0])
                else:
                    gjson2 = '{"data":{"rinp2":%s}}' % (arr2[a2][0])

                self.assertEqual(ds.setDataSources(dp), None)
                self.assertEqual(
                    ds.setJSON(json.loads(gjson), json.loads(gjson2)), None)
                dt = ds.getData()
                v1 = Converters.toBool(arr[a][0]) if arr[
                    a][2] == "DevBoolean" else arr[a][0]
                v2 = Converters.toBool(arr2[a2][0]) if arr2[
                    a2][2] == "DevBoolean" else arr2[a2][0]
                vv = v1 + v2 if type(v1) is type(
                    v2) else str(v1) + str(v2)
                self.checkData(
                    dt, arr[a][1], vv, NTP.pTt[type(vv).__name__], arr[a][3])

    # setup test
    # \brief It tests default settings
    def test_getData_global_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = """
if type(ds.inp[0]) is type(ds.inp2[0]):
    ds.res = ds.inp + ds.inp2
else:
    ds.res = [str(i) for i in ds.inp] + [str(i2) for i2 in ds.inp2]
"""

        dp = DataSourcePool()
        arr = {
            "int": [1243, "SPECTRUM", "DevLong64", []],
            "long": [-10000000000000000000000003, "SPECTRUM", "DevLong64", []],
            "float": [-1.223e-01, "SPECTRUM", "DevDouble", []],
            "str": ['My String', "SPECTRUM", "DevString", []],
            "unicode": ["Hello", "SPECTRUM", "DevString", []],
            # "unicode":[u'\x12\xf8\xff\xf4',"SPECTRUM","DevString",[]],
            "bool": ['true', "SPECTRUM", "DevBoolean", []],
        }

        arr2 = {
            "int": [1123, "SPECTRUM", "DevLong64", []],
            "long": [-1012300000000000000000, "SPECTRUM", "DevLong64", []],
            "float": [-1.112e-01, "SPECTRUM", "DevDouble", []],
            "str": ['My String2', "SPECTRUM", "DevString", []],
            "unicode": ["Hello!", "SPECTRUM", "DevString", []],
            # "unicode":[u'\x14\xf8\xff\xf4',"SPECTRUM","DevString",[]],
            "bool": ['false', "SPECTRUM", "DevBoolean", []],
        }

        for k in arr:

            if arr[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 3)]
                arr[k][0] = [arr[k][0] * self.__rnd.randint(1, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][0] = [("true" if self.__rnd.randint(0, 1) else "false")
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0]]

        for k in arr2:

            if arr2[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 3)]
                arr2[k][0] = [
                    arr2[k][0] * self.__rnd.randint(1, 3)
                    for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr2[k][0] = [("true" if self.__rnd.randint(0, 1) else "false")
                              for c in range(mlen[0])]

            arr2[k][3] = [mlen[0]]

        for k in arr:
            for k2 in arr2:

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
""" % script), None)
                if arr[k][2] == "DevString":
                    gjson = '{"data":{"rinp":%s}}' % (
                        str(arr[k][0]).replace("'", "\""))
                elif arr[k][2] == "DevBoolean":
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + ''.join([a + ',' for a in arr[k][0]])[:-1] + "]")
                else:
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + ''.join([str(a) + ','
                                       for a in arr[k][0]])[:-1] + "]")

                if arr2[k2][2] == "DevString":
                    gjson2 = '{"data":{"rinp2":%s}}' % (
                        str(arr2[k2][0]).replace("'", "\""))
                elif arr2[k2][2] == "DevBoolean":
                    gjson2 = '{"data":{"rinp2":%s}}' % (
                        '[' + ''.join([a + ','
                                       for a in arr2[k2][0]])[:-1] + "]")
                else:
                    gjson2 = '{"data":{"rinp2":%s}}' % (
                        '[' + ''.join([str(a) + ','
                                       for a in arr2[k2][0]])[:-1] + "]")

                self.assertEqual(ds.setDataSources(dp), None)
                self.assertEqual(
                    ds.setJSON(json.loads(gjson), json.loads(gjson2)), None)
                dt = ds.getData()
                v1 = [Converters.toBool(a) for a in arr[k][0]] \
                    if arr[k][2] == "DevBoolean" else arr[k][0]
                v2 = [Converters.toBool(a) for a in arr2[k2][0]] if arr2[
                    k2][2] == "DevBoolean" else arr2[k2][0]
                vv = v1 + v2 if (str(type(v1[0]).__name__) ==
                                 str(type(v2[0]).__name__)) \
                    else [str(i) for i in v1] + [str(i2) for i2 in v2]
                self.checkData(dt, arr[k][1], vv, NTP.pTt[
                               type(vv[0]).__name__],
                               [arr[k][3][0] + arr2[k2][3][0]])

    # getData test
    # \brief It tests default settings with global json string
    def test_getData_global_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        script = """
if type(ds.inp[0][0]) is type(ds.inp2[0][0]):
    ds.res = ds.inp + ds.inp2
else:
    ds.res = [[str(j) for j in i] for i in ds.inp] + """ \
        """[[str(j2) for j2 in i2] for i2 in ds.inp2]
"""

        dp = DataSourcePool()

        arr = {
            "int": [1243, "IMAGE", "DevLong64", []],
            "long": [-10000000000000000000000003, "IMAGE", "DevLong64", []],
            "float": [-1.223e-01, "IMAGE", "DevDouble", []],
            "str": ['My String', "IMAGE", "DevString", []],
            "unicode": ["Hello", "IMAGE", "DevString", []],
            #            "unicode":[u'\x12\xf8\xff\xf4',"IMAGE","DevString",[]],
            "bool": ['true', "IMAGE", "DevBoolean", []],
        }

        arr2 = {
            "int": [1123, "SPECTRUM", "DevLong64", []],
            "long": [-10123000000000000000000003, "SPECTRUM", "DevLong64", []],
            "float": [-1.112e-01, "SPECTRUM", "DevDouble", []],
            "str": ['My String2', "SPECTRUM", "DevString", []],
            "unicode": ["Hello!", "SPECTRUM", "DevString", []],
            #            "unicode":[u'\x14\xf8\xff\xf4',"SPECTRUM","DevString",[]],
            "bool": ['false', "SPECTRUM", "DevBoolean", []],
        }

        for k in arr:
            nl2 = self.__rnd.randint(1, 10)
            if arr[k][2] != "DevBoolean":
                mlen = [
                    self.__rnd.randint(1, 10), nl2, self.__rnd.randint(0, 3)]
                arr[k][0] = [[arr[k][0] * self.__rnd.randint(1, 3)
                              for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), nl2]
                if arr[k][2] == 'DevBoolean':
                    arr[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                   else "false")
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]

            if arr2[k][2] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                arr2[k][0] = [[arr2[k][0] * self.__rnd.randint(1, 3)
                               for r in range(mlen[1])]
                              for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr2[k][2] == 'DevBoolean':
                    arr2[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                    else "false")
                                   for c in range(mlen[1])]
                                  for r in range(mlen[0])]

            arr2[k][3] = [mlen[0], mlen[1]]

        for k in arr:
            for k2 in arr2:

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
""" % script), None)

                if arr[k][2] == "DevString":
                    gjson = '{"data":{"rinp":%s}}' % (
                        str(arr[k][0]).replace("'", "\""))
                elif arr[k][2] == "DevBoolean":
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + "".join(['[' + ''.join(
                            [a + ',' for a in row])[:-1] + "],"
                            for row in arr[k][0]])[:-1] + ']')
                else:
                    gjson = '{"data":{"rinp":%s}}' % (
                        '[' + "".join(['[' + ''.join(
                            [str(a) + ',' for a in row])[:-1] + "],"
                            for row in arr[k][0]])[:-1] + ']')

                if arr2[k2][2] == "DevString":
                    gjson2 = '{"data":{"rinp2":%s}}' % (
                        str(arr2[k2][0]).replace("'", "\""))
                elif arr2[k2][2] == "DevBoolean":
                    gjson2 = '{"data":{"rinp2":%s}}' % (
                        '[' + "".join(['[' + ''.join(
                            [a + ',' for a in row])[:-1] + "],"
                            for row in arr2[k2][0]])[:-1] + ']')
                else:
                    gjson2 = '{"data":{"rinp2":%s}}' % (
                        '[' + "".join(['[' + ''.join(
                            [str(a) + ',' for a in row])[:-1] + "],"
                            for row in arr2[k2][0]])[:-1] + ']')

                self.assertEqual(ds.setDataSources(dp), None)
                self.assertEqual(
                    ds.setJSON(json.loads(gjson), json.loads(gjson2)), None)
                dt = ds.getData()
                v1 = [[Converters.toBool(a) for a in row]
                      for row in arr[k][0]] \
                    if arr[k][2] == "DevBoolean" else arr[k][0]
                v2 = [[Converters.toBool(a) for a in row]
                      for row in arr2[k2][0]] \
                    if arr2[k2][2] == "DevBoolean" else arr2[k2][0]
                vv = v1 + v2 if str(type(v1[0][0])) == str(type(v2[0][0])) \
                    else ([[str(j) for j in i] for i in v1] +
                          [[str(j2) for j2 in i2] for i2 in v2])
                self.checkData(dt, arr[k][1], vv,
                               NTP.pTt[type(vv[0][0]).__name__], [
                               arr[k][3][0] + arr2[k2][3][0], arr[k][3][1]])

    # isValid test
    # \brief It tests default settings
    def test_isValid(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = PyEvalSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.isValid(), True)


if __name__ == '__main__':
    unittest.main()
