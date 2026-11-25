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
# \file MYSQLSourceTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii

try:
    import psycopg2
    # connection arguments to PGSQL DB
    args = {}
    args["database"] = 'mydb'
    # inscance of psycog2
    pgdb = psycopg2.connect(**args)
    pgdb.close()
except Exception:
    import pytest
    if pytest.__version__ < "3.0.0":
        pytest.skip()
    else:
        pytestmark = pytest.mark.skip

from nxswriter.DBaseSource import DBaseSource
from nxswriter.Errors import PackageError

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class PGSQLSourceTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self.__dbtype = "PGSQL"
        self.__dbname = "mydb"

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

        self._mydb = None

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")
        # connection arguments to PGSQL DB
        args = {}
        args["database"] = 'mydb'
        # inscance of psycog2
        self._mydb = psycopg2.connect(**args)
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")
        self._mydb.close()

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

    # setup test
    # \brief It tests default settings
    def test_getData_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        query = "select city from weather limit 1"
        format = "SPECTRUM"

        cursor = self._mydb.cursor()
        cursor.execute(query)
        scalar = cursor.fetchone()[0]
        cursor.close()

        ds = DBaseSource()
        self.myAssertRaise(PackageError, ds.getData)

        ds = DBaseSource()
        ds.dbtype = "UNKNOWNDB"
        self.myAssertRaise(PackageError, ds.getData)

        ds = DBaseSource()
        ds.dbtype = self.__dbtype
