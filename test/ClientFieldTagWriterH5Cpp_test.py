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
# \file ClientFieldTagWriterTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time
import numpy

try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker


from nxswriter.TangoDataWriter import TangoDataWriter
from nxstools import filewriter as FileWriter
from nxstools import h5cppwriter as H5CppWriter


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture

if sys.version_info > (3,):
    long = int


class ClientFieldTagWriterH5CppTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        try:
            # random seed
            self.seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            # random seed
            self.seed = long(time.time() * 256)  # use fractional seconds
#        self.seed = 53867028435352363366241944565880343254
        self.__rnd = random.Random(self.seed)

        self._counter = [1, -2, 6, -8, 9, -11]
        self._fcounter = [1.1, -2.4, 6.54, -8.456, 9.456, -0.46545]
        self._sc = Checker(self)
        self._mca1 = [[self.__rnd.randint(-100, 100)
                       for e in range(256)] for i in range(3)]
        self._mca2 = [[self.__rnd.randint(0, 100)
                       for e in range(256)] for i in range(3)]
        self._fmca1 = [self._sc.nicePlot(1024, 10) for i in range(4)]
#        self._fmca2 = [(float(e)/(100.+e)) for e in range(2048)]
        self._pco1 = [[[self.__rnd.randint(0, 100) for e1 in range(8)]
                       for e2 in range(10)] for i in range(3)]
        self._fpco1 = [self._sc.nicePlot2D(20, 30, 5) for i in range(4)]

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        print("SEED = %s" % self.seed)
        print("CHECKER SEED = %s" % self._sc.seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    def setProp(self, rc, name, value):
        setattr(rc, name, value)

    # opens writer
    # \param fname file name
    # \param xml XML settings
    # \param json JSON Record with client settings
    # \returns Tango Data Writer instance
    def openWriter(self, fname, xml, json=None):
        tdw = TangoDataWriter()
        self.setProp(tdw, "writer", "h5cpp")
        tdw.fileName = fname
        tdw.openFile()
        tdw.xmlsettings = xml
#        tdw.numberOfThreads = 1
        if json:
            tdw.jsonrecord = json
        tdw.openEntry()
        return tdw

    # closes writer
    # \param tdw Tango Data Writer instance
    # \param json JSON Record with client settings
    def closeWriter(self, tdw, json=None):
        if json:
            tdw.jsonrecord = json
        tdw.closeEntry()
        tdw.closeFile()

    # performs one record step
    def record(self, tdw, string):
        tdw.record(string)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientIntScalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_INT" name="counter">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt"/>
          </datasource>
        </field>
        <field units="m" type="NX_INT8" name="counter8">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_8"/>
          </datasource>
        </field>
        <field units="m" type="NX_INT16" name="triggered_counter16">
          <strategy mode="STEP" trigger="trigger1"/>
          <datasource type="CLIENT">
            <record name="cnt_16"/>
          </datasource>
        </field>
        <field units="m" type="NX_INT32" name="counter32">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_32"/>
          </datasource>
        </field>
        <field units="m" type="NX_INT64" name="counter64">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_64"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT" name="ucounter">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u"/>
          </datasource>
        </field>
        <field units="m" type="NX_POSINT" name="pcounter">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_p"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT8" name="ucounter8">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u8"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT16" name="ucounter16">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u16"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT32" name="mclient_ucounter32">
          <strategy mode="STEP"/>
          <datasource type="MCLIENT" name="external datasource">
            <record name="cnt_u32"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT64" name="ucounter64">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u64"/>
          </datasource>
        </field>


        <field units="m" type="NX_UINT64" name="ucounter64_canfail">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="CLIENT">
            <record name="cnt_u64_canfail"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT64" name="init64">
          <strategy mode="INIT"/>
          <datasource type="CLIENT">
            <record name="cnt_64"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT32" name="final32">
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="cnt_u32"/>
          </datasource>
        </field>


        <field units="m" type="NX_INT32" name="final32_canfail">
          <strategy mode="FINAL"  canfail="true"/>
          <datasource type="CLIENT">
            <record name="cnt_32_canfail"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT64" name="init64_canfail">
          <strategy mode="INIT" canfail="true"/>
          <datasource type="CLIENT">
            <record name="cnt_64_canfail"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT32" name="postrun_counter32">
          <strategy mode="POSTRUN">
              https://haso.desy.de/counters/counter32.dat
          </strategy>
        </field>

      </group>
    </group>
  </group>
</definition>
"""

        uc = self._counter[0]
        datasources = ', "datasources":{"MCLIENT":' + \
                      '"nxswriter.ClientSource.ClientSource"}'
        tdw = self.openWriter(
            fname, xml,
            json='{"data": { "cnt_64":' + str(uc) + ' }' +
            str(datasources) + ' }')

        flip = True
        trigstr = ', "triggers":["trigger1"]'
        for c in self._counter:
            uc = abs(c)
            self.record(tdw, '{"data": {"cnt":' + str(c) +
                        ', "cnt_8":' + str(c) +
                        ', "cnt_16":' + str(c) +
                        ', "cnt_32":' + str(c) +
                        ', "cnt_64":' + str(c) +
                        ', "cnt_u":' + str(uc) +
                        ', "cnt_p":' + str(uc) +
                        ', "cnt_u8":' + str(uc) +
                        ', "cnt_u16":' + str(uc) +
                        ', "cnt_u32":' + str(uc) +
                        ((', "cnt_u64_canfail":' + str(uc)) if flip else ' ') +
                        ', "cnt_u64":' + str(uc) +
                        ' } ' +
                        str(trigstr if flip else ' ') +
                        '  }')
            flip = not flip

        uc = abs(self._counter[0])
        self.closeWriter(
            tdw, json='{"data": { "cnt_u32":' + str(uc) + ' } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 17)
        self._sc.checkScalarField(
            det, "counter", "int64", "NX_INT", self._counter)
        self._sc.checkScalarField(
            det, "counter8", "int8", "NX_INT8", self._counter)
        self._sc.checkScalarField(
            det, "triggered_counter16", "int16", "NX_INT16",
            self._counter[0::2])
        self._sc.checkScalarField(
            det, "counter32", "int32", "NX_INT32", self._counter)
        self._sc.checkScalarField(
            det, "counter64", "int64", "NX_INT64", self._counter)
        self._sc.checkScalarField(
            det, "ucounter", "uint64", "NX_UINT",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ucounter8", "uint8", "NX_UINT8",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(det, "ucounter16", "uint16", "NX_UINT16",
                                  [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "mclient_ucounter32", "uint32", "NX_UINT32",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(det, "ucounter64", "uint64", "NX_UINT64",
                                  [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ucounter64_canfail", "uint64", "NX_UINT64",
            [self._counter[i] if not i % 2 else
             numpy.iinfo(getattr(numpy, 'uint64')).max
             for i in range(len(self._counter))],
            attrs={
                "type": "NX_UINT64", "units": "m", "nexdatas_source": None,
                "nexdatas_dsname": None,
                "nexdatas_strategy": "STEP",
                "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleScalarField(
            det, "init64", "int64", "NX_INT64", self._counter[0])
        self._sc.checkSingleScalarField(
            det, "final32", "uint32", "NX_UINT32", abs(self._counter[0]))
        self._sc.checkSingleScalarField(
            det, "final32_canfail", "int32", "NX_INT32", numpy.iinfo(
                getattr(numpy, 'int32')).max,
            attrs={"type": "NX_INT32", "units": "m", "nexdatas_source": None,
                   "nexdatas_dsname": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleScalarField(
            det, "init64_canfail", "int64", "NX_INT64",
            numpy.iinfo(getattr(numpy, 'int64')).max,
            attrs={"type": "NX_INT64", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_dsname": None,
                   "nexdatas_canfail_error": None})
        self._sc.checkPostScalarField(
            det, "postrun_counter32", "int32", "NX_INT32",
            "https://haso.desy.de/counters/counter32.dat")

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientAttrScalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <attribute type="NX_FLOAT" name="scalar_float">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="fcnt"/>
          </datasource>
        </attribute>
        <attribute type="NX_FLOAT32" name="scalar_float32_canfail">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="CLIENT">
            <record name="fcnt_canfail"/>
          </datasource>
        </attribute>
        <attribute type="NX_CHAR" name="scalar_string">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="fcnt"/>
          </datasource>
        </attribute>
        <attribute type="NX_INT" name="init_scalar_int">
          <strategy mode="INIT"/>
          <datasource type="CLIENT">
            <record name="cnt"/>
          </datasource>
        </attribute>
        <attribute type="NX_INT64" name="final_scalar_int64_canfail">
          <strategy mode="FINAL" canfail="true"/>
          <datasource type="CLIENT">
            <record name="cnt_canfail"/>
          </datasource>
        </attribute>
        <attribute type="NX_BOOLEAN" name="flag">
          <strategy mode="INIT"/>
          <datasource type="CLIENT">
            <record name="logical"/>
          </datasource>
        </attribute>
      </group>
      <field type="NX_FLOAT" name="counter">
        <attribute type="NX_FLOAT32" name="scalar_float32">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="fcnt"/>
          </datasource>
        </attribute>
        <attribute type="NX_FLOAT64" name="init_scalar_float64_canfail">
          <strategy mode="INIT" canfail="true"/>
          <datasource type="CLIENT">
            <record name="fcnt_canfail"/>
          </datasource>
        </attribute>
        <attribute type="NX_UINT32" name="scalar_uint32_canfail">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="CLIENT">
            <record name="fcnt_canfail"/>
          </datasource>
        </attribute>
        <attribute type="NX_CHAR" name="scalar_string">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="fcnt"/>
          </datasource>
        </attribute>
        <attribute type="NX_INT8" name="final_scalar_int8">
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="cnt"/>
          </datasource>
        </attribute>
        1.2
      </field>
    </group>
  </group>
</definition>
"""

        logical = ["1", "0", "true", "false", "True", "False", "TrUe", "FaLsE"]

        tdw = self.openWriter(fname, xml, json='{"data": {' +
                              ' "cnt":' + str(self._counter[0]) +
                              ', "logical":' + str(logical[0]) +
                              ' } }')
        steps = min(len(self._fcounter), len(self._counter))
        for i in range(steps):
            self.record(tdw, '{"data": {' +
                        ' "cnt":' + str(self._counter[i]) +
                        ', "fcnt":' + str(self._fcounter[i]) +
                        ', "cnt_32":' + str(self._fcounter[i]) +
                        ', "cnt_64":' + str(self._fcounter[i]) +
                        ' } }')

        self.closeWriter(
            tdw, json='{"data": { "cnt":' + str(self._counter[0]) + ' } }')

        # check the created file
        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det, field = self._sc.checkAttributeTree(f, fname, 8, 7)
        self._sc.checkScalarAttribute(
            det, "scalar_float", "float64", self._fcounter[steps - 1],
            error=1.e-14)
        self._sc.checkScalarAttribute(
            det, "scalar_string", "string",
            str(self._fcounter[steps - 1]))
        self._sc.checkScalarAttribute(
            det, "init_scalar_int", "int64", self._counter[0])
        self._sc.checkScalarAttribute(det, "flag", "bool", logical[0])
        self._sc.checkScalarAttribute(
            field, "scalar_float32", "float32", self._fcounter[steps - 1],
            error=1.e-6)
        self._sc.checkScalarAttribute(
            field, "init_scalar_float64_canfail", "float64",
            numpy.finfo(getattr(numpy, 'float64')).max)
        self._sc.checkScalarAttribute(field, "scalar_string", "string",
                                      str(self._fcounter[steps - 1]))
        self._sc.checkScalarAttribute(
            field, "final_scalar_int8", "int8", self._counter[0])
        self._sc.checkScalarAttribute(
            det, "final_scalar_int64_canfail", "int64",
            numpy.iinfo(getattr(numpy, 'int64')).max)
        self._sc.checkScalarAttribute(
            field, "scalar_uint32_canfail", "uint32",
            numpy.iinfo(getattr(numpy, 'uint32')).max)
        self._sc.checkScalarAttribute(
            det, "scalar_float32_canfail", "float32",
            numpy.finfo(getattr(numpy, 'float32')).max)
        self._sc.checkScalarAttribute(
            det, "nexdatas_canfail", "string", "FAILED")
        self._sc.checkScalarAttribute(
            field, "nexdatas_canfail", "string", "FAILED")

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientFloatScalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt"/>
          </datasource>
        </field>
        <field units="m" type="NX_FLOAT32" name="counter_32">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_32"/>
          </datasource>
        </field>
        <field units="m" type="NX_FLOAT64" name="counter_64">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_64"/>
          </datasource>
        </field>
        <field units="m" type="NX_NUMBER" name="counter_nb">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_64"/>
          </datasource>
        </field>
        <field units="m" type="NX_NUMBER" name="counter_nb_canfail">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="CLIENT">
            <record name="cnt_64_canfail"/>
          </datasource>
        </field>
        <field units="m" type="NX_FLOAT32" name="init_32">
          <strategy mode="INIT"/>
          <datasource type="CLIENT">
            <record name="cnt_32"/>
          </datasource>
        </field>
        <field units="m" type="NX_FLOAT64" name="final_64">
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="cnt_64"/>
          </datasource>
        </field>
        <field units="m" type="NX_FLOAT32" name="final_32_canfail">
          <strategy mode="FINAL"  canfail="true" />
          <datasource type="CLIENT">
            <record name="cnt_32_canfail"/>
          </datasource>
        </field>
        <field units="m" type="NX_FLOAT64" name="init_64_canfail">
          <strategy mode="INIT" canfail="true" />
          <datasource type="CLIENT">
            <record name="cnt_64_canfail"/>
          </datasource>
        </field>
      </group>
    </group>
  </group>
</definition>
"""

        tdw = self.openWriter(
            fname, xml,
            json='{"data": { "cnt_32":' + str(self._fcounter[0]) + ' } }')
        flip = True
        for c in self._fcounter:
            self.record(
                tdw, '{"data": {"cnt":' + str(c) +
                ', "cnt_32":' + str(c) +
                ', "cnt_64":' + str(c) +
                ((', "cnt_64_canfail":' + str(c)) if flip else ' ') +
                ' } }')
            flip = not flip

        self.closeWriter(
            tdw, json='{"data": { "cnt_64":' + str(self._fcounter[0]) + ' } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 9)
        self._sc.checkScalarField(
            det, "counter", "float64", "NX_FLOAT", self._fcounter, 1.0e-14)
        self._sc.checkScalarField(
            det, "counter_64", "float64", "NX_FLOAT64",
            self._fcounter, 1.0e-14)
        self._sc.checkScalarField(
            det, "counter_32", "float32", "NX_FLOAT32",
            self._fcounter, 1.0e-06)
        self._sc.checkScalarField(
            det, "counter_nb", "float64", "NX_NUMBER",
            self._fcounter, 1.0e-14)

        self._sc.checkSingleScalarField(
            det, "init_32", "float32", "NX_FLOAT32",
            self._fcounter[0], 1.0e-06)
        self._sc.checkSingleScalarField(
            det, "final_64", "float64", "NX_FLOAT64",
            self._fcounter[0], 1.0e-14)

        self._sc.checkScalarField(
            det, "counter_nb_canfail", "float64", "NX_NUMBER",
            [self._fcounter[i] if not i % 2 else
             numpy.finfo(getattr(numpy, 'float64')).max
             for i in range(len(self._fcounter))],
            attrs={
                "type": "NX_NUMBER", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleScalarField(
            det, "init_64_canfail", "float64", "NX_FLOAT64",
            numpy.finfo(getattr(numpy, 'float64')).max,
            attrs={
                "type": "NX_FLOAT64", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleScalarField(
            det, "final_32_canfail", "float32", "NX_FLOAT32",
            numpy.finfo(getattr(numpy, 'float32')).max,
            attrs={
                "type": "NX_FLOAT32", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientScalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_DATE_TIME" name="time">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="timestamp"/>
          </datasource>
        </field>
        <field units="m" type="ISO8601" name="isotime">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="timestamp"/>
          </datasource>
        </field>
        <field units="m" type="NX_CHAR" name="string_time">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="timestamp"/>
          </datasource>
        </field>
        <field units="m" type="NX_CHAR" name="string_time_canfail">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="CLIENT">
            <record name="timestamp_canfail"/>
          </datasource>
        </field>
        <field units="m" type="NX_BOOLEAN" name="flags">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="logical"/>
          </datasource>
        </field>
        <field units="m" type="NX_BOOLEAN" name="bool_flags">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="bool"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="init_string">
          <strategy mode="INIT"/>
          <datasource type="CLIENT">
            <record name="timestamp"/>
          </datasource>
        </field>
        <field units="m" type="NX_BOOLEAN" name="final_flag">
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="logical"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="final_string_canfail">
          <strategy mode="FINAL" canfail ="true"  />
          <datasource type="CLIENT">
            <record name="timestamp_canfail"/>
          </datasource>
        </field>
        <field units="m" type="NX_BOOLEAN" name="init_flag_canfail">
          <strategy mode="INIT"  canfail ="true" />
          <datasource type="CLIENT">
            <record name="logical_canfail"/>
          </datasource>
        </field>



      </group>
    </group>
  </group>
</definition>
"""
        dates = [
            "1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
            "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200",
            "1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
            "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200",
        ]
        logical = ["1", "0", "true", "false", "True", "False", "TrUe", "FaLsE"]

        tdw = self.openWriter(
            fname, xml,
            json='{"data": { "timestamp":"' + str(dates[0]) + '" } }')

        flip = True
        for i in range(min(len(dates), len(logical))):
            self.record(tdw, '{"data": {"timestamp":"' + str(dates[i]) +
                        '", "logical":"' + str(logical[i]) +
                        '", "bool":true' +
                        ((', "timestamp_canfail":"' + str(
                            dates[i]) + '"') if flip else ' ') +
                        ' } }')
            flip = not flip
        self.closeWriter(
            tdw, json='{"data": { "logical":"' + str(logical[0]) + '" } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 10)
        self._sc.checkScalarField(det, "time", "string", "NX_DATE_TIME", dates)
        self._sc.checkScalarField(det, "isotime", "string", "ISO8601", dates)
        self._sc.checkScalarField(
            det, "string_time", "string", "NX_CHAR", dates)
        self._sc.checkScalarField(det, "flags", "bool", "NX_BOOLEAN", logical)
        self._sc.checkScalarField(
            det, "bool_flags", "bool", "NX_BOOLEAN", [True for c in range(8)])

        self._sc.checkScalarField(
            det, "string_time_canfail", "string", "NX_CHAR",
            [dates[i] if not i % 2 else ''for i in range(len(dates))],
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkSingleStringScalarField(
            det, "final_string_canfail", "string", "NX_CHAR", '',
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleScalarField(
            det, "init_flag_canfail", "bool", "NX_BOOLEAN", False,
            attrs={
                "type": "NX_BOOLEAN", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkSingleStringScalarField(
            det, "init_string", "string", "NX_CHAR", dates[0])
        self._sc.checkSingleScalarField(
            det, "final_flag", "bool", "NX_BOOLEAN", logical[0])

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientIntSpectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="" type="NX_INT" name="mca_int">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="mca_int"/>
          </datasource>
        </field>
        <field units="" type="NX_INT8" name="mca_int8">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" grows="2"/>
          <datasource type="CLIENT">
            <record name="mca_int"/>
          </datasource>
        </field>
        <field units="" type="NX_INT16" name="mca_int16">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true"/>
          <datasource type="CLIENT">
            <record name="mca_int"/>
          </datasource>
        </field>


        <field units="" type="NX_INT16" name="mca_int16_canfail">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true" canfail="true"/>
          <datasource type="CLIENT">
            <record name="mca_int_canfail"/>
          </datasource>
        </field>

        <field units="" type="NX_INT32" name="mca_int32">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true"  grows="2"
 shuffle="false" />
          <datasource type="CLIENT">
            <record name="mca_int"/>
          </datasource>
        </field>
        <field units="" type="NX_INT64" name="mca_int64">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="mca_int"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT" name="mca_uint">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="mca_uint"/>
          </datasource>
        </field>
        <field units="" type="NX_UINT8" name="mca_uint8">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" grows="2"/>
          <datasource type="CLIENT">
            <record name="mca_uint"/>
          </datasource>
        </field>
        <field units="" type="NX_UINT16" name="mca_uint16">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true"/>
          <datasource type="CLIENT">
            <record name="mca_uint"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT32" name="mca_uint32">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true"  grows="2"
 shuffle="false" />
          <datasource type="CLIENT">
            <record name="mca_uint"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT32" name="mca_uint32_canfail" >
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true"  grows="2"
 shuffle="false" canfail="true"/>
          <datasource type="CLIENT">
            <record name="mca_uint_canfail"/>
          </datasource>
        </field>


        <field units="" type="NX_UINT64" name="mca_uint64">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="mca_uint"/>
          </datasource>
        </field>


        <field units="" type="NX_INT64" name="mca_int64_dim">
          <dimensions rank="1"/>
          <strategy mode="STEP" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="mca_int"/>
          </datasource>
        </field>

        <field units="" type="NX_INT64" name="init_mca_int64">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="INIT" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="mca_int"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT32" name="final_mca_uint32">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="mca_uint"/>
          </datasource>
        </field>



        <field units="" type="NX_INT64" name="init_mca_int64_canfail">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="INIT" compression="true" rate="3" canfail="true" />
          <datasource type="CLIENT">
            <record name="mca_int_canfail"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT32" name="final_mca_uint32_canfail">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource type="CLIENT">
            <record name="mca_uint_canfail"/>
          </datasource>
        </field>


        <field units="" type="NX_INT32" name="init_mca_int32">
          <dimensions rank="1"/>
          <strategy mode="INIT" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="mca_iint"/>
          </datasource>
        </field>

      </group>
    </group>
  </group>
</definition>
"""

        tdw = self.openWriter(
            fname, xml,
            json='{"data": { "mca_int":' + str(self._mca1[0]) +
            ', "mca_iint":' + str(self._mca1[0]) + '  } }')

        mca2 = [[(el + 100) // 2 for el in mca] for mca in self._mca1]
        flip = True
        for mca in self._mca1:
            self.record(
                tdw, '{"data": { "mca_int":' + str(mca) +
                ', "mca_uint":' + str([(el + 100) // 2 for el in mca]) +
                (', "mca_int_canfail":' + str(mca) if flip else "") +
                (', "mca_uint_canfail":' + str(
                    [(el + 100) // 2 for el in mca]) if flip else "") +
                '  } }')
            flip = not flip
        self.closeWriter(
            tdw, json='{"data": { "mca_uint":' + str(mca2[0]) + '  } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 18)
        self._sc.checkSpectrumField(
            det, "mca_int", "int64", "NX_INT", self._mca1)
        self._sc.checkSpectrumField(
            det, "mca_int8", "int8", "NX_INT8", self._mca1, grows=2)
        self._sc.checkSpectrumField(
            det, "mca_int16", "int16", "NX_INT16", self._mca1)
        self._sc.checkSpectrumField(
            det, "mca_int32", "int32", "NX_INT32", self._mca1, grows=2)
        self._sc.checkSpectrumField(
            det, "mca_int64", "int64", "NX_INT64", self._mca1)
        self._sc.checkSpectrumField(
            det, "mca_uint", "uint64", "NX_UINT", mca2)
        self._sc.checkSpectrumField(
            det, "mca_uint8", "uint8", "NX_UINT8", mca2, grows=2)
        self._sc.checkSpectrumField(
            det, "mca_uint16", "uint16", "NX_UINT16", mca2)
        self._sc.checkSpectrumField(
            det, "mca_uint32", "uint32", "NX_UINT32", mca2, grows=2)
        self._sc.checkSpectrumField(
            det, "mca_uint64", "uint64", "NX_UINT64", mca2)
        self._sc.checkSpectrumField(
            det, "mca_int64_dim", "int64", "NX_INT64", self._mca1)

        self._sc.checkSingleSpectrumField(
            det, "init_mca_int64", "int64", "NX_INT64", self._mca1[0])
        self._sc.checkSingleSpectrumField(
            det, "init_mca_int32", "int32", "NX_INT32", self._mca1[0])
        self._sc.checkSingleSpectrumField(
            det, "final_mca_uint32", "uint32", "NX_UINT32", mca2[0])

        self._sc.checkSpectrumField(
            det, "mca_int16_canfail", "int16", "NX_INT16",
            [[(self._mca1[j][i] if not j % 2 else
               numpy.iinfo(getattr(numpy, 'int16')).max)
              for i in range(len(self._mca1[j]))]
             for j in range(len(self._mca1))],
            grows=1,
            attrs={
                "type": "NX_INT16", "units": "",
                "nexdatas_strategy": "STEP", "nexdatas_source": None,
                "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkSpectrumField(
            det, "mca_uint32_canfail", "uint32", "NX_UINT32",
            [[((self._mca1[j][i] + 100) // 2 if not j % 2 else
               numpy.iinfo(getattr(numpy, 'uint32')).max)
              for i in range(len(self._mca1[j]))]
             for j in range(len(self._mca1))],
            grows=2, attrs={
                "type": "NX_UINT32", "units": "",
                "nexdatas_strategy": "STEP",
                "nexdatas_source": None,
                "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkSingleSpectrumField(
            det, "final_mca_uint32_canfail", "uint32", "NX_UINT32",
            [numpy.iinfo(getattr(numpy, 'uint32')).max] * 256,
            attrs={"type": "NX_UINT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleSpectrumField(
            det, "init_mca_int64_canfail", "int64", "NX_INT64",
            [numpy.iinfo(getattr(numpy, 'int64')).max] * 256,
            attrs={"type": "NX_INT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientFloatSpectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="" type="NX_FLOAT" name="mca_float">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT32" name="mca_float32">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"/>
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT64" name="mca_float64">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="STEP" grows="2"/>
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </field>


        <field units="" type="NX_FLOAT32" name="mca_float32_canfail">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"
 canfail="true"/>
          <datasource type="CLIENT">
            <record name="mca_float_canfail"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT64" name="mca_float64_canfail">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="STEP" grows="1" canfail="true"/>
          <datasource type="CLIENT">
            <record name="mca_float_canfail"/>
          </datasource>
        </field>


        <field units="" type="NX_NUMBER" name="mca_number">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="STEP" />
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </field>

        <field units="" type="NX_FLOAT" name="mca_float_dim">
          <dimensions rank="1"/>
          <strategy mode="STEP" />
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </field>

        <field units="" type="NX_FLOAT32" name="init_mca_float32">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="INIT" compression="true" shuffle="true"/>
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </field>

        <field units="" type="NX_FLOAT64" name="final_mca_float64">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="FINAL" />
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </field>



        <field units="" type="NX_FLOAT32" name="init_mca_float32_canfail">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="INIT" compression="true" shuffle="true"
 canfail="true"/>
          <datasource type="CLIENT">
            <record name="mca_float_canfail"/>
          </datasource>
        </field>

        <field units="" type="NX_FLOAT64" name="final_mca_float64_canfail">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="FINAL"  canfail="true" />
          <datasource type="CLIENT">
            <record name="mca_float_canfail"/>
          </datasource>
        </field>

        <field units="" type="NX_FLOAT" name="final_mca_float">
          <dimensions rank="1"/>
          <strategy mode="FINAL" />
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </field>


       </group>
    </group>
  </group>
</definition>
"""

        tdw = self.openWriter(
            fname, xml,
            json='{"data": { "mca_float":' + str(self._fmca1[0]) + '  } }')

        flip = True
        for mca in self._fmca1:
            self.record(
                tdw,
                '{"data": { "mca_float":' + str(mca) +
                (', "mca_float_canfail":' + str(mca) if flip else "") +
                '  } }')
            flip = not flip
        self.closeWriter(
            tdw,
            json='{"data": { "mca_float":' + str(self._fmca1[0]) + '  } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 12)
        self._sc.checkSpectrumField(
            det, "mca_float", "float64", "NX_FLOAT", self._fmca1,
            error=1.0e-14)
        self._sc.checkSpectrumField(
            det, "mca_float_dim", "float64", "NX_FLOAT", self._fmca1,
            error=1.0e-14)
        self._sc.checkSpectrumField(
            det, "mca_float32", "float32", "NX_FLOAT32", self._fmca1,
            error=1.0e-6, grows=2)
        self._sc.checkSpectrumField(
            det, "mca_float64", "float64", "NX_FLOAT64", self._fmca1,
            error=1.0e-14, grows=2)
        self._sc.checkSpectrumField(
            det, "mca_number", "float64", "NX_NUMBER", self._fmca1,
            error=1.0e-14)

        self._sc.checkSingleSpectrumField(
            det, "init_mca_float32", "float32", "NX_FLOAT32", self._fmca1[0],
            error=1.0e-6)
        self._sc.checkSingleSpectrumField(
            det, "final_mca_float64", "float64", "NX_FLOAT64", self._fmca1[0],
            error=1.0e-14)
        self._sc.checkSingleSpectrumField(
            det, "final_mca_float", "float64", "NX_FLOAT", self._fmca1[0],
            error=1.0e-14)

        self._sc.checkSingleSpectrumField(
            det, "init_mca_float32_canfail", "float32", "NX_FLOAT32",
            [numpy.finfo(getattr(numpy, 'float32')).max] * len(self._fmca1[0]),
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleSpectrumField(
            det, "final_mca_float64_canfail", "float64", "NX_FLOAT64",
            [numpy.finfo(getattr(numpy, 'float64')).max] * len(self._fmca1[0]),
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkSpectrumField(
            det, "mca_float32_canfail", "float32", "NX_FLOAT32",
            [[(self._fmca1[j][i] if not j % 2 else
               numpy.finfo(getattr(numpy, 'float32')).max)
              for i in range(
                  len(self._fmca1[j]))] for j in range(len(self._fmca1))],
            grows=2,
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1.0e-6)

        self._sc.checkSpectrumField(
            det, "mca_float64_canfail", "float64", "NX_FLOAT64",
            [[(self._fmca1[j][i] if not j % 2 else
               numpy.finfo(getattr(numpy, 'float64')).max)
              for i in range(
                  len(self._fmca1[j]))] for j in range(len(self._fmca1))],
            grows=1,
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1.0e-6)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientSpectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="" type="NX_DATE_TIME" name="time">
          <strategy mode="STEP" compression="true" rate="3"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="timestamps"/>
          </datasource>
        </field>
        <field units="" type="ISO8601" name="isotime">
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="timestamps"/>
          </datasource>
        </field>

        <field units="" type="NX_CHAR" name="string_time">
          <strategy mode="STEP" grows="2"/>
          <datasource type="CLIENT">
           <record name="timestamps"/>
          </datasource>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
        </field>

        <field units="" type="NX_BOOLEAN" name="flags">
          <strategy mode="STEP"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="logicals"/>
          </datasource>
        </field>


        <field units="" type="NX_CHAR" name="string_time_canfail">
          <strategy mode="STEP" grows="2" canfail="true"/>
          <datasource type="CLIENT">
           <record name="timestamps_canfail"/>
          </datasource>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
        </field>
        <field units="" type="NX_BOOLEAN" name="flags_canfail">
          <strategy mode="STEP" canfail="true"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="logicals_canfail"/>
          </datasource>
        </field>



        <field units="" type="NX_BOOLEAN" name="bool_flags">
          <strategy mode="STEP"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="bool"/>
          </datasource>
        </field>

        <field units="" type="NX_BOOLEAN" name="flags_dim">
          <strategy mode="STEP"/>
          <dimensions rank="1" />
          <datasource type="CLIENT">
            <record name="logicals"/>
          </datasource>
        </field>


        <field units="" type="NX_CHAR" name="string_time_dim">
          <strategy mode="STEP" grows="2"/>
          <datasource type="CLIENT">
           <record name="timestamps"/>
          </datasource>
          <dimensions rank="1"/>
        </field>


        <field units="" type="NX_CHAR" name="init_string_time">
          <strategy mode="INIT" compression="true" shuffle="true"/>
          <datasource type="CLIENT">
           <record name="timestamps"/>
          </datasource>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
        </field>
        <field units="" type="NX_BOOLEAN" name="final_flags">
          <strategy mode="FINAL"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="FINAL" />
          <datasource type="CLIENT">
            <record name="logicals"/>
          </datasource>
        </field>





        <field units="" type="NX_CHAR" name="init_string_time_canfail">
          <strategy mode="INIT" compression="true" shuffle="true"
 canfail="true"/>
          <datasource type="CLIENT">
           <record name="timestamps_canfail"/>
          </datasource>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
        </field>
        <field units="" type="NX_BOOLEAN" name="final_flags_canfail">
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="FINAL"  canfail="true" />
          <datasource type="CLIENT">
            <record name="logicals_canfail"/>
          </datasource>
        </field>


        <field units="" type="NX_BOOLEAN" name="init_flags">
          <strategy mode="INIT"/>
          <dimensions rank="1" />
          <strategy mode="FINAL" />
          <datasource type="CLIENT">
            <record name="logicals"/>
          </datasource>
        </field>

        <field units="" type="NX_CHAR" name="final_string_time">
          <strategy mode="FINAL" compression="true" shuffle="true"/>
          <datasource type="CLIENT">
           <record name="timestamps"/>
          </datasource>
          <dimensions rank="1" />
        </field>

      </group>
    </group>
  </group>
</definition>
"""

        dates = [
            ["1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
             "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200"],
            ["1956-05-23T12:12:32.123+0400", "2212-12-12T12:25:43.1267-0700",
             "1914-11-04T04:13:13.44-0000", "2002-04-03T14:15:03.0012-0300"]]
        logical = [["1", "0", "true", "false"],
                   ["True", "False", "TrUe", "FaLsE"]]
# print "CHECK:", '{"data": { "timestamps":' +
# str(dates[0]).replace("'","\"") + '  } }'
        bools = ["[true, false, true, false]", "[true, false, true, false]"]
        tdw = self.openWriter(
            fname, xml, json='{"data": {' +
            ' "timestamps":' +
            str(dates[0]).replace("'", "\"") +
            ', "logicals":' +
            str(logical[0]).replace("'", "\"") +
            '  } }')

        flip = True
        for i in range(min(len(dates), len(logical))):
            self.record(
                tdw, '{"data": {"timestamps":' +
                str(dates[i]).replace("'", "\"") +
                ', "logicals":' + str(logical[i]).replace("'", "\"") +
                (', "logicals_canfail":' + str(logical[i]).replace("'", "\"")
                 if flip else '') +
                (', "timestamps_canfail":' + str(dates[i]).replace("'", "\"")
                 if flip else '') +
                ', "bool":' + bools[i] +
                ' } }')
            flip = not flip

        self.closeWriter(tdw, json='{"data": {' +
                         ' "timestamps":' +
                         str(dates[0]).replace("'", "\"") +
                         ', "logicals":' +
                         str(logical[0]).replace("'", "\"") +
                         '  } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 15)
        self._sc.checkSpectrumField(
            det, "bool_flags", "bool", "NX_BOOLEAN", logical)
        self._sc.checkSpectrumField(
            det, "time", "string", "NX_DATE_TIME", dates)
        self._sc.checkSpectrumField(
            det, "string_time", "string", "NX_CHAR", dates, grows=2)
        self._sc.checkSpectrumField(
            det, "flags", "bool", "NX_BOOLEAN", logical)
        self._sc.checkSpectrumField(
            det, "isotime", "string", "ISO8601", dates, grows=2)
        self._sc.checkSpectrumField(
            det, "string_time_dim", "string", "NX_CHAR", dates, grows=2)

        self._sc.checkSingleSpectrumField(
            det, "init_string_time", "string", "NX_CHAR", dates[0])
        self._sc.checkSingleSpectrumField(
            det, "final_flags", "bool", "NX_BOOLEAN", logical[0])

        self._sc.checkSingleSpectrumField(
            det, "init_string_time_canfail",
            "string", "NX_CHAR", [''] * len(dates[0]),
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleSpectrumField(
            det, "final_flags_canfail", "bool",
            "NX_BOOLEAN", [False] * len(logical[0]),
            attrs={
                "type": "NX_BOOLEAN", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkSingleSpectrumField(
            det, "final_string_time", "string", "NX_CHAR", dates[0])
        self._sc.checkSingleSpectrumField(
            det, "init_flags", "bool", "NX_BOOLEAN", logical[0])

        self._sc.checkSpectrumField(
            det, "flags_canfail", "bool", "NX_BOOLEAN",
            [[(logical[j][i] if not j % 2 else False)
              for i in range(len(logical[j]))] for j in range(len(logical))],
            grows=1,
            attrs={
                "type": "NX_BOOLEAN", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkSpectrumField(
            det, "string_time_canfail", "string", "NX_CHAR",
            [[(dates[j][i] if not j % 2 else '')
              for i in range(len(dates[j]))] for j in range(len(dates))],
            attrs={
                "type": "NX_CHAR", "units": "", "nexdatas_source": None,
                "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None, "nexdatas_strategy": "STEP"},
            grows=2
        )

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientAttrSpectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <attribute type="NX_FLOAT" name="spectrum_float">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </attribute>
        <attribute type="NX_INT32" name="init_spectrum_int32">
          <dimensions rank="1" />
          <strategy mode="INIT"/>
          <datasource type="CLIENT">
            <record name="mca_int"/>
          </datasource>
        </attribute>
        <attribute type="NX_BOOLEAN" name="spectrum_bool">
          <dimensions rank="1">
            <dim value="8" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="flags"/>
          </datasource>
        </attribute>

        <attribute type="NX_UINT64" name="spectrum_uint64_canfail">
          <dimensions rank="1">
            <dim value="1024" index="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource type="CLIENT">
            <record name="mca_uint_canfail"/>
          </datasource>
        </attribute>
        <attribute type="NX_BOOLEAN" name="spectrum_bool_canfail">
          <dimensions rank="1">
            <dim value="8" index="1"/>
          </dimensions>
          <strategy mode="INIT" canfail="true"/>
          <datasource type="CLIENT">
            <record name="flags_canfail"/>
          </datasource>
        </attribute>

      </group>
      <field type="NX_FLOAT" name="counter">
        <attribute type="NX_FLOAT32" name="spectrum_float32">
          <dimensions rank="1" />
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="mca_float"/>
          </datasource>
        </attribute>

        <attribute type="NX_CHAR" name="flag_spectrum_string">
          <dimensions rank="1">
            <dim value="0" index="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="flags"/>
          </datasource>
        </attribute>


        <attribute type="NX_UINT64" name="final_spectrum_uint64">
          <dimensions rank="1">
            <dim  index="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="mca_uint"/>
          </datasource>
        </attribute>
        <attribute type="NX_BOOLEAN" name="init_spectrum_bool">
          <dimensions rank="1">
            <dim value="8" index="1"/>
          </dimensions>
          <strategy mode="INIT"/>
          <datasource type="CLIENT">
            <record name="flags"/>
          </datasource>
        </attribute>

       <attribute type="NX_UINT64" name="final_spectrum_uint64_canfail">
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource type="CLIENT">
            <record name="mca_uint_canfail"/>
          </datasource>
        </attribute>
        <attribute type="NX_BOOLEAN" name="init_spectrum_bool_canfail">
          <dimensions rank="1">
            <dim value="8" index="1"/>
          </dimensions>
          <strategy mode="INIT" canfail="true"/>
          <datasource type="CLIENT">
            <record name="flags_canfail"/>
          </datasource>
        </attribute>

        1.2
      </field>
    </group>
  </group>
</definition>
"""

        logical = ["1", "0", "true", "false", "True", "False", "TrUe", "FaLsE"]
        tdw = self.openWriter(
            fname, xml, json='{"data": {' +
            ' "mca_float":' + str(self._fmca1[0]) +
            ', "flags":' +
            str(logical).replace("'", "\"") +
            ', "mca_int":' + str(self._mca1[0]) +
            '  } }')
        steps = min(len(self._fmca1), len(self._fmca1))
        flip = True
        for i in range(steps):
            self.record(
                tdw, '{"data": {' +
                ' "mca_float":' + str(self._fmca1[i]) +
                ', "flags":' + str(logical).replace("'", "\"") +
                '  } }')
            flip = not flip
        self.closeWriter(
            tdw, json='{"data": {' +
            ' "mca_float":' + str(self._fmca1[0]) +
            ', "mca_int":' + str(self._mca1[0]) +
            ', "flags":' + str(logical).replace("'", "\"") +
            ', "mca_uint":' + str(self._mca2[0]) +
            '  } }')

        # check the created file
        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det, field = self._sc.checkAttributeTree(f, fname, 7, 8)
        self._sc.checkSpectrumAttribute(
            det, "spectrum_float", "float64", self._fmca1[steps - 1],
            error=1.e-14)
        self._sc.checkSpectrumAttribute(
            det, "init_spectrum_int32", "int32", self._mca1[0])
        self._sc.checkSpectrumAttribute(det, "spectrum_bool", "bool", logical)
        self._sc.checkSpectrumAttribute(
            field, "spectrum_float32", "float32", self._fmca1[steps - 1],
            error=1.e-6)
        self._sc.checkSpectrumAttribute(
            field, "final_spectrum_uint64", "uint64", self._mca2[0])
        self._sc.checkSpectrumAttribute(
            field, "init_spectrum_bool", "bool", logical)
        # NOT SUPPORTED BY PNINX
        print(field.read(), logical)
        self._sc.checkSpectrumAttribute(
            field, "flag_spectrum_string", "string",
            logical)

        self._sc.checkSpectrumAttribute(
            det, "spectrum_uint64_canfail", "uint64",
            [numpy.iinfo(getattr(numpy, 'uint64')).max] * 1024)
        self._sc.checkSpectrumAttribute(
            det, "spectrum_bool_canfail", "bool",
            [False] * 8)

        self._sc.checkSpectrumAttribute(
            field, "final_spectrum_uint64_canfail", "uint64",
            [numpy.iinfo(getattr(numpy, 'uint64')).max] * 256)
        self._sc.checkSpectrumAttribute(
            field, "init_spectrum_bool_canfail", "bool",
            [False] * 8)

        self._sc.checkScalarAttribute(
            det, "nexdatas_canfail", "string", "FAILED")
        self._sc.checkScalarAttribute(
            field, "nexdatas_canfail", "string", "FAILED")
        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientIntImage(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="" type="NX_INT" name="pco_int">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </field>
        <field units="" type="NX_INT8" name="pco_int8">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" grows="2"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </field>
        <field units="" type="NX_INT16" name="pco_int16">
          <dimensions rank="2" />
          <strategy mode="STEP" compression="true" grows="3"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </field>
        <field units="" type="NX_INT32" name="pco_int32">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true"
  grows="2" shuffle="false" />
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </field>
        <field units="" type="NX_INT64" name="pco_int64">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT" name="pco_uint">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="pco_uint"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT64" name="pco_uint64">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"  grows="3"/>
          <datasource type="CLIENT">
            <record name="pco_uint"/>
          </datasource>
        </field>



        <field units="" type="NX_UINT8" name="pco_uint8">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" grows="3"/>
          <datasource type="CLIENT">
            <record name="pco_uint"/>
          </datasource>
        </field>
        <field units="" type="NX_UINT16" name="pco_uint16">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true"/>
          <datasource type="CLIENT">
            <record name="pco_uint"/>
          </datasource>
        </field>
        <field units="" type="NX_UINT32" name="pco_uint32">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true"
  grows="2" shuffle="false" />
          <datasource type="CLIENT">
            <record name="pco_uint"/>
          </datasource>
        </field>



        <field units="" type="NX_UINT8" name="pco_uint8_canfail">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" grows="3" canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_uint_canfail"/>
          </datasource>
        </field>
        <field units="" type="NX_UINT16" name="pco_uint16_canfail">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_uint_canfail"/>
          </datasource>
        </field>
        <field units="" type="NX_UINT32" name="pco_uint32_canfail">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true"  grows="2"
 shuffle="false"  canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_uint_canfail"/>
          </datasource>
        </field>





        <field units="" type="NX_INT64" name="init_pco_int64">
          <dimensions rank="2" />
          <strategy mode="INIT" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT" name="final_pco_uint">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="pco_uint"/>
          </datasource>
        </field>



        <field units="" type="NX_INT64" name="init_pco_int64_canfail">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="INIT" compression="true" rate="3" canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_int_canfail"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT" name="final_pco_uint_canfail">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_uint_canfail"/>
          </datasource>
        </field>

      </group>
    </group>
  </group>
</definition>
"""

        tdw = self.openWriter(
            fname, xml,
            json='{"data": { "pco_int":' + str(self._pco1[0]) + '  } }')

        pco2 = [[[(el + 100) // 2 for el in rpco] for rpco in pco]
                for pco in self._pco1]
        flip = True
        for pco in self._pco1:
            self.record(
                tdw, '{"data": { "pco_int":' + str(pco) +
                ', "pco_uint":' +
                str([[(el + 100) // 2 for el in rpco]
                     for rpco in pco]) +
                (', "pco_uint_canfail":' + str(
                    [[(el + 100) // 2 for el in rpco]
                     for rpco in pco]) if flip else "") +
                '  } }')
            flip = not flip
        self.closeWriter(
            tdw, json='{"data": { "pco_uint":' + str(pco2[0]) + '  } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 17)
        self._sc.checkImageField(
            det, "pco_int", "int64", "NX_INT", self._pco1)
        self._sc.checkImageField(
            det, "pco_int8", "int8", "NX_INT8", self._pco1, grows=2)
        self._sc.checkImageField(
            det, "pco_int16", "int16", "NX_INT16", self._pco1, grows=3)
        self._sc.checkImageField(
            det, "pco_int32", "int32", "NX_INT32", self._pco1, grows=2)
        self._sc.checkImageField(
            det, "pco_int64", "int64", "NX_INT64", self._pco1)
        self._sc.checkImageField(det, "pco_uint", "uint64", "NX_UINT", pco2)
        self._sc.checkImageField(
            det, "pco_uint8", "uint8", "NX_UINT8", pco2, grows=3)
        self._sc.checkImageField(
            det, "pco_uint16", "uint16", "NX_UINT16", pco2)
        self._sc.checkImageField(
            det, "pco_uint32", "uint32", "NX_UINT32", pco2, grows=2)
        self._sc.checkImageField(
            det, "pco_uint64", "uint64", "NX_UINT64", pco2, grows=3)

        self._sc.checkSingleImageField(
            det, "init_pco_int64", "int64", "NX_INT64", self._pco1[0])
        self._sc.checkSingleImageField(
            det, "final_pco_uint", "uint64", "NX_UINT", pco2[0])

# self._sc.checkSingleImageField(det, "init_pco_int64_canfail", "int64",
# "NX_INT64", self._pco1[0])
        self._sc.checkSingleImageField(
            det, "init_pco_int64_canfail", "int64", "NX_INT64",
            [[numpy.iinfo(getattr(numpy, 'int64')).max for el in rpco]
             for rpco in self._pco1[0]],
            attrs={"type": "NX_INT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkSingleImageField(
            det, "final_pco_uint_canfail", "uint64", "NX_UINT",
            [[numpy.iinfo(getattr(numpy, 'uint64')).max for el in rpco]
             for rpco in self._pco1[0]],
            attrs={"type": "NX_UINT", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkImageField(
            det, "pco_uint8_canfail", "uint8", "NX_UINT8",
            [[[((el + 100) // 2 if not j % 2 else
                numpy.iinfo(getattr(numpy, 'uint8')).max)
               for el in rpco] for rpco in self._pco1[j]]
             for j in range(len(self._pco1))],
            grows=3,
            attrs={"type": "NX_UINT8", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkImageField(
            det, "pco_uint16_canfail", "uint16", "NX_UINT16",
            [[[((el + 100) // 2 if not j % 2 else
                numpy.iinfo(getattr(numpy, 'uint16')).max)
               for el in rpco] for rpco in self._pco1[j]]
             for j in range(len(self._pco1))],
            grows=1,
            attrs={"type": "NX_UINT16", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pco_uint32_canfail", "uint32", "NX_UINT32",
            [[[((el + 100) // 2 if not j % 2 else
               numpy.iinfo(getattr(numpy, 'uint32')).max)
               for el in rpco] for rpco in self._pco1[j]] for j in range(
                   len(self._pco1))],
            grows=2,
            attrs={"type": "NX_UINT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientFloatImage(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="" type="NX_FLOAT" name="pco_float">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"/>
          <datasource type="CLIENT">
            <record name="pco_float"/>
          </datasource>
        </field>

        <field units="" type="NX_FLOAT32" name="pco_float32">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"/>
          <datasource type="CLIENT">
            <record name="pco_float"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT64" name="pco_float64">
          <dimensions rank="2" />
          <strategy mode="STEP" grows="3"/>
          <datasource type="CLIENT">
            <record name="pco_float"/>
          </datasource>
        </field>
        <field units="" type="NX_NUMBER" name="pco_number">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP"  grows = "1" />
          <datasource type="CLIENT">
            <record name="pco_float"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="pco_float32_canfail">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"
  canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_float_canfail"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT64" name="pco_float64_canfail">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP" grows="3" canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_float_canfail"/>
          </datasource>
        </field>
        <field units="" type="NX_NUMBER" name="pco_number_canfail">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP"  grows = "1"  canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_float_canfail"/>
          </datasource>
        </field>




        <field units="" type="NX_FLOAT32" name="init_pco_float32">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="INIT" compression="true" shuffle="true"/>
          <datasource type="CLIENT">
            <record name="pco_float"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT64" name="final_pco_float64">
          <dimensions rank="2" />
          <strategy mode="FINAL" />
          <datasource type="CLIENT">
            <record name="pco_float"/>
          </datasource>
        </field>




        <field units="" type="NX_FLOAT32" name="init_pco_float32_canfail">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
         <strategy mode="INIT" compression="true" shuffle="true"
canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_float_canfail"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT64" name="final_pco_float64_canfail">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true" />
          <datasource type="CLIENT">
            <record name="pco_float_canfail"/>
          </datasource>
        </field>


      </group>
    </group>
  </group>
</definition>
"""

        tdw = self.openWriter(
            fname, xml,
            json='{"data": { "pco_float":' + str(self._fpco1[0]) + '  } }')

        flip = True
        for pco in self._fpco1:
            self.record(
                tdw,
                '{"data": { "pco_float":' + str(pco) +
                (', "pco_float_canfail":' + str(pco) if flip else "") +
                '  } }')
            flip = not flip
        self.closeWriter(
            tdw,
            json='{"data": { "pco_float":' + str(self._fpco1[0]) + '  } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 11)
        self._sc.checkImageField(
            det, "pco_float", "float64", "NX_FLOAT", self._fpco1,
            error=1.0e-14)
        self._sc.checkImageField(
            det, "pco_float32", "float32", "NX_FLOAT32", self._fpco1,
            error=1.0e-6, grows=2)
        self._sc.checkImageField(
            det, "pco_float64", "float64", "NX_FLOAT64", self._fpco1,
            error=1.0e-14, grows=3)
        self._sc.checkImageField(
            det, "pco_number", "float64", "NX_NUMBER", self._fpco1,
            error=1.0e-14, grows=1)

        self._sc.checkSingleImageField(
            det, "init_pco_float32", "float32", "NX_FLOAT32", self._fpco1[0],
            error=1.0e-6)
        self._sc.checkSingleImageField(
            det, "final_pco_float64", "float64", "NX_FLOAT64", self._fpco1[0],
            error=1.0e-14)

        self._sc.checkSingleImageField(
            det, "init_pco_float32_canfail", "float32", "NX_FLOAT32",
            [[numpy.finfo(getattr(numpy, 'float32')).max for el in rpco]
             for rpco in self._fpco1[0]],
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1.0e-6)
        self._sc.checkSingleImageField(
            det, "final_pco_float64_canfail", "float64", "NX_FLOAT64",
            [[numpy.finfo(getattr(numpy, 'float64')).max for el in rpco]
             for rpco in self._fpco1[0]],
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1.0e-14)

        self._sc.checkImageField(
            det, "pco_float32_canfail", "float32", "NX_FLOAT32",
            [[[(el if not j % 2 else
               numpy.finfo(getattr(numpy, 'float32')).max)
               for el in rpco] for rpco in self._fpco1[j]] for j in range(
                   len(self._fpco1))],
            grows=2,
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1.0e-6)
        self._sc.checkImageField(
            det, "pco_float64_canfail", "float64", "NX_FLOAT64",
            [[[(el if not j % 2 else
               numpy.finfo(getattr(numpy, 'float64')).max)
               for el in rpco] for rpco in self._fpco1[j]] for j in range(
                   len(self._fpco1))],
            grows=3,
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1.0e-14)
        self._sc.checkImageField(
            det, "pco_number_canfail", "float64", "NX_NUMBER",
            [[[(el if not j % 2 else
               numpy.finfo(getattr(numpy, 'float64')).max)
               for el in rpco] for rpco in self._fpco1[j]] for j in range(
                   len(self._fpco1))],
            grows=1,
            attrs={"type": "NX_NUMBER", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            error=1.0e-14)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientImage(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="" type="NX_DATE_TIME" name="time">
          <strategy mode="STEP" compression="true" rate="3"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="timestamps"/>
          </datasource>
        </field>
        <field units="" type="ISO8601" name="isotime">
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"/>
          <dimensions rank="2" />
          <datasource type="CLIENT">
            <record name="timestamps"/>
          </datasource>
        </field>
        <field units="" type="NX_CHAR" name="string_time">
          <strategy mode="STEP" grows="2"/>
          <datasource type="CLIENT">
           <record name="timestamps"/>
          </datasource>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
        </field>





        <field units="" type="NX_BOOLEAN" name="flags">
          <strategy mode="STEP"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="logicals"/>
          </datasource>
        </field>





        <field units="" type="NX_DATE_TIME" name="time_canfail">
          <strategy mode="STEP" compression="true" rate="3" canfail="true"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="timestamps_canfail"/>
          </datasource>
        </field>
        <field units="" type="NX_CHAR" name="string_time_canfail">
          <strategy mode="STEP" grows="2" canfail="true"/>
          <datasource type="CLIENT">
           <record name="timestamps_canfail"/>
          </datasource>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
        </field>
        <field units="" type="NX_BOOLEAN" name="flags_canfail">
          <strategy mode="STEP" grows="3" canfail="true"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="logicals_canfail"/>
          </datasource>
        </field>





        <field units="" type="NX_BOOLEAN" name="bool_flags">
          <strategy mode="STEP"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="bool"/>
          </datasource>
        </field>

        <field units="" type="NX_BOOLEAN" name="flags_dim">
          <strategy mode="STEP"/>
          <dimensions rank="2" />
          <datasource type="CLIENT">
            <record name="logicals"/>
          </datasource>
        </field>



        <field units="" type="NX_CHAR" name="init_string_time">
          <strategy mode="INIT" grows="2"/>
          <datasource type="CLIENT">
           <record name="timestamps"/>
          </datasource>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
        </field>
        <field units="" type="NX_BOOLEAN" name="final_flags">
          <strategy mode="FINAL"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="logicals"/>
          </datasource>
        </field>


        <field units="" type="NX_CHAR" name="final_string_time">
          <strategy mode="FINAL" grows="2"/>
          <datasource type="CLIENT">
           <record name="timestamps"/>
          </datasource>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
        </field>
        <field units="" type="NX_BOOLEAN" name="init_flags">
          <strategy mode="INIT"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="logicals"/>
          </datasource>
        </field>



        <field units="" type="NX_CHAR" name="final_string_time_canfail">
          <strategy mode="FINAL" canfail="true"/>
          <datasource type="CLIENT">
           <record name="timestamps_canfail"/>
          </datasource>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
        </field>
        <field units="" type="NX_BOOLEAN" name="init_flags_canfail">
          <strategy mode="INIT" canfail="true"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <datasource type="CLIENT">
            <record name="logicals_canfail"/>
          </datasource>
        </field>


      </group>
    </group>
  </group>
</definition>
"""
        dates = [
            [["1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
              "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200"],
             ["1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
              "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200"],
             ["1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
              "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200"]],
            [["956-05-23T12:12:32.123+0400", "1212-12-12T12:25:43.1267-0700",
              "914-11-04T04:13:13.44-0000", "1002-04-03T14:15:03.0012-0300"],
             ["956-05-23T12:12:32.123+0400", "1212-12-12T12:25:43.1267-0700",
              "914-11-04T04:13:13.44-0000", "1002-04-03T14:15:03.0012-0300"],
             ["956-05-23T12:12:32.123+0400", "1212-12-12T12:25:43.1267-0700",
              "914-11-04T04:13:13.44-0000", "1002-04-03T14:15:03.0012-0300"]]]

        logical = [
            [["1", "0", "true", "false"],
             ["True", "False", "TrUe", "FaLsE"], ["1", "0", "0", "1"]],
            [["0", "1", "true", "false"],
             ["TrUe", "1", "0", "FaLsE"], ["0", "0", "1", "0"]]]

        bools = [
            "[ [true,false,true,false], [true,false,true,false], "
            "[true,false,false,true]]",
            "[ [false,true,true,false], [true,true,false,false], "
            "[false,false,true,false]]"]

        tdw = self.openWriter(fname, xml, json='{"data": {' +
                              '"timestamps":' +
                              str(dates[0]).replace("'", "\"") +
                              ', "logicals":' +
                              str(logical[0]).replace("'", "\"") +
                              '  } }')

        flip = True
        for i in range(min(len(dates), len(logical))):
            self.record(
                tdw,
                '{"data": {"timestamps":' + str(dates[i]).replace("'", "\"") +
                (', "timestamps_canfail":' + str(
                    dates[i]).replace("'", "\"") if flip else "") +
                (', "logicals_canfail":' + str(
                    logical[i]).replace("'", "\"") if flip else "") +
                ', "logicals":' + str(logical[i]).replace("'", "\"") +
                ', "bool":' + bools[i] +
                ' } }')
            flip = not flip

        self.closeWriter(tdw, json='{"data": {' +
                         '"timestamps":' +
                         str(dates[0]).replace("'", "\"") +
                         ', "logicals":' +
                         str(logical[0]).replace("'", "\"") +
                         '  } }')

        # check the created file

        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 15)
        self._sc.checkImageField(det, "flags", "bool", "NX_BOOLEAN", logical)
        self._sc.checkImageField(
            det, "bool_flags", "bool", "NX_BOOLEAN", logical)
        self._sc.checkImageField(det, "time", "string", "NX_DATE_TIME", dates)
        self._sc.checkImageField(
            det, "string_time", "string", "NX_CHAR", dates, grows=2)
        self._sc.checkImageField(
            det, "isotime", "string", "ISO8601", dates, grows=2)
        self._sc.checkImageField(
            det, "flags_dim", "bool", "NX_BOOLEAN", logical)

        self._sc.checkSingleImageField(
            det, "init_string_time", "string", "NX_CHAR", dates[0])
        self._sc.checkSingleImageField(
            det, "final_flags", "bool", "NX_BOOLEAN", logical[0])

        self._sc.checkSingleImageField(
            det, "final_string_time_canfail", "string", "NX_CHAR",
            [['' for el in rpco] for rpco in dates[0]],
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleImageField(
            det, "init_flags_canfail", "bool", "NX_BOOLEAN",
            [[False for el in rpco] for rpco in logical[0]],
            attrs={
                "type": "NX_BOOLEAN", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkImageField(
            det, "flags_canfail", "bool", "NX_BOOLEAN",
            [[[(el if not j % 2 else False)
               for el in rpco] for rpco in logical[j]] for j in range(
                   len(logical))],
            grows=3,
            attrs={
                "type": "NX_BOOLEAN", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkImageField(
            det, "string_time_canfail", "string", "NX_CHAR",
            [[[(el if not j % 2 else '')
               for el in rpco] for rpco in dates[j]] for j in range(
                   len(dates))],
            attrs={
                "type": "NX_CHAR", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            grows=2)
        self._sc.checkImageField(
            det, "time_canfail", "string", "NX_DATE_TIME",
            [[[(el if not j % 2 else '')
               for el in rpco] for rpco in dates[j]] for j in range(
                   len(dates))],
            attrs={
                "type": "NX_DATE_TIME", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        f.close()
        os.remove(fname)

#        <field units="" type="NX_DATE_TIME" name="time_canfail">
#        <field units="" type="NX_CHAR" name="string_time_canfail">
#        <field units="" type="NX_BOOLEAN" name="flags_canfail">

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientAttrImage(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

        <attribute type="NX_FLOAT" name="image_float">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="pco_float"/>
          </datasource>
        </attribute>

        <attribute type="NX_INT" name="image_int">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </attribute>



        <attribute type="NX_FLOAT" name="image_float_canfail">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_float_canfail"/>
          </datasource>
        </attribute>

        <attribute type="NX_INT" name="image_int_canfail">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_int_canfail"/>
          </datasource>
        </attribute>


        <attribute type="NX_INT32" name="image_int32">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </attribute>



        <attribute type="NX_BOOLEAN" name="image_bool">
          <dimensions rank="2">
            <dim value="2" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="flags"/>
          </datasource>
        </attribute>

      </group>
      <field type="NX_FLOAT" name="counter">
        <attribute type="NX_FLOAT32" name="image_float32">
          <dimensions rank="2">
            <dim value="20" index="1"/>
            <dim value="30" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="pco_float"/>
          </datasource>
        </attribute>

        <attribute type="NX_UINT32" name="image_uint32">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </attribute>

        <attribute type="NX_UINT64" name="image_uint64">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource type="CLIENT">
            <record name="pco_int"/>
          </datasource>
        </attribute>


        <attribute type="NX_BOOLEAN" name="image_bool">
          <dimensions rank="2">
            <dim value="2" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <strategy mode="INIT"/>
          <datasource type="CLIENT">
            <record name="flags"/>
          </datasource>
        </attribute>



        <attribute type="NX_UINT64" name="image_uint64_canfail">
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource type="CLIENT">
            <record name="pco_int_canfail"/>
          </datasource>
        </attribute>


        <attribute type="NX_BOOLEAN" name="image_bool_canfail">
          <dimensions rank="2">
            <dim value="2" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <strategy mode="INIT" canfail="true"/>
          <datasource type="CLIENT">
            <record name="flags_canfail"/>
          </datasource>
        </attribute>



        1.2
      </field>
    </group>
  </group>
</definition>
"""

#        <attribute type="NX_CHAR" name="flag_spectrum_string">
#          <dimensions rank="1">
#            <dim value="8" index="1"/>
#          </dimensions>
#          <strategy mode="STEP"/>
#          <datasource type="CLIENT">
#            <record name="flags"/>
#          </datasource>
#        </attribute>

        logical = [["1", "0", "true", "false"],
                   ["True", "False", "TrUe", "FaLsE"]]
        tdw = self.openWriter(
            fname, xml, json='{"data": {' +
            ' "pco_float":' + str(self._fpco1[0]) +
            ', "flags":' +
            str(logical).replace("'", "\"") +
            ', "pco_int":' + str(self._pco1[0]) +
            '  } }')
        steps = min(len(self._pco1), len(self._fpco1))
        for i in range(steps):
            self.record(tdw, '{"data": {' +
                        ' "pco_float":' + str(self._fpco1[i]) +
                        ', "pco_int":' + str(self._pco1[i]) +
                        ', "flags":' + str(logical).replace("'", "\"") +
                        '  } }')

        self.closeWriter(tdw, json='{"data": {' +
                         ' "pco_float":' + str(self._fpco1[0]) +
                         ', "pco_int":' + str(self._pco1[0]) +
                         ', "flags":' + str(logical).replace("'", "\"") +
                         '  } }')

        # check the created file
        FileWriter.writer = H5CppWriter
        f = FileWriter.open_file(fname, readonly=True)
        det, field = self._sc.checkAttributeTree(f, fname, 8, 8)
        self._sc.checkImageAttribute(
            det, "image_float", "float64", self._fpco1[steps - 1],
            error=1.e-14)
        self._sc.checkImageAttribute(det, "image_int", "int64", self._pco1[0])
        self._sc.checkImageAttribute(det, "image_bool", "bool", logical)
        self._sc.checkImageAttribute(
            det, "image_int32", "int32", self._pco1[steps - 1])
        self._sc.checkImageAttribute(
            field, "image_float32", "float32", self._fpco1[steps - 1],
            error=1.e-6)
        self._sc.checkImageAttribute(
            field, "image_uint32", "uint32", self._pco1[steps - 1])
        self._sc.checkImageAttribute(
            field, "image_uint64", "uint64", self._pco1[0])
        self._sc.checkImageAttribute(field, "image_bool", "bool", logical)

        self._sc.checkImageAttribute(
            field, "image_uint64_canfail", "uint64",
            [[numpy.iinfo(getattr(numpy, 'uint64')).max] *
             len(self._pco1[0][0])] * len(self._pco1[0]))
        self._sc.checkImageAttribute(
            field, "image_bool_canfail", "bool",
            [[False] * len(logical[0])] * len(logical))
        self._sc.checkImageAttribute(
            det, "image_float_canfail", "float64",
            [[numpy.finfo(getattr(numpy, 'float64')).max] * 30] * 20)
        self._sc.checkImageAttribute(
            det, "image_int_canfail", "int64",
            [[numpy.iinfo(getattr(numpy, 'int64')).max] *
             len(self._pco1[0][0])] * len(self._pco1[0]))
        # STRING NOT SUPPORTED BY PNINX

        self._sc.checkScalarAttribute(
            det, "nexdatas_canfail", "string", "FAILED")
        self._sc.checkScalarAttribute(
            field, "nexdatas_canfail", "string", "FAILED")
        f.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
