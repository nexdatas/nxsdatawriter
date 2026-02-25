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
# \file EFileTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct


from nxswriter.FElement import FElement, FElementWithAttr
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile

from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class EFileH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None
        self._fattrs = {"short_name": "test", "units": "m"}
        self._gname = "testFile"
        self._gtype = "NXentry"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")
        FileWriter.writer = H5PYWriter

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

    # default constructor test
    # \brief It tests default settings
    def test_default_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        el = EFile({}, None, None)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, 'file')
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.source, None)
        self.assertEqual(el.error, None)
        self.assertEqual(el.h5Object, None)
        self.assertEqual(el.last, None)

    # default constructor test
    # \brief It tests default settings
    def test_constructor_nx(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        el = EFile({}, None, self._nxFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertEqual(el.tagName, 'file')
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.source, None)
        self.assertEqual(el.error, None)
        self.assertEqual(el._tagAttrs, {})
        self.assertEqual(type(el.h5Object), H5PYWriter.H5PYGroup)

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_constructor_attrs(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        el = EFile(self._fattrs, None, self._nxFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertEqual(el.tagName, 'file')
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.last, None)
        self.assertEqual(el.source, None)
        self.assertEqual(el.error, None)
        for k in self._fattrs:
            self.assertEqual(el._tagAttrs[k], self._fattrs[k])

        self.assertEqual(el._tagAttrs, self._fattrs)
        self.assertEqual(type(el.h5Object), H5PYWriter.H5PYGroup)

        self._nxFile.close()
        os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
