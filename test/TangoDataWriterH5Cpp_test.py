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
# \file TangoDataWriterTest.py
# unittests for TangoDataWriter
#
import unittest
import os
import sys
import json
import numpy
from xml.sax import SAXParseException

import nxswriter
from nxswriter.TangoDataWriter import TangoDataWriter
import struct

from nxstools import h5cppwriter as H5CppWriter


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture


class TangoDataWriterH5CppTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._scanXmlpart = u"""
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="\u03bcm" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT" name="mca">
          <dimensions rank="1">
            <dim value="2048" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="p09/mca/exp.02"/>
          </datasource>
        </field>
      </group>
    </group>
"""

        self._scanXmlb = """
<definition>
  <group type="NXentry" name="entry%s">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT" name="mca">
          <dimensions rank="1">
            <dim value="2048" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="p09/mca/exp.02"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="/NXentry/NXinstrument/NXdetector/mca" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="%s://entry%s/instrument/detector/counter1" name="cnt1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""

        self._scanXml = """
<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT" name="mca">
          <dimensions rank="1">
            <dim value="2048" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="p09/mca/exp.02"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="/NXentry/NXinstrument/NXdetector/mca" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="%s://entry1/instrument/detector/counter1" name="cnt1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""
        self._scanXml1 = """
<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT" name="mca">
          <dimensions rank="1">
            <dim value="2048" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="p09/mca/exp.02"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="/NXentry/NXinstrument/NXdetector/mca" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="/entry1/instrument/detector/counter1" name="cnt1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""
        self._scanXml2 = """
<definition>
  <group type="NXentry" name="entry1">
    <field units="m" type="NX_CHAR" name="nxrootstr">
      <strategy mode="INIT"/>
      <datasource type="PYEVAL">
        <result name='res2'>
ds.res2 = str(commonblock["__nxroot__"].link.path)</result>
      </datasource>
    </field>
    <field units="m" type="NX_CHAR" name="nxrootpath">
      <strategy mode="INIT"/>
      <datasource type="PYEVAL">
        <result name='res2'>
ds.res2 = (commonblock["__nxroot__"]).link.path.name</result>
      </datasource>
    </field>
    <field units="m" type="NX_CHAR" name="nxrootlink">
      <strategy mode="FINAL"/>
      <datasource type="PYEVAL">
        <result name='res2'>
from pninexus import h5cpp
root = commonblock["__nxroot__"]
en = root.get_group(h5cpp.Path("entry1"))
h5cpp.node.link(target=h5cpp.Path("/entry1/nxrootpath"),
    link_base=en, link_path=h5cpp.Path("mylink"))
ds.res2 = str(True)
        </result>
      </datasource>
    </field>
  </group>
</definition>
"""
        self._scanXml3 = """
<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_INT64" name="image">
          <dimensions rank="2">
            <dim value="100" index="1"/>
            <dim value="200" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="image"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="/NXentry/NXinstrument/NXdetector/image" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="%s://entry1/instrument/detector/counter1" name="cnt1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""
        self._counter = [0.1, 0.2]
        self._mca1 = [e * 0.1 for e in range(2048)]
        self._mca2 = [(float(e) / (100. + e)) for e in range(2048)]
        self._image1 = [[(i + j) for i in range(100)] for j in range(200)]
        self._image2 = [[(i - j) for i in range(100)] for j in range(200)]

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
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

    def myAssertDict(self, dct, dct2, skip=None, parent=None):
        parent = parent or ""
        self.assertTrue(isinstance(dct, dict))
        self.assertTrue(isinstance(dct2, dict))
        if len(list(dct.keys())) != len(list(dct2.keys())):
            print(list(dct.keys()))
            print(list(dct2.keys()))
        self.assertEqual(
            len(list(dct.keys())), len(list(dct2.keys())))
        for k, v in dct.items():
            if parent:
                node = "%s.%s" % (parent, k)
            else:
                node = k
            if k not in dct2.keys():
                print("%s not in %s" % (k, dct2))
            self.assertTrue(k in dct2.keys())
            if not skip or node not in skip:
                if isinstance(v, dict):
                    self.myAssertDict(v, dct2[k], skip, node)
                else:
                    self.assertEqual(v, dct2[k])

    # openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile(self):
        print("Run: %s.test_openFile() " % self.__class__.__name__)
        fname = "test.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            tdw.writer = "h5cpp"
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))

            tdw.openFile()
            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)

            tdw.closeFile()
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))
            self.assertTrue(tdw.getFile() is None)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()

