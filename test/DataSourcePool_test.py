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
# \file DataSourcePoolTest.py
# unittests for field Tags running Tango Server
#
import unittest
import sys
import struct
import json

import nxswriter


from nxswriter.DataSourcePool import DataSourcePool
from nxswriter.TangoSource import TangoSource
from nxswriter.DBaseSource import DBaseSource
from nxswriter.ClientSource import ClientSource

import _thread as thread

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# Wrong DataSource
class W0DS(object):
    pass

# Wrong DataSource


class W1DS(object):
    # setup method

    def setup(self):
        pass

# Wrong DataSource


class W2DS(object):
    # setup method

    def setup(self):
        pass

    # getData method
    def getData(self):
        pass


# Wrong DataSource
class W3DS(object):
    # setup method

    def setup(self):
        pass

    # getData method
    def getData(self):
        pass

    # isValid method
    def isValid(self):
        pass


# Wrong DataSource
class W4DS(object):
    # setup method

    def setup(self):
        pass

    # getData method
    def getData(self):
        pass

    # isValid method
    def isValid(self):
        pass

    # str method
    def __str__(self):
        pass


# test fixture
class DataSourcePoolTest(unittest.TestCase):

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

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")

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

        el = DataSourcePool()
        self.assertTrue(isinstance(el, object))

        el = DataSourcePool(json.loads("{}"))
        self.assertTrue(isinstance(el, object))

        jsn = json.loads('{"datasources":{"CL":"DataSources.Source"}}')
        self.myAssertRaise(AttributeError, DataSourcePool, jsn)

        jsn = json.loads('{"datasources":{"CL":"DSources.ClientSource"}}')
        self.myAssertRaise(ImportError, DataSourcePool, jsn)

        el = DataSourcePool(
            json.loads(
                '{"datasources":{"CL":'
                '"nxswriter.ClientSource.ClientSource"}}'))

    # hasDataSource test
    # \brief It tests default settings
    def test_hasDataSource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DataSourcePool()
        self.assertEqual(el.common, {})
        self.assertEqual(el.counter, 0)
        self.assertEqual(el.canfail, False)
        self.assertEqual(type(el.lock), thread.LockType)
        self.assertTrue(el.hasDataSource("TANGO"))
        self.assertTrue(el.hasDataSource("CLIENT"))
        self.assertTrue(el.hasDataSource("DB"))
        self.assertTrue(not el.hasDataSource("DBB"))
        self.assertTrue(not el.hasDataSource("CL"))

        el = DataSourcePool(
            json.loads(
                '{"datasources":{"CL":'
                '"nxswriter.ClientSource.ClientSource"}}'))
        self.assertTrue(el.hasDataSource("TANGO"))
        self.assertTrue(el.hasDataSource("CLIENT"))
        self.assertTrue(el.hasDataSource("DB"))
        self.assertTrue(not el.hasDataSource("DBB"))
        self.assertTrue(el.hasDataSource("CL"))

    # get method test
    # \brief It tests default settings
    def test_get(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DataSourcePool()
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("DDB"), None)
        self.assertEqual(el.get("CL"), None)

        el = DataSourcePool(
            json.loads(
                '{"datasources":{"CL":'
                '"nxswriter.ClientSource.ClientSource"}}'))
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("DDB"), None)
        ds = el.get("CL")()
        self.assertTrue(isinstance(ds, ClientSource))

    # append method test
    # \brief It tests default settings
    def test_append(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DataSourcePool()
        el.append(nxswriter.ClientSource.ClientSource, "CL")
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("DDB"), None)
        ds = el.get("CL")()
        self.assertTrue(isinstance(ds, ClientSource))

        el = DataSourcePool()
        el.append(W0DS, "W0")
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("W0"), None)

        el = DataSourcePool()
        el.append(W1DS, "W0")
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("W0"), None)

        el = DataSourcePool()
        el.append(W2DS, "W0")
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("W0"), None)

        el = DataSourcePool()
        el.append(W3DS, "W0")
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        ds = el.get("W0")()
        self.assertTrue(isinstance(ds, W3DS))

        el = DataSourcePool()
        el.append(W4DS, "W0")
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        ds = el.get("W0")()
        self.assertTrue(isinstance(ds, W4DS))

    # append pop test
    # \brief It tests default settings
    def test_pop(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DataSourcePool()
        el.pop("CL")
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("CL"), None)
        el.pop("TANGO")
        self.assertEqual(el.get("TANGO"), None)
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("CL"), None)

        el = DataSourcePool()
        el.append(W4DS, "W0")
        ds = el.get("W0")()
        self.assertTrue(isinstance(ds, W4DS))
        ds = el.get("TANGO")()
        self.assertTrue(isinstance(ds, TangoSource))
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("CL"), None)
        el.pop("TANGO")
        el.pop("W0")
        self.assertEqual(el.get("TANGO"), None)
        ds = el.get("DB")()
        self.assertTrue(isinstance(ds, DBaseSource))
        ds = el.get("CLIENT")()
        self.assertTrue(isinstance(ds, ClientSource))
        self.assertEqual(el.get("CL"), None)
        self.assertEqual(el.get("W0"), None)


if __name__ == '__main__':
    unittest.main()
