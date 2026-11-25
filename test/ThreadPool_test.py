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
# \file ThreadPoolTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time
import json

from nxswriter.ThreadPool import ThreadPool
from nxswriter.Errors import ThreadError


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# datasource
class Source(object):
    # contructor

    def __init__(self):
        # local json
        self.ljson = None
        # global json
        self.gjson = None
    # sets json string

    def setJSON(self, gjson, ljson=None):
        self.ljson = ljson
        self.gjson = gjson

# H5 object


class H5(object):
    # contructor

    def __init__(self):
        # close flag
        self.closed = False

    # closing method
    def close(self):
        self.closed = True


# class job
class Job(object):
    # contructor

    def __init__(self):
        # counter
        self.counter = 0
        # error
        self.error = None

    # run method
    def run(self):
        self.counter += 1


# class job with error
class EJob(object):
    # contructor

    def __init__(self):
        # counter
        self.counter = 0
        # error
        self.error = None
        # message
        self.message = ("Error", "My Error")
        # canfail flag
        self.canfail = None
        # markfail flag
        self.markfail = 0
        self.error = None

    # run method
    def run(self):
        self.counter += 1
        self.error = self.message

    # run method
    def markFailed(self, error=None):
        self.markfail += 1
        self.error = error

# class job with error


class SOJob(object):
    # contructor

    def __init__(self):
        # counter
        self.counter = 0
        # error
        self.error = None
        # message
        self.message = ("Error", "My Error")
        # datasource
        self.source = Source()
        # datasource
        self.h5Object = H5()

    # run method
    def run(self):
        time.sleep(0.01)
        self.counter += 1


# job without run method
class WJob(object):
    # contructor

    def __init__(self):
        pass


# test fixture
class ThreadPoolTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name": "test", "units": "m"}

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

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
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        nth = self.__rnd.randint(1, 10)
        el = ThreadPool(nth)
        self.assertEqual(el.numberOfThreads, nth)

    # constructor test
    # \brief It tests default settings
    def test_run_append_join_wait(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        nth = self.__rnd.randint(1, 10)
        el = ThreadPool(nth)
        self.assertEqual(el.numberOfThreads, nth)

        jlist = [Job() for c in range(self.__rnd.randint(1, 20))]
        for jb in jlist:
            self.assertEqual(el.append(jb), None)
        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for c in jlist:
            self.assertEqual(c.counter, 1)

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for c in jlist:
            self.assertEqual(c.counter, 2)

        self.assertEqual(el.runAndWait(), None)

        for c in jlist:
            self.assertEqual(c.counter, 3)

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for c in jlist:
            self.assertEqual(c.counter, 4)

        self.assertEqual(el.runAndWait(), None)

        for c in jlist:
            self.assertEqual(c.counter, 5)

    # constructor test
    # \brief It tests default settings
    def test_errors(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        nth = self.__rnd.randint(1, 10)
        el = ThreadPool(nth)
        self.assertEqual(el.numberOfThreads, nth)

        jlist = [EJob() for c in range(self.__rnd.randint(1, 20))]
        for jb in jlist:
            self.assertEqual(el.append(jb), None)

        self.assertEqual(el.checkErrors(), None)

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for c in jlist:
            self.assertEqual(c.counter, 1)

        self.myAssertRaise(ThreadError, el.checkErrors)

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for c in jlist:
            self.assertEqual(c.counter, 2)

        self.assertEqual(el.runAndWait(), None)

        self.myAssertRaise(ThreadError, el.checkErrors)

    # constructor test
    # \brief It tests default settings
    def test_errors_canfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        nth = self.__rnd.randint(1, 10)
        el = ThreadPool(nth)
        self.assertEqual(el.numberOfThreads, nth)

        jlist = [EJob() for c in range(self.__rnd.randint(1, 20))]
        for jb in jlist:
            self.assertEqual(el.append(jb), None)

        self.assertEqual(el.checkErrors(), None)

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for c in jlist:
            self.assertEqual(c.counter, 1)

        self.myAssertRaise(ThreadError, el.checkErrors)

        for jb in jlist:
            self.assertEqual(jb.markfail, 0)
            jb.canfail = True

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for c in jlist:
            self.assertEqual(c.counter, 2)

        self.assertEqual(el.runAndWait(), None)

        el.checkErrors()
        for jb in jlist:
            self.assertEqual(jb.markfail, 1)

    # constructor test
    # \brief It tests default settings
    def test_setJSON(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        gjson = json.loads('{"data":{"a":"1"}}')
        ljson = json.loads('{"data":{"n":2}}')

        nth = self.__rnd.randint(1, 10)
        el = ThreadPool(nth)
        self.assertEqual(el.numberOfThreads, nth)

        jlist = [SOJob() for c in range(self.__rnd.randint(1, 20))]
        for jb in jlist:
            self.assertEqual(el.append(jb), None)

        self.assertEqual(el.setJSON(gjson), el)
        for jb in jlist:
            self.assertEqual(jb.source.gjson, gjson)
            self.assertEqual(jb.source.ljson, None)

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for jb in jlist:
            self.assertEqual(jb.source.gjson, gjson)
            self.assertEqual(jb.source.ljson, None)

        for c in jlist:
            self.assertEqual(c.counter, 1)

        self.assertEqual(el.setJSON(gjson, ljson), el)
        for jb in jlist:
            self.assertEqual(jb.source.gjson, gjson)
            self.assertEqual(jb.source.ljson, ljson)

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for jb in jlist:
            self.assertEqual(jb.counter, 2)
            self.assertEqual(jb.source.gjson, gjson)
            self.assertEqual(jb.source.ljson, ljson)

    # constructor test
    # \brief It tests default settings
    def test_close(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        # gjson = json.loads('{"data":{"a":"1"}}')
        # ljson = json.loads('{"data":{"n":2}}')

        nth = self.__rnd.randint(1, 10)
        el = ThreadPool(nth)
        self.assertEqual(el.numberOfThreads, nth)

        jlist = [SOJob() for c in range(self.__rnd.randint(1, 20))]
        for jb in jlist:
            self.assertEqual(el.append(jb), None)

        for jb in jlist:
            self.assertTrue(not jb.h5Object.closed)

        self.assertEqual(el.run(), None)
        self.assertEqual(el.join(), None)

        for jb in jlist:
            self.assertTrue(not jb.h5Object.closed)

        self.assertEqual(el.close(), None)

        for jb in jlist:
            self.assertTrue(jb.h5Object.closed)


if __name__ == '__main__':
    unittest.main()