#            print("\nFile attributes:")
            cnt = 0
            for at in f.attributes:
                cnt += 1
#                print(at.name),"=",at[...]
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(5, len(f.attributes))
#            print ""

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()
        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile_valueerror(self):
        print("Run: %s.test_openFile() " % self.__class__.__name__)
        fname = "test.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            tdw.writer = "h5cpp"
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))

            tdw.openFile()
            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)
            try:
                error = False
                tdw.jsonrecord = "}"
            except ValueError:
                error = True
            self.assertEqual(error, True)

            tdw.closeFile()
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))
            self.assertTrue(tdw.getFile() is None)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()

#            print("\nFile attributes:")
            cnt = 0
            for at in f.attributes:
                cnt += 1
#                print(at.name),"=",at[...]
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(5, len(f.attributes))
#            print ""

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile_typeerror(self):
        print("Run: %s.test_openFile() " % self.__class__.__name__)
        fname = "test.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            tdw.writer = "h5cpp"
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))

            tdw.openFile()
            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)
            try:
                error = False
                tdw.jsonrecord = 1223
            except TypeError:
                error = True
            self.assertEqual(error, True)

            tdw.closeFile()
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))
            self.assertTrue(tdw.getFile() is None)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()

#            print("\nFile attributes:")
            cnt = 0
            for at in f.attributes:
                cnt += 1
#                print(at.name),"=",at[...]
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(5, len(f.attributes))
#            print ""

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_writer(self):
        print("Run: %s.test_writer() " % self.__class__.__name__)
        self.assertTrue("h5cpp" in nxswriter.TangoDataWriter.WRITERS.keys())
        self.assertEqual(
            nxswriter.TangoDataWriter.WRITERS["h5cpp"], H5CppWriter)

    # openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFileDir(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        directory = '#nexdatas_test_directoryS#'
        dirCreated = False
        dirExists = False
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                dirCreated = True
                dirExists = True
            except Exception:
                pass
        else:
            dirExists = True

        if dirExists:
            fname = '%s/%s/%s%s.h5' % (
                os.getcwd(), directory, self.__class__.__name__, fun)
        else:
            fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)

        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            tdw.writer = "h5cpp"
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))

            tdw.openFile()
            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)

            tdw.closeFile()
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))
            self.assertTrue(tdw.getFile() is None)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
#            print("\nFile attributes:")
            cnt = 0
            for at in f.attributes:
                cnt += 1