#        dt = ds.getData()
        self.myAssertRaise(TypeError, ds.getData)

        ds = DBaseSource()
        ds.dbtype = self.__dbtype
        ds.query = query
        self.myAssertRaise(TypeError, ds.getData)

        ds = DBaseSource()
        ds.dbtype = self.__dbtype
        ds.query = query
        ds.format = format
        ds.dbname = self.__dbname
        dt = ds.getData()

        self.checkData(dt, 'SPECTRUM', [scalar], 'DevString', [1, 0])

    # setup test
    # \brief It tests default settings
    def test_getData_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": ["SELECT temp_lo FROM weather limit 1", "SCALAR",
                    "DevLong64", [1, 0]],
            "long": ["SELECT temp_lo FROM weather limit 1", "SCALAR",
                     "DevLong64", [1, 0]],
            "float": ["SELECT prcp FROM weather limit 1", "SCALAR",
                      "DevDouble", [1, 0]],
            "str": ["SELECT city FROM weather limit 1", "SCALAR",
                    "DevString", [1, 0]],
            "unicode": ["SELECT city FROM weather limit 1", "SCALAR",
                        "DevString", [1, 0]],
            # "bool":["SELECT exported FROM weather limit 1","SCALAR",
            #    "DevBoolean",[1,0]],
            "bool": ["SELECT temp_lo FROM weather limit 1", "SCALAR",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchone()[0]
            cursor.close()

            ds = DBaseSource()
            ds.query = arr[a][0]
            ds.dbtype = self.__dbtype
            ds.format = arr[a][1]
            ds.dbname = self.__dbname
            dt = ds.getData()

#            print a, value, dt,arr[a][0]

            self.checkData(dt, arr[a][1], value, arr[a][2], arr[a][3])

    # setup test
    # \brief It tests default settings
    def test_getData_spectrum_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": ["SELECT temp_lo FROM weather limit 1", "SPECTRUM",
                    "DevLong64", [1, 0]],
            "long": ["SELECT temp_lo FROM weather limit 1", "SPECTRUM",
                     "DevLong64", [1, 0]],
            "float": ["SELECT prcp FROM weather limit 1", "SPECTRUM",
                      "DevDouble", [1, 0]],
            "str": ["SELECT city FROM weather limit 1", "SPECTRUM",
                    "DevString", [1, 0]],
            "unicode": ["SELECT city FROM weather limit 1", "SPECTRUM",
                        "DevString", [1, 0]],
            #  "bool":["SELECT exported FROM weather limit 1",
            # "SPECTRUM","DevBoolean",[1,0]],
            "bool": ["SELECT temp_lo FROM weather limit 1", "SPECTRUM",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchone()
            cursor.close()

            arr[a][3][0] = len(value)

            ds = DBaseSource()
            ds.query = arr[a][0]
            ds.dbtype = self.__dbtype
            ds.format = arr[a][1]
            ds.dbname = self.__dbname
            dt = ds.getData()

#            print a, value, dt,arr[a][0]

            self.checkData(dt, arr[a][1], value, arr[a][2], arr[a][3])

    # setup test
    # \brief It tests default settings
    def test_getData_spectrum_trans(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": ["SELECT temp_lo FROM weather limit 1", "SPECTRUM",
                    "DevLong64", [1, 0]],
            "long": ["SELECT temp_lo FROM weather limit 1", "SPECTRUM",
                     "DevLong64", [1, 0]],
            "float": ["SELECT prcp FROM weather limit 1", "SPECTRUM",
                      "DevDouble", [1, 0]],
            "str": ["SELECT city FROM weather limit 1", "SPECTRUM",
                    "DevString", [1, 0]],
            "unicode": ["SELECT city FROM weather limit 1", "SPECTRUM",
                        "DevString", [1, 0]],
            #            "bool":["SELECT exported FROM weather limit 1",
            # "SPECTRUM","DevBoolean",[1,0]],
            "bool": ["SELECT temp_lo FROM weather limit 1", "SPECTRUM",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchall()
            cursor.close()

            arr[a][3] = [len(value[0]), 0]

            ds = DBaseSource()
            ds.query = arr[a][0]
            ds.dbtype = self.__dbtype
            ds.format = arr[a][1]
            ds.dbname = self.__dbname
            dt = ds.getData()

            self.checkData(
                dt, arr[a][1], list(el for el in value[0]), arr[a][2],
                arr[a][3])

    # setup test
    # \brief It tests default settings
    def test_getData_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": ["SELECT temp_lo FROM weather limit 4", "SPECTRUM",
                    "DevLong64", [1, 0]],
            "long": ["SELECT temp_lo FROM weather limit 4", "SPECTRUM",
                     "DevLong64", [1, 0]],
            "float": ["SELECT prcp FROM weather limit 4", "SPECTRUM",
                      "DevDouble", [1, 0]],
            "str": ["SELECT city FROM weather limit 4", "SPECTRUM",
                    "DevString", [1, 0]],
            "unicode": ["SELECT city FROM weather limit 4", "SPECTRUM",
                        "DevString", [1, 0]],
            #            "bool":["SELECT exported FROM weather limit 4",
            #  "SPECTRUM","DevBoolean",[1,0]],
            "bool": ["SELECT temp_lo FROM weather limit 4", "SPECTRUM",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchall()
            cursor.close()

            arr[a][3] = [len(value), 0]

            ds = DBaseSource()
            ds.query = arr[a][0]
            ds.dbtype = self.__dbtype
            ds.format = arr[a][1]
            ds.dbname = self.__dbname
            dt = ds.getData()

            self.checkData(dt, arr[a][1], list(el[0]
                           for el in value), arr[a][2], arr[a][3])

    # setup test
    # \brief It tests default settings
    def test_getData_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": ["SELECT temp_lo FROM weather limit 4", "IMAGE",
                    "DevLong64", [1, 0]],
            "long": ["SELECT temp_lo FROM weather limit 4", "IMAGE",
                     "DevLong64", [1, 0]],
            "float": ["SELECT prcp FROM weather limit 4", "IMAGE",
                      "DevDouble", [1, 0]],
            "str": ["SELECT city FROM weather limit 4", "IMAGE",
                    "DevString", [1, 0]],
            "unicode": ["SELECT city FROM weather limit 4", "IMAGE",
                        "DevString", [1, 0]],
            #            "bool":["SELECT exported FROM weather limit 4",
            #  "IMAGE","DevBoolean",[1,0]],
            "bool": ["SELECT temp_lo FROM weather limit 4", "IMAGE",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchall()
            cursor.close()

            arr[a][3] = [len(value), len(value[0])]

            ds = DBaseSource()
            ds.query = arr[a][0]
            ds.dbtype = self.__dbtype
            ds.format = arr[a][1]
            ds.dbname = self.__dbname
            dt = ds.getData()

            self.checkData(dt, arr[a][1], value, arr[a][2], arr[a][3])


if __name__ == '__main__':
    unittest.main()
