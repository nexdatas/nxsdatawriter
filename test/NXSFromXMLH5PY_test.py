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
# \file NXSFromXMLTest.py
# unittests for NXSFromXML
#
import unittest
import os
import sys
import struct

from nxswriter import NXSFromXML
from nxstools import h5pywriter as H5PYWriter

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture

#: (:obj:`bool`) tango bug #213 flag related to EncodedAttributes in python3
PYTG_BUG_213 = False
try:
    try:
        import tango
    except Exception:
        import PyTango as tango
    PYTGMAJOR, PYTGMINOR, PYTGPATCH = list(
        map(int, tango.__version__.split(".")[:3]))
    if PYTGMAJOR <= 9:
        if PYTGMAJOR == 9:
            if PYTGMINOR < 2:
                PYTG_BUG_213 = True
            elif PYTGMINOR == 2 and PYTGPATCH <= 4:
                PYTG_BUG_213 = True
        else:
            PYTG_BUG_213 = True
except Exception:
    pass


class NXSFromXMLH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._scanXmlpart = """
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
"""

        self._scanXml = """
<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="INIT"/>
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
        self._counter = [0.1, 0.2]
        self._mca1 = [e * 0.1 for e in range(2048)]

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

    def runtest(self, argv):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = mystdout = StringIO()
        sys.stderr = mystderr = StringIO()
        old_argv = sys.argv
        sys.argv = argv

        old_stdin = sys.stdin
        sys.stdin = StringIO()

        etxt = None
        try:
            NXSFromXML.main()
        except Exception as e:
            etxt = str(e)
        except SystemExit as e:
            etxt = str(e)
        sys.argv = old_argv

        sys.stdout = old_stdout
        sys.stderr = old_stderr
        sys.stdin = old_stdin
        sys.argv = old_argv
        vl = mystdout.getvalue()
        er = mystderr.getvalue()
        # print(vl)
        # print(er)
        if etxt:
            print(etxt)
        self.assertTrue(etxt is None)
        return vl, er

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        data = '{"exp_c01":' + str(self._counter[0]) + \
            ', "p09/mca/exp.02":' + str(self._mca1) + '  }'
        jdata = '{"data": {"exp_c01":' + str(self._counter[0]) + \
            ', "p09/mca/exp.02":' + str(self._mca1) + '  } }'
        xmlfile = '%s/%s%s.xml' % (
            os.getcwd(), self.__class__.__name__, fun)
        jsonfile = '%s/%s%s.json' % (
            os.getcwd(), self.__class__.__name__, fun)

        commands = [
            ['nxsfromxml', '--h5py',
             '-p', fname, '--nrecords', '2',
             '-j', jsonfile,
             '--time', '0.5',
             '-v',
             self._scanXml % fname],
            ['nxsfromxml', '--h5py',
             '--parent', fname, '--nrecords', '2',
             '--json-file', jsonfile,
             '-x', xmlfile],
            ['nxsfromxml', '--h5py',
             '-p', fname, '-n', '2',
             '-d', data,
             '--verbose',
             '--xml-file', xmlfile],
            ['nxsfromxml', '--h5py',
             '--parent', fname, '-n', '2',
             '--data', data,
             '-t', '0',
             self._scanXml % fname],
        ]
        for ci, cmd in enumerate(commands):
            try:

                with open(xmlfile, "w") as text_file:
                    text_file.write(self._scanXml % fname)
                with open(jsonfile, "w") as text_file:
                    text_file.write(jdata)
                vl, er = self.runtest(cmd)
                if PYTG_BUG_213:
                    self.assertTrue(er)
                else:
                    self.assertEqual('', er)
                if ci % 2:
                    self.assertEqual('', vl)
                else:
                    self.assertTrue(vl)

                # check the created file

                from nxstools import filewriter as FileWriter
                FileWriter.writer = H5PYWriter
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
                self.assertEqual(cnt.shape, (1,))
                self.assertEqual(cnt.dtype, "float64")
                self.assertEqual(cnt.size, 1)
                value = cnt.read()
    #            value = cnt[:]
                for i in range(len(value)):
                    self.assertEqual(self._counter[0], value[i])

                self.assertEqual(len(cnt.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "INIT")

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
                    self.assertEqual(self._mca1[i], value[1][i])

                self.assertEqual(len(mca.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "INIT")

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

                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(cnt.shape), 1)
                self.assertEqual(cnt.shape, (1,))
                self.assertEqual(cnt.dtype, "float64")
                self.assertEqual(cnt.size, 1)
    #             print(cnt.read())
                value = cnt[:]
                self.assertEqual(self._counter[0], value)

                self.assertEqual(len(cnt.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "INIT")

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
                    self.assertEqual(self._mca1[i], value[1][i])

                self.assertEqual(len(mca.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "INIT")

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
                if os.path.isfile(xmlfile):
                    os.remove(xmlfile)
                if os.path.isfile(jsonfile):
                    os.remove(jsonfile)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_append(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        data = '{"exp_c01":' + str(self._counter[0]) + \
            ', "p09/mca/exp.02":' + str(self._mca1) + '  }'
        jdata = '{"data": {"exp_c01":' + str(self._counter[0]) + \
            ', "p09/mca/exp.02":' + str(self._mca1) + '  } }'
        xmlfile = '%s/%s%s.xml' % (
            os.getcwd(), self.__class__.__name__, fun)
        jsonfile = '%s/%s%s.json' % (
            os.getcwd(), self.__class__.__name__, fun)

        commands = [
            ['nxsfromxml', '--h5py',
             '-p', fname, '--nrecords', '1',
             '-j', jsonfile,
             '--time', '0.5',
             '-v',
             '-a',
             self._scanXml % fname],
            ['nxsfromxml', '--h5py',
             '--parent', fname, '--nrecords', '1',
             '--json-file', jsonfile,
             '--append',
             '-x', xmlfile],
            ['nxsfromxml', '--h5py',
             '-p', fname, '-n', '1',
             '-d', data,
             '-a',
             '--verbose',
             '--xml-file', xmlfile],
            ['nxsfromxml', '--h5py',
             '--parent', fname, '-n', '1',
             '--data', data,
             '--append',
             '-t', '0',
             self._scanXml % fname],
        ]
        for ci, cmd in enumerate(commands):
            try:

                with open(xmlfile, "w") as text_file:
                    text_file.write(self._scanXml % fname)
                with open(jsonfile, "w") as text_file:
                    text_file.write(jdata)
                vl, er = self.runtest(cmd)
                if PYTG_BUG_213:
                    self.assertTrue(er)
                else:
                    self.assertEqual('', er)
                if ci % 2:
                    self.assertEqual('', vl)
                else:
                    self.assertTrue(vl)

                vl, er = self.runtest(cmd)
                if PYTG_BUG_213:
                    self.assertTrue(er)
                else:
                    self.assertEqual('', er)
                if ci % 2:
                    self.assertEqual('', vl)
                else:
                    self.assertTrue(vl)

                # check the created file

                from nxstools import filewriter as FileWriter
                FileWriter.writer = H5PYWriter
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

                cnt = det.open("counter1")
                self.assertTrue(cnt.is_valid)
                self.assertEqual(cnt.name, "counter1")
                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(cnt.shape), 1)
                self.assertEqual(cnt.shape, (1,))
                self.assertEqual(cnt.dtype, "float64")
                self.assertEqual(cnt.size, 1)
                value = cnt.read()
                for i in range(len(value)):
                    self.assertEqual(0, value[0])

                self.assertEqual(len(cnt.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "INIT")

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
                    self.assertEqual(self._mca1[i], value[1][i])

                self.assertEqual(len(mca.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "INIT")

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
                self.assertEqual(dt.size, 0)

                at = dt.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 0)
                self.assertEqual(at.shape, ())
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXdata")

                f.close()

            finally:

                if os.path.isfile(fname):
                    os.remove(fname)
                if os.path.isfile(xmlfile):
                    os.remove(xmlfile)
                if os.path.isfile(jsonfile):
                    os.remove(jsonfile)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_nexuspath(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        data = '{"exp_c01":' + str(self._counter[0]) + \
            ', "p09/mca/exp.02":' + str(self._mca1) + '  }'
        jdata = '{"data": {"exp_c01":' + str(self._counter[0]) + \
            ', "p09/mca/exp.02":' + str(self._mca1) + '  } }'
        xmlfile = '%s/%s%s.xml' % (
            os.getcwd(), self.__class__.__name__, fun)
        jsonfile = '%s/%s%s.json' % (
            os.getcwd(), self.__class__.__name__, fun)
        nxpath = "/entry1:NXentry"

        commands = [
            ['nxsfromxml', '--h5py',
             '-p', "%s:/%s" % (fname, nxpath),
             '--nrecords', '2',
             '-j', jsonfile,
             '--time', '0.5',
             '-r',
             '-v',
             self._scanXmlpart],
            ['nxsfromxml', '--h5py',
             '--parent', "%s:/%s" % (fname, nxpath), '--nrecords', '2',
             '--json-file', jsonfile,
             '-r',
             '-x', xmlfile],
            ['nxsfromxml', '--h5py',
             '-p', "%s:/%s" % (fname, nxpath), '-n', '2',
             '-d', data,
             '--no-nexus-logs',
             '--verbose',
             '--xml-file', xmlfile],
            ['nxsfromxml', '--h5py',
             '--parent', "%s:/%s" % (fname, nxpath), '-n', '2',
             '--data', data,
             '--no-nexus-logs',
             '-t', '0',
             self._scanXmlpart],
        ]
        for ci, cmd in enumerate(commands):
            try:

                with open(xmlfile, "w") as text_file:
                    text_file.write(self._scanXmlpart)
                with open(jsonfile, "w") as text_file:
                    text_file.write(jdata)
                vl, er = self.runtest(cmd)
                if PYTG_BUG_213:
                    self.assertTrue(er)
                else:
                    print(er)
                    self.assertEqual('', er)
                if ci % 2:
                    self.assertEqual('', vl)
                else:
                    self.assertTrue(vl)

                # check the created file

                from nxstools import filewriter as FileWriter
                FileWriter.writer = H5PYWriter
                f = FileWriter.open_file(fname, readonly=True)
                f = f.root()
                self.assertEqual(5, len(f.attributes))
                self.assertEqual(f.attributes["file_name"][...], fname)
                self.assertTrue(f.attributes["NX_class"][...], "NXroot")
                self.assertEqual(f.size, 1)

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
                    self.assertEqual(self._counter[0], value[i])

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

                if os.path.isfile(fname):
                    os.remove(fname)
                if os.path.isfile(xmlfile):
                    os.remove(xmlfile)
                if os.path.isfile(jsonfile):
                    os.remove(jsonfile)


if __name__ == '__main__':
    unittest.main()