#                print(at.name),"=",at[...]
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(5, len(f.attributes))
#            print ""

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)
            if dirCreated:
                os.removedirs(directory)

    # openEntry test
    # \brief It tests validation of opening and closing entry in H5 files.
    def test_openEntry(self):
        fun = sys._getframe().f_code.co_name
        print("Run: TangoDataWriterTest.test_openEntry() ")
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = '<definition> <group type="NXentry" name="entry"/></definition>'
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname
            tdw.openFile()

            tdw.xmlsettings = xml
            tdw.openEntry()

            tdw.closeEntry()

            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.writer, "h5cpp")
            self.assertNotEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, (int, int)))

            tdw.closeFile()

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 2)

            cnt = 0
            for ch in f:
                self.assertTrue(ch.is_valid)
                cnt += 1
                if ch.name == "entry":
                    self.assertEqual(ch.name, "entry")
                    self.assertEqual(len(ch.attributes), 1)
                    for at in ch.attributes:
                        self.assertTrue(at.is_valid)
                        # self.assertTrue(hasattr(at.shape,"__iter__"))
                        # self.assertEqual(len(at.shape),0)
                        self.assertEqual(len(at.shape), 0)
                        self.assertEqual(at.shape, ())
                        self.assertEqual(at.dtype, "string")
                    #                    self.assertEqual(at.dtype,"string")
                        self.assertEqual(at.name, "NX_class")
                        self.assertEqual(at[...], "NXentry")
                else:
                    self.assertEqual(ch.name, "nexus_logs")
                    ch2 = ch.open("configuration")
                    c = ch2.open("nexus__entry__1_xml")
                    self.assertEqual(
                        c.read(),
                        '<definition> <group type="NXentry" name="entry"/>'
                        '</definition>')
                    print(c.read())
                    c = ch2.open("python_version")
                    self.assertEqual(c.name, "python_version")
                    self.assertEqual(c.read(), sys.version)

                    self.assertEqual(len(ch.attributes), 0)

            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # openEntryWithSAXParseException test
    # \brief It tests validation of opening and closing entry
    #        with SAXParseException
    def test_openEntryWithSAXParseException(self):
        print("Run: TangoDataWriterTest.test_openEntryWithSAXParseException()")
        fname = "test.h5"
        wrongXml = """Ala ma kota."""
        xml = """<definition/>"""
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname

            tdw.openFile()

            try:
                error = None
                tdw.xmlsettings = wrongXml
            except SAXParseException:
                error = True
            except Exception:
                error = False
            self.assertTrue(error is not None)
            self.assertEqual(error, True)

            try:
                tdw.xmlsettings = xml
                error = None
                tdw.openEntry()
            except SAXParseException:
                error = True
            except Exception:
                error = False
            self.assertTrue(error is None)

            tdw.closeEntry()

            tdw.closeFile()

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1

            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_twoentries(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        fmname1 = '%s.entry001.json' % fname
        fmname2 = '%s.entry002.json' % fname
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.metadataOutput = "file"
            tdw.fileName = fname

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.xmlsettings = self._scanXmlb % ("001", fname, "001")
            tdw.openEntry()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.record('{"data": {"exp_c01":' + str(self._counter[0]) +
                       ', "p09/mca/exp.02":' + str(self._mca1) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.closeEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.xmlsettings = self._scanXmlb % ("002", fname, "002")
            tdw.openEntry()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.record('{"data": {"exp_c01":' + str(self._counter[0]) +
                       ', "p09/mca/exp.02":' + str(self._mca1) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.closeEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.closeFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 3)

            ent = ["001", "002"]
            for et in ent:

                en = f.open("entry%s" % et)
                self.assertTrue(en.is_valid)
                self.assertEqual(en.name, "entry%s" % et)
                self.assertEqual(len(en.attributes), 1)
                self.assertEqual(en.size, 2)

                at = en.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXentry")

    # ins = f.open("entry1/instrument:NXinstrument")    #bad exception
    #            ins = f.open("entry1/instrument")
                ins = en.open("instrument")
                self.assertTrue(ins.is_valid)
                self.assertEqual(ins.name, "instrument")
                self.assertEqual(len(ins.attributes), 2)
                self.assertEqual(ins.size, 1)

                at = ins.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXinstrument")

                at = ins.attributes["short_name"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "short_name")
                self.assertEqual(at[...], "scan instrument")

                det = ins.open("detector")
                self.assertTrue(det.is_valid)
                self.assertEqual(det.name, "detector")
                self.assertEqual(len(det.attributes), 1)
                self.assertEqual(det.size, 2)

                at = det.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXdetector")

    # cnt = det.open("counter")              # bad exception
                cnt = det.open("counter1")
                self.assertTrue(cnt.is_valid)
                self.assertEqual(cnt.name, "counter1")
                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(cnt.shape), 1)
                self.assertEqual(cnt.shape, (2,))
                self.assertEqual(cnt.dtype, "float64")
                self.assertEqual(cnt.size, 2)
                value = cnt.read()
    #            value = cnt[:]
                for i in range(len(value)):
                    self.assertEqual(self._counter[i], value[i])

                self.assertEqual(len(cnt.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "STEP")

                at = cnt.attributes["type"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "type")
                self.assertEqual(at[...], "NX_FLOAT")

                at = cnt.attributes["units"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "units")
                self.assertEqual(at[...], "m")

                at = cnt.attributes["nexdatas_source"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")

                mca = det.open("mca")
                self.assertTrue(mca.is_valid)
                self.assertEqual(mca.name, "mca")

                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(mca.shape), 2)
                self.assertEqual(mca.shape, (2, 2048))
                self.assertEqual(mca.dtype, "float64")
                self.assertEqual(mca.size, 4096)
                value = mca.read()
                for i in range(len(value[0])):
                    self.assertEqual(self._mca1[i], value[0][i])
                for i in range(len(value[0])):
                    self.assertEqual(self._mca2[i], value[1][i])

                self.assertEqual(len(mca.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "STEP")

                at = mca.attributes["type"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "type")
                self.assertEqual(at[...], "NX_FLOAT")

                at = mca.attributes["units"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "units")
                self.assertEqual(at[...], "")

                at = mca.attributes["nexdatas_source"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")

                dt = en.open("data")
                self.assertTrue(dt.is_valid)
                self.assertEqual(dt.name, "data")
                self.assertEqual(len(dt.attributes), 1)
                self.assertEqual(dt.size, 2)

                at = dt.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXdata")

                cnt = dt.open("cnt1")
                self.assertTrue(cnt.is_valid)
                #            ???
                # self.assertEqual(cnt.name,"cnt1")
                #            self.assertEqual(cnt.name,"counter1")

                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(cnt.shape), 1)
                self.assertEqual(cnt.shape, (2,))
                self.assertEqual(cnt.dtype, "float64")
                self.assertEqual(cnt.size, 2)
    #             print(cnt.read())
                value = cnt[:]
                for i in range(len(value)):
                    self.assertEqual(self._counter[i], value[i])

                self.assertEqual(len(cnt.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "STEP")

                at = cnt.attributes["type"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "type")
                self.assertEqual(at[...], "NX_FLOAT")

                at = cnt.attributes["units"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "units")
                self.assertEqual(at[...], "m")

                at = cnt.attributes["nexdatas_source"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")

                mca = dt.open("data")
                self.assertTrue(mca.is_valid)
                self.assertEqual(mca.name, "data")

                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(mca.shape), 2)
                self.assertEqual(mca.shape, (2, 2048))
                self.assertEqual(mca.dtype, "float64")
                self.assertEqual(mca.size, 4096)
                value = mca.read()
                for i in range(len(value[0])):
                    self.assertEqual(self._mca1[i], value[0][i])
                for i in range(len(value[0])):
                    self.assertEqual(self._mca2[i], value[1][i])

                self.assertEqual(len(mca.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "STEP")

                at = mca.attributes["type"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "type")
                self.assertEqual(at[...], "NX_FLOAT")

                at = mca.attributes["units"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "units")
                self.assertEqual(at[...], "")

                at = mca.attributes["nexdatas_source"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")

            f.close()
            with open(fmname1, "r") as mf:
                md1 = mf.read()
            with open(fmname2, "r") as mf:
                md2 = mf.read()
            mresult = {
                "techniques": [],
                "creationTime": "",
                "creationLocation": "/DESY/PETRA III",
                "ownerGroup": "ingestor",
                "type": "raw",
                "scientificMetadata": {
                    "data": {
                        "NX_class": "NXdata",
                        "cnt1": {
                            "shape": [
                                2
                            ],
                            "source": "exp_c01",
                            "source_name": "",
                            "source_type": "CLIENT",
                            "strategy": "STEP",
                            "type": "NX_FLOAT",
                            "unit": "m"
                        },
                        "data": {
                            "shape": [
                                2,
                                2048
                            ],
                            "source": "p09/mca/exp.02",
                            "source_name": "",
                            "source_type": "CLIENT",
                            "strategy": "STEP",
                            "type": "NX_FLOAT",
                            "unit": ""
                        }
                    },
                    "instrument": {
                        "NX_class": "NXinstrument",
                        "detector": {
                            "NX_class": "NXdetector",
                            "counter1": {
                                "shape": [
                                    2
                                ],
                                "source": "exp_c01",
                                "source_name": "",
                                "source_type": "CLIENT",
                                "strategy": "STEP",
                                "type": "NX_FLOAT",
                                "unit": "m"
                            },
                            "mca": {
                                "shape": [
                                    2,
                                    2048
                                ],
                                "source": "p09/mca/exp.02",
                                "source_name": "",
                                "source_type": "CLIENT",
                                "strategy": "STEP",
                                "type": "NX_FLOAT",
                                "unit": ""
                            }
                        },
                        "short_name": "scan instrument"
                    },
                    "name": "entry001"
                }
            }
            mresult["scientificMetadata"]["name"] = "entry001"
            self.myAssertDict(mresult, json.loads(md1),
                              skip=["creationTime"])
            mresult["scientificMetadata"]["name"] = "entry002"
            self.myAssertDict(mresult, json.loads(md2),
                              skip=["creationTime"])
        finally:
            if os.path.isfile(fname):
                os.remove(fname)
            if os.path.isfile(fmname2):
                os.remove(fmname2)
            if os.path.isfile(fmname1):
                os.remove(fmname1)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.xmlsettings = self._scanXml % fname
            tdw.openEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.record('{"data": {"exp_c01":' + str(self._counter[0]) +
                       ', "p09/mca/exp.02":' + str(self._mca1) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeEntry()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # PNI self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_nexuspath(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            nxpath = "/entry1:NXentry"
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = "%s:/%s" % (fname, nxpath)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.xmlsettings = self._scanXmlpart
            tdw.openEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.record('{"data": {"exp_c01":' + str(self._counter[0]) +
                       ', "p09/mca/exp.02":' + str(self._mca1) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeEntry()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 1)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], u"\u03bcm")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)
            # pass

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_skipacq(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.skipacquisition, False)
            tdw.openFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.skipacquisition, False)
            tdw.xmlsettings = self._scanXml % fname
            tdw.openEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.record('{"data": {"exp_c01":' + str(self._counter[0]) +
                       ', "p09/mca/exp.02":' + str(self._mca1) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.skipacquisition = True
            tdw.closeEntry()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.skipacquisition, False)
            tdw.openFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.skipacquisition, False)
            tdw.xmlsettings = self._scanXml % fname
            self.myAssertRaise(Exception, tdw.openEntry)
            tdw.skipacquisition = True
            tdw.openEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.skipacquisition = True
            tdw.closeEntry()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.skipacquisition, False)
            tdw.openFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.skipacquisition, False)
            tdw.xmlsettings = self._scanXml % fname
            self.myAssertRaise(Exception, tdw.openEntry)
            tdw.skipacquisition = True
            tdw.openEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.skipacquisition = True
            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeEntry()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.skipacquisition, False)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # PNI self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)
