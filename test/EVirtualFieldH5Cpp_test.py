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
# \file ELinkTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct
import json
import numpy as np

try:
    from TstDataSource import TstDataSource
except Exception:
    from .TstDataSource import TstDataSource

try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker

from nxswriter.FElement import FElement
# from nxswriter.ELink import ELink
from nxswriter.EField import EField
from nxswriter.EVirtualField import (
    EVirtualField, EVirtualDataMap, EVirtualSourceView)
from nxswriter.H5Elements import EDim
from nxswriter.H5Elements import EDimensions
from nxswriter.H5Elements import ESelection
from nxswriter.H5Elements import ESlice
from nxswriter.H5Elements import ESlab
from nxswriter.EGroup import EGroup
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile
# from nxswriter.Errors import XMLSettingSyntaxError
# from nxswriter.FetchNameHandler import TNObject

from nxstools import filewriter as FileWriter
from nxstools import h5cppwriter as H5CppWriter


# from  xml.sax import SAXParseException

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class EVirtualFieldH5CppTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._fname2 = "test2.h5"
        self._nxFile = None
        self._eFile = None
        self._unlimited = 18446744073709551615

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"name": "testField", "units": "m", "type": "NX_INT"}
        self._fattrs2 = {"name": "testField2", "units": "m", "type": "NX_INT"}
        self._fattrs3 = {"name": "testField3", "units": "m", "type": "NX_INT"}
        self._gattrs = {"name": "testGroup", "type": "NXentry"}
        self._vattrs = {"name": "test_virtual_field", "type": "NX_INT"}
        self._dmrank1 = {"rank": 1}
        self._dmrank2 = {"rank": 2}
        self._di1vl1 = {"index": "1", "value": "1"}
        self._di1vl2 = {"index": "1", "value": "2"}
        self._di1vl3 = {"index": "1", "value": "3"}
        self._di1vl4 = {"index": "1", "value": "4"}
        self._di1vl6 = {"index": "1", "value": "6"}
        self._di2vl4 = {"index": "2", "value": "4"}
        self._di2vl12 = {"index": "2", "value": "12"}
        self._sl1_n_u = {"index": "1",  "stop": "%s" % self._unlimited}
        self._sl1_n_n = {"index": "1"}
        self._sl2_n_n = {"index": "2"}
        self._sl1_0_1 = {"index": "1", "start": "0", "stop": "1"}
        self._sl1_0_2 = {"index": "1", "start": "0", "stop": "2"}
        self._sl1_1_2 = {"index": "1", "start": "1", "stop": "2"}
        self._sl1_2_3 = {"index": "1", "start": "2", "stop": "3"}
        self._sl1_2_4 = {"index": "1", "start": "2", "stop": "4"}
        self._sl1_4_6 = {"index": "1", "start": "4", "stop": "6"}
        self._sl2_0_4 = {"index": "2", "start": "0", "stop": "4"}
        self._sl2_4_8 = {"index": "2", "start": "4", "stop": "8"}
        self._sh1o0bu = {"index": "1", "offset": "0",
                         "block": "%s" % self._unlimited}
        self._sh1o0b2 = {"index": "1", "offset": "0", "block": "2"}
        self._sh1o2b1 = {"index": "1", "offset": "2", "block": "1"}
        self._sh1o4b2 = {"index": "1", "offset": "4", "block": "2"}
        self._sh2o0b4 = {"index": "2", "offset": "0", "block": "4"}
        self._sh2o8b4 = {"index": "2", "offset": "8", "block": "4"}

        self._gname = "testGroup"
        self._gtype = "NXentry"
        self._fdname = "testField"
        self._fdtype = "int64"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self._sc = Checker(self)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        FileWriter.writer = H5CppWriter
        self._unlimited = FileWriter.writer.unlimited()
        print("\nsetting up...")
        print("CHECKER SEED = %s" % self._sc.seed)

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
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        li = EVirtualField({}, eFile)
        self.assertTrue(isinstance(li, Element))
        self.assertTrue(isinstance(li, FElement))
        self.assertEqual(li.tagName, "vds")
        self.assertEqual(li.content, [])

        self.assertEqual(li.h5Object, None)

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank1, vf)
        di1 = EDim(self._di1vl1, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "/testField",
                    }
        vm1 = EVirtualDataMap(vmattrs1, vf)
        dm1 = EDimensions(self._dmrank1, vm1)
        di1 = EDim(self._di1vl1, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        self.assertEqual(vm1.store(""), None)
        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertEqual(rv.read(), fi.h5Object.read())

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_default2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank1, fi)
        di1 = EDim(self._di1vl3, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3"]
        fi.store()
        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank1, vf)
        di1 = EDim(self._di1vl3, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "%s:/testField" % self._fname
                    }

        vm1 = EVirtualDataMap(vmattrs1, vf)
        dm1 = EDimensions(self._dmrank1, vm1)
        di1 = EDim(self._di1vl3, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        self.assertEqual(vm1.store(""), None)
        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertTrue((rv.read() == fi.h5Object.read()).all())
        self.assertTrue(
            (np.array([1, 2, 3]) == fi.h5Object.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_three(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank1, fi)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank1, fi2)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank1, fi3)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        di1 = EDim(self._di1vl3, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "%s:/testField" % self._fname
                    }
        vmattrs2 = {"name": "map2",
                    "target": "%s:/testField2" % self._fname
                    }
        vmattrs3 = {"name": "map3",
                    "target": "%s:/testField3" % self._fname
                    }

        vm1 = EVirtualDataMap(vmattrs1, vf)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_0_1, se1)
        sl2 = ESlice(self._sl2_0_4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs2, vf)
        dm1 = EDimensions(self._dmrank2, vm1)
        di1 = EDim(self._di1vl1, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_1_2, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs3, vf)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlab(self._sh1o2b1, se1)
        sl2 = ESlab(self._sh2o0b4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        # self.assertTrue((rv.read() == fi.h5Object.read()).all())
        self.assertTrue(
            (np.array([[1, 2, 3, 4],
                       [11, 12, 13, 14],
                       [21, 22, 23, 24]]) == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_append(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank2, fi)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank2, fi2)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank2, fi3)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24 25 26 27 28"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        di1 = EDim(self._di1vl6, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "%s:/testField" % self._fname
                    }
        vmattrs2 = {"name": "map2",
                    "target": "%s:/testField2" % self._fname
                    }
        vmattrs3 = {"name": "map3",
                    "target": "%s:/testField3" % self._fname
                    }

        vm1 = EVirtualDataMap(vmattrs1, vf)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_0_2, se1)
        sl2 = ESlice(self._sl2_0_4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs2, vf)
        dm1 = EDimensions(self._dmrank2, vm1)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_2_4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs3, vf)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlab(self._sh1o4b2, se1)
        sl2 = ESlab(self._sh2o0b4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertTrue(
            (np.array([[1, 2, 3, 4],
                       [5, 6, 7, 8],
                       [11, 12, 13, 14],
                       [15, 16, 17, 18],
                       [21, 22, 23, 24],
                       [25, 26, 27, 28]]) == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_modules(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank2, fi)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank2, fi2)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank2, fi3)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24 25 26 27 28"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl12, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "%s:/testField" % self._fname
                    }
        vmattrs2 = {"name": "map2",
                    "target": "%s:/testField2" % self._fname
                    }
        vmattrs3 = {"name": "map3",
                    "target": "%s:/testField3" % self._fname
                    }

        vm1 = EVirtualDataMap(vmattrs1, vf)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_0_2, se1)
        sl2 = ESlice(self._sl2_0_4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs2, vf)
        dm1 = EDimensions(self._dmrank2, vm1)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmrank2, vm1)
        sl2 = ESlice(self._sl2_4_8, se1)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs3, vf)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlab(self._sh1o0b2, se1)
        sl2 = ESlab(self._sh2o8b4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertTrue(
            (np.array(
                [[1, 2, 3, 4, 11, 12, 13, 14, 21, 22, 23, 24],
                 [5, 6, 7, 8, 15, 16, 17, 18, 25, 26, 27, 28]])
             == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_modules_unlimited(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_unlimited_vds_supported():
            print("Skip the test: VDS unlimited not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank2, fi)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4\n 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank2, fi2)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14\n 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank2, fi3)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24\n 25 26 27 28"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        # di1 = EDim(self._di1vl2, dm1)
        di1 = EDim(self._di1vl1, dm1)
        di2 = EDim(self._di2vl12, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "%s:/testField" % self._fname
                    }
        vmattrs2 = {"name": "map2",
                    "target": "%s:/testField2" % self._fname
                    }
        vmattrs3 = {"name": "map3",
                    "target": "%s:/testField3" % self._fname
                    }

        vm1 = EVirtualDataMap(vmattrs1, vf)
        dm1 = EDimensions(self._dmrank2, vm1)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_n_u, se1)
        sl2 = ESlice(self._sl2_0_4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)

        sv1 = EVirtualSourceView({}, vm1)
        vse1 = ESelection(self._dmrank2, sv1)
        vsl1 = ESlice(self._sl1_n_u, vse1)
        vsl2 = ESlice(self._sl2_n_n, vse1)
        self.assertEqual(vsl1.store(""), None)
        self.assertEqual(vsl2.store(""), None)
        self.assertEqual(vse1.store(""), None)
        self.assertEqual(sv1.store(""), None)

        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs2, vf)
        dm1 = EDimensions(self._dmrank2, vm1)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_n_u, se1)
        sl2 = ESlice(self._sl2_4_8, se1)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)

        sv1 = EVirtualSourceView({}, vm1)
        vse1 = ESelection(self._dmrank2, sv1)
        vsl1 = ESlice(self._sl1_n_u, vse1)
        vsl2 = ESlice(self._sl2_n_n, vse1)
        self.assertEqual(vsl1.store(""), None)
        self.assertEqual(vsl2.store(""), None)
        self.assertEqual(vse1.store(""), None)
        self.assertEqual(sv1.store(""), None)

        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs3, vf)
        dm1 = EDimensions(self._dmrank2, vm1)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmrank2, vm1)
        # sl1 = ESlab(self._sh1o0b2, se1)
        sl1 = ESlab(self._sh1o0bu, se1)
        sl2 = ESlab(self._sh2o8b4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)

        sv1 = EVirtualSourceView({}, vm1)
        vse1 = ESelection(self._dmrank2, sv1)
        vsl1 = ESlice(self._sl1_n_u, vse1)
        vsl2 = ESlice(self._sl2_n_n, vse1)
        self.assertEqual(vsl1.store(""), None)
        self.assertEqual(vsl2.store(""), None)
        self.assertEqual(vse1.store(""), None)
        self.assertEqual(sv1.store(""), None)

        self.assertEqual(vm1.store(""), None)

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        # print("rEAD", rv.read())
        self.assertTrue(
            (np.array(
                [[1, 2, 3, 4, 11, 12, 13, 14, 21, 22, 23, 24],
                 [5, 6, 7, 8, 15, 16, 17, 18, 25, 26, 27, 28]])
             == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_modules_unlimited_min(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_unlimited_vds_supported():
            print("Skip the test: VDS unlimited not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank2, fi)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4\n 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank2, fi2)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14\n 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank2, fi3)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24\n 25 26 27 28"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        # di1 = EDim(self._di1vl2, dm1)
        di1 = EDim(self._di1vl1, dm1)
        di2 = EDim(self._di2vl12, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "%s:/testField" % self._fname
                    }
        vmattrs2 = {"name": "map2",
                    "target": "%s:/testField2" % self._fname
                    }
        vmattrs3 = {"name": "map3",
                    "target": "%s:/testField3" % self._fname
                    }

        vm1 = EVirtualDataMap(vmattrs1, vf)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_n_u, se1)
        sl2 = ESlice(self._sl2_0_4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)

        sv1 = EVirtualSourceView({}, vm1)
        vse1 = ESelection(self._dmrank2, sv1)
        vsl1 = ESlice(self._sl1_n_u, vse1)
        vsl2 = ESlice(self._sl2_n_n, vse1)
        self.assertEqual(vsl1.store(""), None)
        self.assertEqual(vsl2.store(""), None)
        self.assertEqual(vse1.store(""), None)
        self.assertEqual(sv1.store(""), None)

        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs2, vf)
        se1 = ESelection(self._dmrank2, vm1)
        sl1 = ESlice(self._sl1_n_u, se1)
        sl2 = ESlice(self._sl2_4_8, se1)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)

        sv1 = EVirtualSourceView({}, vm1)
        vse1 = ESelection(self._dmrank2, sv1)
        vsl1 = ESlice(self._sl1_n_u, vse1)
        vsl2 = ESlice(self._sl2_n_n, vse1)
        self.assertEqual(vsl1.store(""), None)
        self.assertEqual(vsl2.store(""), None)
        self.assertEqual(vse1.store(""), None)
        self.assertEqual(sv1.store(""), None)

        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs3, vf)
        se1 = ESelection(self._dmrank2, vm1)
        # sl1 = ESlab(self._sh1o0b2, se1)
        sl1 = ESlab(self._sh1o0bu, se1)
        sl2 = ESlab(self._sh2o8b4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)

        sv1 = EVirtualSourceView({}, vm1)
        vse1 = ESelection(self._dmrank2, sv1)
        vsl1 = ESlice(self._sl1_n_u, vse1)
        vsl2 = ESlice(self._sl2_n_n, vse1)
        self.assertEqual(vsl1.store(""), None)
        self.assertEqual(vsl2.store(""), None)
        self.assertEqual(vse1.store(""), None)
        self.assertEqual(sv1.store(""), None)

        self.assertEqual(vm1.store(""), None)

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        # print("rEAD", rv.read())
        self.assertTrue(
            (np.array(
                [[1, 2, 3, 4, 11, 12, 13, 14, 21, 22, 23, 24],
                 [5, 6, 7, 8, 15, 16, 17, 18, 25, 26, 27, 28]])
             == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_default_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank1, vf)
        di1 = EDim(self._di1vl1, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)

        ds = TstDataSource()
        mjson = json.dumps({
            # "shape": [1],
            "target": "/testField"})
        ds.value = {"rank": 0, "value": mjson,
                    "tangoDType": "DevString", "shape": []}
        vf.source = ds
        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertEqual(rv.read(), fi.h5Object.read())

        self._nxFile.close()
        # os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_default2_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank1, fi)
        di1 = EDim(self._di1vl3, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3"]
        fi.store()
        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank1, vf)
        di1 = EDim(self._di1vl3, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)

        ds = TstDataSource()
        mjson = json.dumps({
            "shape": [3],
            "key": [None],
            "target": "h5file:/%s::/testField" % self._fname})
        ds.value = {"rank": 0, "value": mjson,
                    "tangoDType": "DevString", "shape": []}
        vf.source = ds

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertTrue((rv.read() == fi.h5Object.read()).all())
        self.assertTrue(
            (np.array([1, 2, 3]) == fi.h5Object.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_default3_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank1, fi)
        di1 = EDim(self._di1vl3, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3"]
        fi.store()
        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank1, vf)
        di1 = EDim(self._di1vl3, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)

        # vmattrs1 = {"name": "map1"}
        vm1 = EVirtualDataMap({}, vf)

        ds = TstDataSource()
        mjson = json.dumps({
            "shape": [3],
            "key": [None],
            "target": "%s://testField" % self._fname})
        ds.value = {"rank": 0, "value": mjson,
                    "tangoDType": "DevString", "shape": []}
        vm1.source = ds
        vm1.strategy = 'STEP'

        self.assertEqual(vm1.store(""), ('STEP', None))

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vm1.run(), None)
        self.assertEqual(vf.run(), None)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertTrue((rv.read() == fi.h5Object.read()).all())
        self.assertTrue(
            (np.array([1, 2, 3]) == fi.h5Object.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_three_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank1, fi)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank1, fi2)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank1, fi3)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        di1 = EDim(self._di1vl3, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        ds = TstDataSource()
        mjson = json.dumps(
            [
                {
                    "target": "%s:/testField" % self._fname
                },
                {
                    "target": "%s:/testField2" % self._fname
                },
                {
                    "target": "%s:/testField3" % self._fname
                },
             ]
        )

        ds.value = {"rank": 0, "value": mjson,
                    "tangoDType": "DevString", "shape": []}
        vf.source = ds

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        # self.assertTrue((rv.read() == fi.h5Object.read()).all())
        self.assertTrue(
            (np.array([[1, 2, 3, 4],
                       [11, 12, 13, 14],
                       [21, 22, 23, 24]]) == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_three2_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank1, fi)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank1, fi2)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank1, fi3)
        di1 = EDim(self._di1vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        di1 = EDim(self._di1vl3, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vm1 = EVirtualDataMap({}, vf)

        ds = TstDataSource()

        vm1.source = ds
        vm1.strategy = 'STEP'

        self.assertEqual(vm1.store(""), ('STEP', None))
        self.assertEqual(vf.store(""), ('FINAL', None))

        ds.value = {"rank": 0, "value": json.dumps(
            {"target": "h5file:/%s::/testField" % self._fname}),
                    "tangoDType": "DevString", "shape": []}
        self.assertEqual(vm1.run(), None)
        ds.value = {"rank": 0, "value": json.dumps(
            {"target": "%s:/testField2" % self._fname}),
                    "tangoDType": "DevString", "shape": []}
        self.assertEqual(vm1.run(), None)
        ds.value = {"rank": 0, "value": json.dumps(
            {"target": "%s:/testField3" % self._fname}),
                    "tangoDType": "DevString", "shape": []}

        self.assertEqual(vm1.run(), None)
        self.assertEqual(vf.run(), None)

        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        # self.assertTrue((rv.read() == fi.h5Object.read()).all())
        self.assertTrue(
            (np.array([[1, 2, 3, 4],
                       [11, 12, 13, 14],
                       [21, 22, 23, 24]]) == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_append_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank2, fi)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank2, fi2)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank2, fi3)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24 25 26 27 28"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        di1 = EDim(self._di1vl6, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        ds = TstDataSource()
        vf.source = ds

        self.assertEqual(vf.store(""), ('FINAL', None))

        mjson = json.dumps(
            [
                {
                    "target": "%s:/testField" % self._fname,
                    "key": [[0, 2], [0, 4]]
                },
                {
                    "target": "%s:/testField2" % self._fname,
                    "shape": [2, 4], "key": [[2, 4], None]
                },
                {
                    "target": "%s:/testField3" % self._fname,
                    "key": [[4, 2, 1, 1], [0, 4, 1, 1]]
                },
             ]
        )

        ds.value = {"rank": 0, "value": mjson,
                    "tangoDType": "DevString", "shape": []}

        self.assertEqual(vf.run(), None)
        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertTrue(
            (np.array([[1, 2, 3, 4],
                       [5, 6, 7, 8],
                       [11, 12, 13, 14],
                       [15, 16, 17, 18],
                       [21, 22, 23, 24],
                       [25, 26, 27, 28]]) == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_modules_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank2, fi)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank2, fi2)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank2, fi3)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24 25 26 27 28"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl12, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vm1 = EVirtualDataMap({}, vf)

        ds = TstDataSource()
        mjson = json.dumps([
            {
                "target": "%s://testField" % self._fname,
                "key": [[0, 2], [0, 4]],
            },
            {
                "target": "%s://testField2" % self._fname,
                "shape": [2, 4],
                "key": [None, [4, 8]],
            },
            {
                "target": "%s://testField3" % self._fname,
                "key": [[0, 2, 1, 1], [8, 4, 1, 1]],
            },
        ])
        ds.value = {"rank": 0, "value": mjson,
                    "tangoDType": "DevString", "shape": []}
        vm1.source = ds
        vm1.strategy = 'INIT'

        self.assertEqual(vm1.store(""), ('INIT', None))
        self.assertEqual(vf.store(""), ('FINAL', None))

        self.assertEqual(vm1.run(), None)

        self.assertEqual(vf.run(), None)
        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertTrue(
            (np.array(
                [[1, 2, 3, 4, 11, 12, 13, 14, 21, 22, 23, 24],
                 [5, 6, 7, 8, 15, 16, 17, 18, 25, 26, 27, 28]])
             == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_modules_unlimited_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not FileWriter.writer.is_unlimited_vds_supported():
            print("Skip the test: VDS unlimited not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_b.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fi = EField(self._fattrs, eFile)
        dm1 = EDimensions(self._dmrank2, fi)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4\n 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmrank2, fi2)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14\n 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmrank2, fi3)
        di1 = EDim(self._di1vl2, dm1)
        di2 = EDim(self._di2vl4, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi3.content = ["21 22 23 24\n 25 26 27 28"]
        fi3.store()

        self._nxFile2 = FileWriter.create_file(
            self._fname2, overwrite=True).root()
        eFile2 = EFile({}, None, self._nxFile2)
        gr = EGroup(self._gattrs, eFile2)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmrank2, vf)
        # di1 = EDim(self._di1vl2, dm1)
        di1 = EDim(self._di1vl1, dm1)
        di2 = EDim(self._di2vl12, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "%s:/testField" % self._fname
                    }
        vmattrs2 = {"name": "map2",
                    "target": "%s:/testField2" % self._fname
                    }
        vmattrs3 = {"name": "map3",
                    "target": "%s:/testField3" % self._fname
                    }

        vm1 = EVirtualDataMap(vmattrs1, vf)
        ds1 = TstDataSource()
        vm1.source = ds1
        vm1.strategy = 'INIT'
        self.assertEqual(vm1.store(""), ('INIT', None))

        vm2 = EVirtualDataMap(vmattrs2, vf)
        ds2 = TstDataSource()
        vm2.source = ds2
        vm2.strategy = 'INIT'
        self.assertEqual(vm2.store(""), ('INIT', None))

        vm3 = EVirtualDataMap(vmattrs3, vf)
        ds3 = TstDataSource()
        vm3.source = ds3
        vm3.strategy = 'INIT'
        self.assertEqual(vm3.store(""), ('INIT', None))

        self.assertEqual(vf.store(""), ('FINAL', None))

        mjson = json.dumps({
            "key": [[None, self._unlimited], [0, 4]],
            "sourcekey": [[None, self._unlimited], [None, None]],
        })
        ds1.value = {"rank": 0, "value": mjson,
                     "tangoDType": "DevString", "shape": []}

        mjson = json.dumps({
            "key": [[None, self._unlimited], [4, 8]],
            "sourcekey": [[None, self._unlimited], [None, None]],
        })
        ds2.value = {"rank": 0, "value": mjson,
                     "tangoDType": "DevString", "shape": []}

        mjson = json.dumps({
            "key": [[0, self._unlimited, 1, 1], [8, 4, 1, 1]],
            "sourcekey": [[None, self._unlimited], [None, None]],
        })
        ds3.value = {"rank": 0, "value": mjson,
                     "tangoDType": "DevString", "shape": []}

        self.assertEqual(vm1.run(), None)
        self.assertEqual(vm2.run(), None)
        self.assertEqual(vm3.run(), None)

        self.assertEqual(vf.run(), None)

        if vf.error:
            print(vf.error)

        rv = gr.h5Object.open("test_virtual_field")
        # print("rEAD", rv.read())
        self.assertTrue(
            (np.array(
                [[1, 2, 3, 4, 11, 12, 13, 14, 21, 22, 23, 24],
                 [5, 6, 7, 8, 15, 16, 17, 18, 25, 26, 27, 28]])
             == rv.read()).all())

        self._nxFile.close()
        self._nxFile2.close()
        os.remove(self._fname)
        os.remove(self._fname2)


if __name__ == '__main__':
    unittest.main()
