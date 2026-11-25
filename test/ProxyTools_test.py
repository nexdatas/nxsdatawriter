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
import threading

try:
    import tango
except Exception:
    import PyTango as tango


try:
    import SimpleServerSetUp
except Exception:
    from . import SimpleServerSetUp


from nxswriter.TangoSource import ProxyTools

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test pool
class pool(object):

    def __init__(self):
        self.common = {}
        self.lock = threading.Lock()
        self.counter = 0

# test fixture


class TangoSourceTest(unittest.TestCase):

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
    def test_proxySetup(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        self.myAssertRaise(RuntimeError, ProxyTools.proxySetup, None)

        self.myAssertRaise(
            Exception, ProxyTools.proxySetup, "stestp09/testss/s3r228")

        dp = ProxyTools.proxySetup("stestp09/testss/s2r228")
        self.assertTrue(isinstance(dp, tango.DeviceProxy))
        self.assertEqual(dp.state(), tango._tango.DevState.ON)
        self.assertEqual(dp.dev_name(), "stestp09/testss/s2r228")

        dp = ProxyTools.proxySetup("stestp09/testss/s1r228")
        self.assertTrue(isinstance(dp, tango.DeviceProxy))
        self.assertEqual(dp.dev_name(), "stestp09/testss/s1r228")
        self.assertEqual(dp.state(), tango._tango.DevState.ON)

    # constructor test
    # \brief It tests default settings
    def test_isProxyValid(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        self.assertEqual(ProxyTools.isProxyValid(None), False)
        self.assertEqual(ProxyTools.isProxyValid(proxy(False)), False)
        self.assertEqual(ProxyTools.isProxyValid(proxy(True)), True)


# test proxy class
class proxy(object):
    # constructor
    # \param if proxy is valid

    def __init__(self, valid):
        self.valid = valid
        pass

    # get proxy state
    def state(self):
        if not self.valid:
            raise Exception("Not valid proxy")
        return "something"

    # ping method
    def ping(self):
        if not self.valid:
            raise Exception("Not valid proxy")
        return "something"


if __name__ == '__main__':
    unittest.main()