#            pass

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_canfail_setfalse(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname
            tdw.defaultCanFail = False
            self.assertEqual(tdw.defaultCanFail, False)
            tdw.canfail = True

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.defaultCanFail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.xmlsettings = self._scanXml % fname
            tdw.openEntry()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.record()

            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.record()

            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeEntry()
            self.assertEqual(tdw.canfail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()
            self.assertEqual(tdw.canfail, False)
            self.assertEqual(tdw.defaultCanFail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max, value[i])

            self.assertEqual(len(cnt.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = cnt.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[1][i])

            self.assertEqual(len(mca.attributes), 6)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = mca.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # PNI self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(numpy.finfo(getattr(numpy, 'float64')).max,
                                 value[i])

            self.assertEqual(len(cnt.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = cnt.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[1][i])

            self.assertEqual(len(mca.attributes), 6)
            at = mca.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = mca.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')")

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)
#            pass

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_canfail_false(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname
            self.assertEqual(tdw.defaultCanFail, True)
            tdw.canfail = True

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.defaultCanFail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.xmlsettings = self._scanXml % fname
            tdw.openEntry()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.record()

            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.record()

            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeEntry()
            self.assertEqual(tdw.canfail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.defaultCanFail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max, value[i])

            self.assertEqual(len(cnt.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = cnt.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[1][i])

            self.assertEqual(len(mca.attributes), 6)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = mca.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # PNI self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(numpy.finfo(getattr(numpy, 'float64')).max,
                                 value[i])

            self.assertEqual(len(cnt.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = cnt.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[1][i])

            self.assertEqual(len(mca.attributes), 6)
            at = mca.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = mca.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')")

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)
#            pass

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_defaultcanfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname
            self.assertEqual(tdw.defaultCanFail, True)
            tdw.defaultCanFail = True

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.defaultCanFail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.xmlsettings = self._scanXml % fname
            tdw.openEntry()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.record()

            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.record()

            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeEntry()
            self.assertEqual(tdw.canfail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.defaultCanFail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max, value[i])

            self.assertEqual(len(cnt.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = cnt.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[1][i])

            self.assertEqual(len(mca.attributes), 6)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = mca.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # PNI self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(numpy.finfo(getattr(numpy, 'float64')).max,
                                 value[i])

            self.assertEqual(len(cnt.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = cnt.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: "
                "CLIENT record exp_c01', 'Data without value')")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[1][i])

            self.assertEqual(len(mca.attributes), 6)
            at = mca.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = mca.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')\n"
                "('Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')")

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)
#            pass

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_canfail_false_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname
            self.assertEqual(tdw.defaultCanFail, True)
            tdw.canfail = False
            self.assertEqual(tdw.defaultCanFail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()
            self.assertEqual(tdw.canfail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.xmlsettings = self._scanXml % fname
            self.assertEqual(tdw.canfail, False)
            tdw.openEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.canfail, False)

            self.myAssertRaise(Exception, tdw.record)
            self.assertEqual(tdw.canfail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.myAssertRaise(Exception, tdw.record)
            self.assertEqual(tdw.canfail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.canfail, False)
            tdw.closeEntry()
            self.assertEqual(tdw.canfail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()
            self.assertEqual(tdw.canfail, True)
            self.assertEqual(tdw.defaultCanFail, True)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
#            for i in range(len(value)):
#                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
#            self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype, "float64")
#            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # PNI self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
#            for i in range(len(value)):
#                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
#            self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype, "float64")
#            self.assertEqual(mca.size, 4096)
            value = mca.read()
#            for i in range(len(value[0])):
#                self.assertEqual(self._mca1[i], value[0][i])
#            for i in range(len(value[0])):
#                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)
                #            pass

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_defaultcanfail_false(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname
            self.assertEqual(tdw.defaultCanFail, True)
            tdw.defaultCanFail = False
            self.assertEqual(tdw.defaultCanFail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()
            self.assertEqual(tdw.canfail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.xmlsettings = self._scanXml % fname
            self.assertEqual(tdw.canfail, False)
            tdw.openEntry()
            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.canfail, False)

            self.myAssertRaise(Exception, tdw.record)
            self.assertEqual(tdw.canfail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.myAssertRaise(Exception, tdw.record)
            self.assertEqual(tdw.canfail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            self.assertEqual(tdw.canfail, False)
            tdw.closeEntry()
            self.assertEqual(tdw.canfail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.closeFile()
            self.assertEqual(tdw.canfail, False)
            self.assertEqual(tdw.defaultCanFail, False)

            self.assertEqual(tdw.stepsperfile, 0)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
#            for i in range(len(value)):
#                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
#            self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype, "float64")
#            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # PNI self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
#            for i in range(len(value)):
#                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
#            self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype, "float64")
#            self.assertEqual(mca.size, 4096)
            value = mca.read()
#            for i in range(len(value[0])):
#                self.assertEqual(self._mca1[i], value[0][i])
#            for i in range(len(value[0])):
#                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)
#            pass

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_split(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        tfname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        fname = None
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = tfname
            tdw.stepsperfile = 2
            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 0)
            tdw.openFile()
            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 0)

            tdw.xmlsettings = self._scanXml1
            tdw.openEntry()

            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 1)

            tdw.record('{"data": {"exp_c01":' + str(self._counter[0]) +
                       ', "p09/mca/exp.02":' + str(self._mca1) + '  } }')

            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 1)
            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 2)

            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 2)
            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 3)

            tdw.record('{"data": {"exp_c01":' + str(self._counter[1]) +
                       ', "p09/mca/exp.02":' + str(self._mca2) + '  } }')

            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 3)
            tdw.record('{"data": {"exp_c01":' + str(self._counter[0]) +
                       ', "p09/mca/exp.02":' + str(self._mca1) + '  } }')

            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 4)

            tdw.closeEntry()
            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 1)

            tdw.closeFile()

            self.assertEqual(tdw.stepsperfile, 2)
            self.assertEqual(tdw.currentfileid, 0)

            # check the created file

            fname = '%s/%s%s_00001.h5' % (
                os.getcwd(), self.__class__.__name__, fun)
            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            #   self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()
            # check the created file

            fname = '%s/%s%s_00002.h5' % (
                os.getcwd(), self.__class__.__name__, fun)
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[1], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[1], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()
            # check the created file

            fname = '%s/%s%s_00003.h5' % (
                os.getcwd(), self.__class__.__name__, fun)
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[1 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[1 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()
        finally:
            for i in range(1, 4):
                fname = '%s/%s%s_%05d.h5' % (
                    os.getcwd(), self.__class__.__name__, fun, i)
                if os.path.isfile(fname):
                    os.remove(fname)
            if os.path.isfile(tfname):
                os.remove(tfname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecordGrow(self):
        print("Run: TangoDataWriterTest.test_scanRecordGrow() ")
        fname = "scantest.h5"
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname

            tdw.openFile()

            tdw.xmlsettings = self._scanXml % fname
            tdw.openEntry()

            cntg = [self._counter[0], self._counter[1]]
            mcag = [self._mca1, self._mca2]
            rec = {"data": {"exp_c01": cntg, "p09/mca/exp.02": mcag}}
            tdw.record(json.dumps(rec))

            tdw.closeEntry()

            tdw.closeFile()

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # PNI self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            # print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)
#            pass

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecordGrow2(self):
        print("Run: TangoDataWriterTest.test_scanRecordGrow() ")
        fname = "scantestgrow.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            tdw.writer = "h5cpp"

            tdw.openFile()

            tdw.xmlsettings = self._scanXml % fname
            tdw.openEntry()

            cntg = [self._counter[0], self._counter[1]]
            mcag = [self._mca1, self._mca2]
            rec = {"data": {"exp_c01": cntg, "p09/mca/exp.02": mcag}}
            tdw.record(json.dumps(rec))

            cntg = [self._counter[1], self._counter[0]]
            mcag = [self._mca2, self._mca1]
            rec = {"data": {"exp_c01": cntg, "p09/mca/exp.02": mcag}}
            tdw.record(json.dumps(rec))

            tdw.closeEntry()

            tdw.closeFile()
            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (4, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 8192)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[3][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[2][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (4, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 8192)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[3][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[2][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecordGrow3(self):
        print("Run: TangoDataWriterTest.test_scanRecordGrow() ")
        fname = "scantestgrow.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            tdw.writer = "h5cpp"

            tdw.openFile()

            tdw.xmlsettings = self._scanXml3 % fname
            tdw.openEntry()

            cntg = [self._counter[0], self._counter[1]]
            imageg = [self._image1, self._image2]
            rec = {"data": {"exp_c01": cntg, "image": imageg}}
            tdw.record(json.dumps(rec))

            cntg = [self._counter[1], self._counter[0]]
            imageg = [self._image2, self._image1]
            rec = {"data": {"exp_c01": cntg, "image": imageg}}
            tdw.record(json.dumps(rec))

            tdw.closeEntry()

            tdw.closeFile()
            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = det.open("image")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "image")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 3)
            self.assertEqual(mca.shape, (4, 200, 100))
            self.assertEqual(mca.dtype, "int64")
            self.assertEqual(mca.size, 80000)
            value = mca.read()
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1[i][j], value[0][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2[i][j], value[1][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2[i][j], value[2][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1[i][j], value[3][i][j])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_INT64")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 3)
            self.assertEqual(mca.shape, (4, 200, 100))
            self.assertEqual(mca.dtype, "int64")
            self.assertEqual(mca.size, 80000)
            value = mca.read()
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1[i][j], value[0][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2[i][j], value[1][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2[i][j], value[2][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1[i][j], value[3][i][j])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_INT64")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_nxrootlink(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        try:
            tdw = TangoDataWriter()
            tdw.writer = "h5cpp"
            tdw.fileName = fname
            tdw.openFile()
            mfl = tdw.getFile()
            rt = mfl.root()
            print(id(rt))
            tdw.xmlsettings = self._scanXml2
            tdw.openEntry()

            tdw.record()

            tdw.record()

            tdw.closeEntry()

            tdw.closeFile()

            # check the created file

            from nxstools import filewriter as FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(5, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 4)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 0)
            self.assertEqual(at.shape, ())
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

            cnt = en.open("nxrootstr")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "nxrootstr")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 0)
            self.assertEqual(cnt.shape, ())
            self.assertEqual(cnt.dtype, "string")
            self.assertEqual(cnt.size, 1)
            value = cnt[...]
            # self.assertEqual(fname, value)
            self.assertEqual("/", value)

            cnt = en.open("nxrootpath")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "nxrootpath")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 0)
            self.assertEqual(cnt.shape, ())
            self.assertEqual(cnt.dtype, "string")
            self.assertEqual(cnt.size, 1)
            value = cnt[...]
            self.assertEqual('.', value)

            cnt = en.open("nxrootlink")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "nxrootlink")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 0)
            self.assertEqual(cnt.shape, ())
            self.assertEqual(cnt.dtype, "string")
            self.assertEqual(cnt.size, 1)
            value = cnt[...]
            self.assertEqual('True', value)

            cnt = en.open("mylink")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "mylink")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 0)
            self.assertEqual(cnt.shape, ())
            self.assertEqual(cnt.dtype, "string")
            self.assertEqual(cnt.size, 1)
            value = cnt[...]
            self.assertEqual('.', value)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)


if __name__ == '__main__':
    unittest.main()
