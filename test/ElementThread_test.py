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
# \file ElementThreadTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time
from threading import Thread
from nxswriter.ElementThread import ElementThread

import queue as Queue


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# class job
class Job:
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
class EJob:
    # contructor

    def __init__(self):
        # counter
        self.counter = 0
        # error
        self.error = None
        # message
        self.message = ("Error", "My Error")

    # run method
    def run(self):
        self.counter += 1
        self.error = self.message


# job without run method
class WJob:
    # contructor

    def __init__(self):
        pass


# test fixture
class ElementThreadTest(unittest.TestCase):

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
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

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

        index = self.__rnd.randint(1, 1000)
        el = ElementThread(index, None)
        self.assertEqual(el.index, index)
        self.assertTrue(isinstance(el, Thread))

    # constructor test
    # \brief It tests default settings
    def test_run_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        index = self.__rnd.randint(1, 1000)
        elementQueue = Queue.Queue()

        el = ElementThread(index, elementQueue)
        self.assertEqual(el.index, index)
        self.assertEqual(el.run(), None)

        jlist = [WJob() for c in range(self.__rnd.randint(1, 20))]

        index = self.__rnd.randint(1, 1000)
        elementQueue = Queue.Queue()

        for eth in jlist:
            elementQueue.put(eth)

        el = ElementThread(index, elementQueue)
        self.assertEqual(el.index, index)
        self.assertEqual(el.run(), None)

    # constructor test
    # \brief It tests default settings
    def test_run_jobs(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        jlist = [Job() for c in range(self.__rnd.randint(1, 20))]

        index = self.__rnd.randint(1, 1000)
        elementQueue = Queue.Queue()

        for eth in jlist:
            elementQueue.put(eth)

        el = ElementThread(index, elementQueue)
        self.assertEqual(el.index, index)
        self.assertEqual(el.run(), None)

        for c in jlist:
            self.assertEqual(c.counter, 1)

    # constructor test
    # \brief It tests default settings
    def test_run_jobs_with_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        jlist = [EJob() for c in range(self.__rnd.randint(1, 20))]

        index = self.__rnd.randint(1, 1000)
        elementQueue = Queue.Queue()

        for eth in jlist:
            elementQueue.put(eth)

        el = ElementThread(index, elementQueue)
        self.assertEqual(el.index, index)
        self.assertEqual(el.run(), None)

        for c in jlist:
            self.assertEqual(c.counter, 1)
            self.assertEqual(c.error, c.message)


if __name__ == '__main__':
    unittest.main()
