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
import numpy as np

# try:
#     from TstDataSource import TstDataSource
# except Exception:
#     from .TstDataSource import TstDataSource

try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker

from nxswriter.FElement import FElement
# from nxswriter.ELink import ELink
from nxswriter.EField import EField
from nxswriter.EVirtualField import EVirtualField, EVirtualDataMap
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

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"name": "testField", "units": "m", "type": "NX_INT"}
        self._fattrs2 = {"name": "testField2", "units": "m", "type": "NX_INT"}
        self._fattrs3 = {"name": "testField3", "units": "m", "type": "NX_INT"}
        self._gattrs = {"name": "testGroup", "type": "NXentry"}
        self._vattrs = {"name": "test_virtual_field", "type": "NX_INT"}
        self._dmattrs1 = {"rank": 1}
        self._dmattrs3 = {"rank": 2}
        self._diattrs1 = {"index": "1", "value": "1"}
        self._diattrs2 = {"index": "1", "value": "3"}
        self._diattrs3a = {"index": "1", "value": "4"}
        self._diattrs3b = {"index": "2", "value": "4"}
        self._diattrs4 = {"index": "1", "value": "2"}
        self._diattrs5 = {"index": "2", "value": "4"}
        self._diattrs6 = {"index": "1", "value": "6"}
        self._slattrs1 = {"index": "1", "start": "0", "stop": "1"}
        self._slattrs2 = {"index": "1", "start": "1", "stop": "2"}
        self._slattrs3 = {"index": "1", "start": "2", "stop": "3"}
        self._slattrs3b = {"index": "1", "offset": "2", "block": "1"}
        self._slattrs3c = {"index": "2", "offset": "0", "block": "4"}
        self._slattrs3d = {"index": "1", "offset": "4", "block": "2"}
        self._slattrs4 = {"index": "2", "start": "0", "stop": "4"}
        self._slattrs5 = {"index": "1", "start": "0", "stop": "2"}
        self._slattrs6 = {"index": "1", "start": "2", "stop": "4"}
        self._slattrs7 = {"index": "1", "start": "4", "stop": "6"}

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

        dm1 = EDimensions(self._dmattrs1, vf)
        di1 = EDim(self._diattrs1, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "/testField",
                    }
        vm1 = EVirtualDataMap(vmattrs1, vf)
        dm1 = EDimensions(self._dmattrs1, vm1)
        di1 = EDim(self._diattrs1, dm1)
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
        dm1 = EDimensions(self._dmattrs1, fi)
        di1 = EDim(self._diattrs2, dm1)
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

        dm1 = EDimensions(self._dmattrs1, vf)
        di1 = EDim(self._diattrs2, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    "target": "%s:/testField" % self._fname
                    }
        vm1 = EVirtualDataMap(vmattrs1, vf)
        dm1 = EDimensions(self._dmattrs1, vm1)
        di1 = EDim(self._diattrs2, dm1)
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
        dm1 = EDimensions(self._dmattrs1, fi)
        di1 = EDim(self._diattrs3a, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmattrs1, fi2)
        di1 = EDim(self._diattrs3a, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmattrs1, fi3)
        di1 = EDim(self._diattrs3a, dm1)
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

        dm1 = EDimensions(self._dmattrs3, vf)
        di1 = EDim(self._diattrs2, dm1)
        di2 = EDim(self._diattrs3b, dm1)
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
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlice(self._slattrs1, se1)
        sl2 = ESlice(self._slattrs4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs2, vf)
        dm1 = EDimensions(self._dmattrs3, vm1)
        di1 = EDim(self._diattrs1, dm1)
        di2 = EDim(self._diattrs3b, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlice(self._slattrs2, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs3, vf)
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlab(self._slattrs3b, se1)
        sl2 = ESlab(self._slattrs3c, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
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
        dm1 = EDimensions(self._dmattrs3, fi)
        di1 = EDim(self._diattrs4, dm1)
        di2 = EDim(self._diattrs5, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmattrs3, fi2)
        di1 = EDim(self._diattrs4, dm1)
        di2 = EDim(self._diattrs5, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmattrs3, fi3)
        di1 = EDim(self._diattrs4, dm1)
        di2 = EDim(self._diattrs5, dm1)
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

        dm1 = EDimensions(self._dmattrs3, vf)
        di1 = EDim(self._diattrs6, dm1)
        di2 = EDim(self._diattrs5, dm1)
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
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlice(self._slattrs5, se1)
        sl2 = ESlice(self._slattrs4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs2, vf)
        dm1 = EDimensions(self._dmattrs3, vm1)
        di1 = EDim(self._diattrs4, dm1)
        di2 = EDim(self._diattrs3b, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlice(self._slattrs6, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs3, vf)
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlab(self._slattrs3d, se1)
        sl2 = ESlab(self._slattrs3c, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
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
    def ttest_createVDS_unlimited(self):
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
        dm1 = EDimensions(self._dmattrs3, fi)
        di1 = EDim(self._diattrs4, dm1)
        di2 = EDim(self._diattrs5, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi.content = ["1 2 3 4 5 6 7 8"]
        fi.store()

        fi2 = EField(self._fattrs2, eFile)
        dm1 = EDimensions(self._dmattrs3, fi2)
        di1 = EDim(self._diattrs4, dm1)
        di2 = EDim(self._diattrs5, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        fi2.content = ["11 12 13 14 15 16 17 18"]
        fi2.store()

        fi3 = EField(self._fattrs3, eFile)
        dm1 = EDimensions(self._dmattrs3, fi3)
        di1 = EDim(self._diattrs4, dm1)
        di2 = EDim(self._diattrs5, dm1)
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

        dm1 = EDimensions(self._dmattrs3, vf)
        di1 = EDim(self._diattrs6, dm1)
        di2 = EDim(self._diattrs5, dm1)
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
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlice(self._slattrs5, se1)
        sl2 = ESlice(self._slattrs4, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs2, vf)
        dm1 = EDimensions(self._dmattrs3, vm1)
        di1 = EDim(self._diattrs4, dm1)
        di2 = EDim(self._diattrs3b, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(di2.store(""), None)
        self.assertEqual(dm1.store(""), None)
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlice(self._slattrs6, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        vm1 = EVirtualDataMap(vmattrs3, vf)
        se1 = ESelection(self._dmattrs3, vm1)
        sl1 = ESlab(self._slattrs3d, se1)
        sl2 = ESlab(self._slattrs3c, se1)
        self.assertEqual(sl1.store(""), None)
        self.assertEqual(sl2.store(""), None)
        self.assertEqual(se1.store(""), None)
        self.assertEqual(vm1.store(""), None)

        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)
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


if __name__ == '__main__':
    unittest.main()
