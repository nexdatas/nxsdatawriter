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
import time

try:
    try:
        import MySQLdb
    except Exception:
        import pymysql as MySQLdb
        MySQLdb.install_as_MySQLdb()
    # connection arguments to MYSQL DB
    args = {}
    args["db"] = 'tango'
    # args["host"] = 'localhost'
    args["read_default_file"] = '/etc/my.cnf'
    # inscance of MySQLdb
    mydb = MySQLdb.connect(**args)
    mydb.close()
except Exception:
    try:
        try:
            import MySQLdb
        except Exception:
            import pymysql as MySQLdb
            MySQLdb.install_as_MySQLdb()
        import MySQLdb
        from os.path import expanduser
        home = expanduser("~")
        # connection arguments to MYSQL DB
        args2 = {
            # 'host': u'localhost',
            'db': u'tango',
            'read_default_file': u'%s/.my.cnf' % home,
            'use_unicode': True}
        # inscance of MySQLdb
        mydb = MySQLdb.connect(**args2)
        mydb.close()
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


if sys.version_info > (3,):
    long = int


# test fixture
class MYSQLSourceTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self.__dbtype = "MYSQL"
        self.__dbname = "tango"
        self.__mycnf = '/etc/my.cnf'

        try:
            self.__seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = long(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

        self._mydb = None
        self._largs = None

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")
        # connection arguments to MYSQL DB
        try:
            args = {}
            args["db"] = 'tango'
            # args["host"] = 'localhost'
            args["read_default_file"] = '/etc/my.cnf'
            self._mydb = MySQLdb.connect(**args)
        except Exception:
            from os.path import expanduser
            home = expanduser("~")
            args2 = {
                # 'host': u'localhost',
                'db': u'tango',
                'read_default_file': u'%s/.my.cnf' % home,
                'use_unicode': True}
            self._mydb = MySQLdb.connect(**args2)
            self._largs = args2
            print("ARGS: %s" % str(args2))
        print("SEED = %s" % self.__seed)

    def setsource(self, sr):
        if self._largs:
            if 'read_default_file' in self._largs.keys():
                sr.mycnf = self._largs['read_default_file']

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

        query = "select pid from devices;"
        query2 = "SELECT pid FROM device limit 1"
        format = "SPECTRUM"

        cursor = self._mydb.cursor()
        cursor.execute(query2)
        scalar = cursor.fetchone()[0]
        cursor.close()

        ds = DBaseSource()
        self.setsource(ds)
        self.myAssertRaise(PackageError, ds.getData)

        ds = DBaseSource()
        self.setsource(ds)
        ds.dbtype = "UNKNOWNDB"
        self.myAssertRaise(PackageError, ds.getData)

        ds = DBaseSource()
        self.setsource(ds)
        ds.dbtype = self.__dbtype
        self.myAssertRaise(TypeError, ds.getData)

        ds = DBaseSource()
        self.setsource(ds)
        ds.dbtype = self.__dbtype
        ds.query = query
        self.myAssertRaise(MySQLdb.OperationalError, ds.getData)

        ds = DBaseSource()
        self.setsource(ds)
        ds.dbtype = self.__dbtype
        ds.query = query2
        ds.format = format
        ds.dbname = self.__dbname
        dt = ds.getData()

        self.checkData(dt, 'SPECTRUM', [long(scalar)], 'DevLong64', [1, 0])

    # setup test
    # \brief It tests default settings
    def test_getData_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "int": ["SELECT pid FROM device limit 1", "SCALAR",
                    "DevLong64", [1, 0]],
            "long": ["SELECT pid FROM device limit 1", "SCALAR",
                     "DevLong64", [1, 0]],
            "float": ["SELECT pid FROM device limit 1", "SCALAR",
                      "DevLong64", [1, 0]],
            #            "float":["SELECT pid FROM device limit 1",
            # "SCALAR","DevDouble",[1,0]],
            "str": ["SELECT name FROM device limit 1", "SCALAR",
                    "DevString", [1, 0]],
            "unicode": ["SELECT name FROM device limit 1", "SCALAR",
                        "DevString", [1, 0]],
            #            "bool":["SELECT exported FROM device limit 1",
            # "SCALAR","DevBoolean",[1,0]],
            "bool": ["SELECT exported FROM device limit 1", "SCALAR",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchone()[0]
            cursor.close()

            ds = DBaseSource()
            self.setsource(ds)
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
            "int": ["SELECT pid FROM device limit 1", "SPECTRUM",
                    "DevLong64", [1, 0]],
            "long": ["SELECT pid FROM device limit 1", "SPECTRUM",
                     "DevLong64", [1, 0]],
            "float": ["SELECT pid FROM device limit 1", "SPECTRUM",
                      "DevLong64", [1, 0]],
            #            "float":["SELECT pid FROM device limit 1",
            # "SPECTRUM","DevDouble",[1,0]],
            "str": ["SELECT name FROM device limit 1", "SPECTRUM",
                    "DevString", [1, 0]],
            "unicode": ["SELECT name FROM device limit 1", "SPECTRUM",
                        "DevString", [1, 0]],
            #            "bool":["SELECT exported FROM device limit 1",
            # "SPECTRUM","DevBoolean",[1,0]],
            "bool": ["SELECT exported FROM device limit 1", "SPECTRUM",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchone()
            cursor.close()

            arr[a][3][0] = len(value)

            ds = DBaseSource()
            self.setsource(ds)
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
            "int": ["SELECT pid,exported FROM device limit 1", "SPECTRUM",
                    "DevLong64", [1, 0]],
            "long": ["SELECT pid,exported FROM device limit 1", "SPECTRUM",
                     "DevLong64", [1, 0]],
            "float": ["SELECT pid,name FROM device limit 1", "SPECTRUM",
                      "DevLong64", [1, 0]],
            #            "float":["SELECT pid,exported FROM device limit 1",
            # "SPECTRUM","DevDouble",[1,0]],
            "str": ["SELECT name,name FROM device limit 1", "SPECTRUM",
                    "DevString", [1, 0]],
            "unicode": ["SELECT name,pid FROM device limit 1", "SPECTRUM",
                        "DevString", [1, 0]],
            #            "bool":["SELECT exported,pid FROM device limit 1",
            # "SPECTRUM","DevBoolean",[1,0]],
            "bool": ["SELECT exported,pid FROM device limit 1", "SPECTRUM",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchall()
            cursor.close()

            arr[a][3] = [len(value[0]), 0]

            ds = DBaseSource()
            self.setsource(ds)
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
            "int": ["SELECT pid FROM device limit 4", "SPECTRUM",
                    "DevLong64", [1, 0]],
            "long": ["SELECT pid FROM device limit 4", "SPECTRUM",
                     "DevLong64", [1, 0]],
            "float": ["SELECT pid FROM device limit 4", "SPECTRUM",
                      "DevLong64", [1, 0]],
            #            "float":["SELECT pid FROM device limit 4",
            # "SPECTRUM","DevDouble",[1,0]],
            "str": ["SELECT name FROM device limit 4", "SPECTRUM",
                    "DevString", [1, 0]],
            "unicode": ["SELECT name FROM device limit 4", "SPECTRUM",
                        "DevString", [1, 0]],
            #            "bool":["SELECT exported FROM device limit 4",
            # "SPECTRUM","DevBoolean",[1,0]],
            "bool": ["SELECT exported FROM device limit 4", "SPECTRUM",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchall()
            cursor.close()

            arr[a][3] = [len(value), 0]

            ds = DBaseSource()
            self.setsource(ds)
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
            "int": ["SELECT pid FROM device limit 4", "IMAGE", "DevLong64",
                    [1, 0]],
            "long": ["SELECT pid FROM device limit 4", "IMAGE", "DevLong64",
                     [1, 0]],
            "float": ["SELECT pid FROM device limit 4", "IMAGE", "DevLong64",
                      [1, 0]],
            #            "float":["SELECT pid FROM device limit 4","IMAGE",
            # "DevDouble",[1,0]],
            "str": ["SELECT name FROM device limit 4", "IMAGE", "DevString",
                    [1, 0]],
            "unicode": ["SELECT name FROM device limit 4", "IMAGE",
                        "DevString", [1, 0]],
            #            "bool":["SELECT exported FROM device limit 4",
            # "IMAGE","DevBoolean",[1,0]],
            "bool": ["SELECT exported FROM device limit 4", "IMAGE",
                     "DevLong64", [1, 0]],
        }

        for a in arr:
            cursor = self._mydb.cursor()
            cursor.execute(arr[a][0])
            value = cursor.fetchall()
            cursor.close()

            arr[a][3] = [len(value), len(value[0])]

            ds = DBaseSource()
            self.setsource(ds)
            ds.query = arr[a][0]
            ds.dbtype = self.__dbtype
            ds.format = arr[a][1]
            ds.dbname = self.__dbname
            dt = ds.getData()

            self.checkData(dt, arr[a][1], value, arr[a][2], arr[a][3])


if __name__ == '__main__':
    unittest.main()
