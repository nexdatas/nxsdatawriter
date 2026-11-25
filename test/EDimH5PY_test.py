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
# \file EDimTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii

from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter


from nxswriter.EField import EField
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile
from nxswriter.H5Elements import EDim
from nxswriter.H5Elements import EDimensions

try:
    from TstDataSource import TstDataSource
except Exception:
    from .TstDataSource import TstDataSource


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class EDimTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "dim"
        self._fname = "test.h5"
        self._nxDoc = None
        self._eDoc = None
        self._fattrs = {"name": "test", "units": "m"}
        self._fattrs2 = {"fname": "test", "units": "m"}
        self._fattrs3 = {"fname": "test", "units": "m", "rank": "2"}
        self._fattrs4 = {"fname": "test", "units": "m", "rank": "1"}
        self._attrs1 = {"index": "1", "value": "14"}
        self._attrs2 = {"index": "2", "value": "22"}
        self._attrs3 = {"value": "2"}
        self._attrs4 = {"index": "2"}
        self._attrs5 = {"index": "1"}
        self._gname = "testDoc"
        self._gtype = "NXentry"

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)
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
        el = EDim({}, None)
        self.assertTrue(isinstance(el, Element))
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.last, None)

    # store method test
    # \brief It tests executing store method
    def test_store(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        el = Element(self._tfname, self._fattrs2)
        el2 = EDim(self._fattrs2, el)
        self.assertEqual(el2.tagName, self._tfname)
        self.assertEqual(el2.content, [])
        self.assertEqual(el2._tagAttrs, self._fattrs2)
        self.assertEqual(el2.doc, "")
        self.assertEqual(el2.store(""), None)
        self.assertEqual(el2.last, el)
        self.assertEqual(el2.store("<tag/>"), None)

    # last method test
    # \brief It tests executing _lastObject method
    def test_last(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs3, el)
        el2 = EDimensions(self._fattrs3, fi)
        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs3)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "2")

        nxFile.close()
        os.remove(fname)

    # last method test
    # \brief It tests executing _lastObject method
    def test_last_index(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs4, fi)
        el3 = EDim(self._attrs1, el2)
        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "1")
        self.assertEqual(el3._beforeLast().lengths, {'1': '14'})
        self.assertEqual(fi.lengths, {'1': '14'})
        self.assertEqual(fi.rank, "1")

        nxFile.close()
        os.remove(fname)

    # last method test
    # \brief It tests executing _lastObject method
    def test_last_index2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs3, fi)
        el3 = EDim(self._attrs1, el2)
        # el4 =
        EDim(self._attrs2, el2)
        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "2")
        self.assertEqual(el3._beforeLast().lengths, {'1': '14', '2': '22'})
        self.assertEqual(fi.lengths, {'1': '14', '2': '22'})
        self.assertEqual(fi.rank, "2")

        nxFile.close()
        os.remove(fname)

    # last method test
    # \brief It tests executing _lastObject method
    def test_last_noindex(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs3, fi)
        el3 = EDim(self._attrs3, el2)
        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "2")
        self.assertEqual(el3._beforeLast().lengths, {})
        self.assertEqual(fi.lengths, {})
        self.assertEqual(fi.rank, "2")

        nxFile.close()
        os.remove(fname)

    # _last method test
    # \brief It tests executing _lastObject method
    def test_last_novalue(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs4, fi)
        el3 = EDim(self._attrs3, el2)
        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "1")
        self.assertEqual(el3._beforeLast().lengths, {})
        self.assertEqual(fi.lengths, {})
        self.assertEqual(fi.rank, "1")

        nxFile.close()
        os.remove(fname)

    # last method test
    # \brief It tests executing _lastObject method
    def test_store_last_index(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs4, fi)
        el3 = EDim(self._attrs5, el2)
        ds = TstDataSource()
        ds.value0d = self.__rnd.randint(1, 10)
        el3.source = ds
        el3.store()
        print(el3._beforeLast().lengths)
        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "1")
        self.assertEqual(el3._beforeLast().lengths, {'1': '%s' % ds.value0d})
        self.assertEqual(fi.lengths, {'1': '%s' % ds.value0d})
        self.assertEqual(fi.rank, "1")

        nxFile.close()
        os.remove(fname)

    # last method test
    # \brief It tests executing _lastObject method
    def test_store_last_index2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs3, fi)
        el3 = EDim(self._attrs5, el2)
        ds = TstDataSource()
        ds.value0d = self.__rnd.randint(1, 10)
        el3.source = ds
        el4 = EDim(self._attrs4, el2)
        ds2 = TstDataSource()
        ds2.value0d = self.__rnd.randint(1, 10)
        el4.source = ds2
        el3.store()
        el4.store()

        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "2")
        self.assertEqual(el3._beforeLast().lengths,
                         {'1': '%s' % ds.value0d, '2': '%s' % ds2.value0d})
        self.assertEqual(fi.lengths,
                         {'1': '%s' % ds.value0d, '2': '%s' % ds2.value0d})
        self.assertEqual(fi.rank, "2")

        nxFile.close()
        os.remove(fname)

    # last method test
    # \brief It tests executing _lastObject method
    def test_store_last_index2_mixed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs3, fi)
        el3 = EDim(self._attrs5, el2)
        ds = TstDataSource()
        ds.value0d = self.__rnd.randint(1, 10)
        el3.source = ds
        # el4 =
        EDim(self._attrs2, el2)
        el3.store()

        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "2")
        self.assertEqual(el3._beforeLast().lengths,
                         {'1': '%s' % ds.value0d, '2': '22'})
        self.assertEqual(fi.lengths,
                         {'1': '%s' % ds.value0d, '2': '22'})
        self.assertEqual(fi.rank, "2")

        nxFile.close()
        os.remove(fname)

    # last method test
    # \brief It tests executing _lastObject method
    def test_store_last_noindex(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs3, fi)
        el3 = EDim({}, el2)

        ds = TstDataSource()
        ds.value0d = self.__rnd.randint(1, 10)
        el3.source = ds
        el3.store()

        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "2")
        self.assertEqual(el3._beforeLast().lengths, {})
        self.assertEqual(fi.lengths, {})
        self.assertEqual(fi.rank, "2")

        nxFile.close()
        os.remove(fname)

    # _last method test
    # \brief It tests executing _lastObject method
    def test_store_last_novalue(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs4, fi)
        el3 = EDim(self._attrs5, el2)
        ds = TstDataSource()
        ds.value0d = ""
        el3.source = ds
        el3.store()

        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "1")
        self.assertEqual(el3._beforeLast().lengths, {'1': ''})
        self.assertEqual(fi.lengths, {'1': ''})
        self.assertEqual(fi.rank, "1")

        nxFile.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
