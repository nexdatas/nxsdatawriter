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
# \file TangoFieldTagWriterTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import numpy
import struct
import binascii
import time

try:
    import tango
except Exception:
    import PyTango as tango

from nxswriter import Types
from nxswriter.TangoDataWriter import TangoDataWriter
from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter

try:
    from pninexus import h5cpp
    if hasattr(h5cpp.filter, "is_filter_available") \
       and h5cpp.filter.is_filter_available(32008):
        BSFILTER = True
    else:
        BSFILTER = False
except Exception:
    BSFILTER = False


try:
    from ProxyHelper import ProxyHelper
except Exception:
    from .ProxyHelper import ProxyHelper

try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker

try:
    import SimpleServerSetUp
except Exception:
    from . import SimpleServerSetUp


#: (:obj:`bool`) tango bug #213 flag related to EncodedAttributes in python3
PYTG_BUG_213 = False
try:
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

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class TangoFieldTagWriterH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._simps = SimpleServerSetUp.SimpleServerSetUp()

        try:
            # random seed
            self.seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.seed)

        self._counter = [1, -2, 6, -8, 9, -11]
        self._bools = ["TruE", "0", "1", "False", "false", "True"]
        self._fcounter = [1.1, -2.4, 6.54, -8.456, 9.456, -0.46545]
        self._dcounter = [
            0.1, -2342.4, 46.54, -854.456, 9.243456, -0.423426545]
        self._logical = [[True, False, True, False], [
            True, False, False, True], [False, False, True, True]]

        self._logical2 = [
            [[True, False, True, False], [True, False, False, True]],
            [[False, False, True, True], [
                False, False, True, False]],
            [[True, False, True, True], [False, False, True, False]]]

        self._sc = Checker(self)
        self._mca1 = [[self.__rnd.randint(-100, 100)
                       for e in range(256)] for i in range(3)]
        self._mca2 = [[self.__rnd.randint(0, 100)
                       for e in range(256)] for i in range(3)]
        self._fmca1 = [self._sc.nicePlot(1024, 10) for i in range(4)]
#        self._fmca2 = [(float(e)/(100.+e)) for e in range(2048)]

        self._dates = [
            ["1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
             "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200"],
            ["1956-05-23T12:12:32.123+0400", "1212-12-12T12:25:43.1267-0700",
             "914-11-04T04:13:13.44-0000", "1002-04-03T14:15:03.0012-0300"],
            ["1966-02-21T11:22:02.113+0200", "1432-12-11T11:23:13.1223-0300",
             "1714-11-10T14:03:13.12-0400", "1001-01-01T14:11:11.0011-0100"]]

        self._dates2 = [
            [["1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
              "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200"],
             ["1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
              "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200"]],
            [["1996-07-31T21:15:22.123+0600", "2012-11-14T14:05:23.2344-0200",
              "2014-02-04T04:16:12.43-0100", "2012-11-14T14:05:23.2344-0200"],
             ["956-05-23T12:12:32.123+0400", "1212-12-12T12:25:43.1267-0700",
              "914-11-04T04:13:13.44-0000", "1002-04-03T14:15:03.0012-0300"]],
            [["956-05-23T12:12:32.123+0400", "1212-12-12T12:25:43.1267-0700",
              "914-11-04T04:13:13.44-0000", "1002-04-03T14:15:03.0012-0300"],
             ["956-05-23T12:12:32.123+0400", "1212-12-12T12:25:43.1267-0700",
              "914-11-04T04:13:13.44-0000", "1002-04-03T14:15:03.0012-0300"]]]

        self._pco1 = [[[self.__rnd.randint(0, 100) for e1 in range(8)]
                       for e2 in range(10)] for i in range(3)]
        self._fpco1 = [self._sc.nicePlot2D(20, 30, 5) for i in range(4)]

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self._dbhost = None
        self._dbport = None

    # test starter
    # \brief Common set up
    def setUp(self):
        self._simps.setUp()
        self._dbhost = self._simps.dp.get_db_host()
        self._dbport = self._simps.dp.get_db_port()
        print("SEED = %s" % self.seed)
        print("CHECKER SEED = %s" % self._sc.seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        self._simps.tearDown()

    # opens writer
    # \param fname file name
    # \param xml XML settings
    # \param json JSON Record with client settings
    # \returns Tango Data Writer instance
    def openWriter(self, fname, xml, json=None):
        tdw = TangoDataWriter()
        tdw.fileName = fname
#        tdw.numberOfThreads = 1
        self.setProp(tdw, "writer", "h5py")

        tdw.openFile()
        tdw.xmlsettings = xml
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

    def setProp(self, rc, name, value):
        setattr(rc, name, value)

    # performs one record step
    def record(self, tdw, string):
        tdw.record(string)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoScalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

       <field units="m" type="NX_BOOLEAN" name="ScalarBoolean">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarBoolean"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT8" name="ScalarUChar">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarUChar"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT16" name="ScalarShort">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarShort"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT16" name="ScalarUShort">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarUShort"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT" name="ScalarLong">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarLong"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT" name="ScalarULong">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarULong"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT64" name="ScalarLong64">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarLong64"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT32" name="ScalarFloat">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarFloat"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT64" name="ScalarDouble">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarDouble"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarString">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarString"/>
          </datasource>
        </field>

        <field units="m" type="NX_CHAR" name="ScalarEncoded">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
            <record name="ScalarEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="UTF8"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarEncoded_MUTF8">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
            <record name="ScalarEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="MUTF8"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarState">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="State"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT32" name="InitScalarULong">
          <strategy mode="INIT"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarULong"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT64" name="FinalScalarDouble">
          <strategy mode="FINAL"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarDouble"/>
          </datasource>
        </field>


        <field units="m" type="NX_UINT64" name="ScalarULong64">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarULong64"/>
          </datasource>
        </field>


      </group>
    </group>
  </group>
</definition>
"""

        xml = xml.replace("localhost", self._dbhost)
        self._simps.dp.ScalarULong = abs(self._counter[0])

        decoder = '"decoders":{"MUTF8":"nxswriter.DecoderPool.UTF8decoder"}'
        tdw = self.openWriter(fname, xml, json='{ ' + decoder + ' }')

        steps = min(len(self._counter), len(self._fcounter), len(self._bools))
        for i in range(steps):
            self._simps.dp.ScalarBoolean = Types.Converters.toBool(
                self._bools[i])
            self._simps.dp.ScalarUChar = abs(self._counter[i])
            self._simps.dp.ScalarShort = self._counter[i]
            self._simps.dp.ScalarUShort = abs(self._counter[i])
            self._simps.dp.ScalarLong = self._counter[i]
            self._simps.dp.ScalarULong = abs(self._counter[i])
            self._simps.dp.ScalarLong64 = self._counter[i]
            self._simps.dp.ScalarFloat = self._fcounter[i]
            self._simps.dp.ScalarDouble = self._dcounter[i]
            self._simps.dp.ScalarString = self._bools[i]
            self._simps.dp.ScalarULong64 = int(abs(self._counter[i]))
            self.record(tdw, '{}')
#            self._fcounter[i] = self._simps.dp.ScalarFloat
#            self._dcounter[i] = self._simps.dp.ScalarDouble

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 16)
        self._sc.checkScalarField(
            det, "ScalarBoolean", "bool", "NX_BOOLEAN", self._bools)
        self._sc.checkScalarField(
            det, "ScalarUChar", "uint8", "NX_UINT8",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ScalarShort", "int16", "NX_INT16", self._counter)
        self._sc.checkScalarField(
            det, "ScalarUShort", "uint16", "NX_UINT16",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ScalarLong", "int64", "NX_INT", self._counter)
        self._sc.checkScalarField(
            det, "ScalarULong", "uint64", "NX_UINT",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ScalarLong64", "int64", "NX_INT64", self._counter)
        self._sc.checkScalarField(
            det, "ScalarULong64", "uint64", "NX_UINT64",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ScalarFloat", "float32", "NX_FLOAT32",
            self._fcounter, error=1e-6)
        self._sc.checkScalarField(
            det, "ScalarDouble", "float64", "NX_FLOAT64",
            self._dcounter, error=1e-14)
        self._sc.checkScalarField(
            det, "ScalarString", "string", "NX_CHAR", self._bools)
        self._sc.checkScalarField(
            det, "ScalarEncoded", "string", "NX_CHAR", [
                u'Hello UTF8! Pr\xf3ba \u6d4b' for c in self._bools])
        self._sc.checkScalarField(
            det, "ScalarEncoded_MUTF8", "string", "NX_CHAR", [
                u'Hello UTF8! Pr\xf3ba \u6d4b' for c in self._bools])
        self._sc.checkScalarField(
            det, "ScalarState", "string", "NX_CHAR",
            ["ON" for c in self._bools])

        # writing encoded attributes not supported for tango 7.2.3

        self._sc.checkSingleScalarField(
            det, "InitScalarULong", "uint32", "NX_UINT32",
            abs(self._counter[0]))
        self._sc.checkSingleScalarField(
            det, "FinalScalarDouble", "float64", "NX_FLOAT64",
            self._dcounter[steps - 1], error=1e-14)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoScalar_client(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

       <field units="m" type="NX_BOOLEAN" name="ScalarBoolean">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarBoolean"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT8" name="ScalarUChar">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarUChar"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT16" name="ScalarShort">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarShort"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT16" name="ScalarUShort">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarUShort"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT" name="ScalarLong">
          <strategy mode="STEP"/>
          <datasource type="TANGO" name="scalarlong">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarLong"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT" name="ScalarULong">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarULong"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT64" name="ScalarLong64">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarLong64"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT32" name="ScalarFloat">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarFloat"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT64" name="ScalarDouble">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarDouble"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarString">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarString"/>
          </datasource>
        </field>

        <field units="m" type="NX_CHAR" name="ScalarEncoded">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
            <record name="ScalarEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__"
 encoding="UTF8"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarEncoded_MUTF8">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
            <record name="ScalarEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__"
 encoding="MUTF8"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarState">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="State"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT32" name="InitScalarULong">
          <strategy mode="INIT"/>
          <datasource type="TANGO" name="cnt_64">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__"/>
           <record name="ScalarULong"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT64" name="FinalScalarDouble">
          <strategy mode="FINAL"/>
          <datasource type="TANGO">
           <device member="attribute"
name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarDouble"/>
          </datasource>
        </field>


        <field units="m" type="NX_UINT64" name="ScalarULong64">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" group="__CLIENT__" />
           <record name="ScalarULong64"/>
          </datasource>
        </field>


      </group>
    </group>
  </group>
</definition>
"""

        xml = xml.replace("localhost", self._dbhost)
        self._simps.dp.ScalarULong = abs(self._counter[0])
        fdbhost = self._dbhost
        sdbhost = self._dbhost.split(".")[0]

        decoder = '"decoders":{"MUTF8":"nxswriter.DecoderPool.UTF8decoder"}'

        uc = abs(self._counter[1])
        tdw = self.openWriter(
            fname, xml,
            json='{"data": { "cnt_64":' + str(uc) + ' }, ' +
            decoder + ' }')

        # tdw = self.openWriter(fname, xml, json='{ ' + decoder + ' }')

        steps = min(len(self._counter), len(self._fcounter), len(self._bools))
        for i in range(steps):

            self._simps.dp.ScalarBoolean = Types.Converters.toBool(
                self._bools[i])
            self._simps.dp.ScalarUChar = abs(self._counter[i])
            self._simps.dp.ScalarShort = self._counter[i]
            self._simps.dp.ScalarUShort = abs(self._counter[0])
            self._simps.dp.ScalarLong = self._counter[0]
            self._simps.dp.ScalarULong = abs(self._counter[i])
            self._simps.dp.ScalarLong64 = self._counter[i]
            self._simps.dp.ScalarFloat = self._fcounter[i]
            self._simps.dp.ScalarDouble = self._dcounter[i]
            self._simps.dp.ScalarString = self._bools[i]
            self._simps.dp.ScalarULong64 = int(abs(self._counter[i]))
            self.record(
                tdw,
                '{"data": {'
                '"tango://%s:10000/stestp09/testss/s1r228/scalarboolean":'
                % fdbhost + str(self._bools[i]).lower() +
                ", " +
                '"%s:10000/stestp09/testss/s1r228/scalaruchar":'
                % fdbhost + str(abs(self._counter[i])) +
                ", " +
                '"%s:10000/stestp09/testss/s1r228/scalarshort":'
                % sdbhost + str(self._counter[i]) +
                ", " +
                '"%s:10000/stestp09/testss/s1r228/scalarushort":'
                % sdbhost + str(abs(self._counter[i])) +
                ", " +
                '"scalarlong":' + str(self._counter[i]) +
                '} }')
#            self._fcounter[i] = self._simps.dp.ScalarFloat
#            self._dcounter[i] = self._simps.dp.ScalarDouble

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 16)
        self._sc.checkScalarField(
            det, "ScalarBoolean", "bool", "NX_BOOLEAN", self._bools)
        self._sc.checkScalarField(
            det, "ScalarUChar", "uint8", "NX_UINT8",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ScalarShort", "int16", "NX_INT16", self._counter)
        self._sc.checkScalarField(
            det, "ScalarUShort", "uint16", "NX_UINT16",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ScalarLong", "int64", "NX_INT", self._counter)
        self._sc.checkScalarField(
            det, "ScalarULong", "uint64", "NX_UINT",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ScalarLong64", "int64", "NX_INT64",
            self._counter)
        self._sc.checkScalarField(
            det, "ScalarULong64", "uint64", "NX_UINT64",
            [abs(c) for c in self._counter])
        self._sc.checkScalarField(
            det, "ScalarFloat", "float32", "NX_FLOAT32",
            self._fcounter, error=1e-6)
        self._sc.checkScalarField(
            det, "ScalarDouble", "float64", "NX_FLOAT64",
            self._dcounter, error=1e-14)
        self._sc.checkScalarField(
            det, "ScalarString", "string", "NX_CHAR", self._bools)
        self._sc.checkScalarField(
            det,
            "ScalarEncoded", "string", "NX_CHAR", [
                u'Hello UTF8! Pr\xf3ba \u6d4b' for c in self._bools])
        self._sc.checkScalarField(
            det, "ScalarEncoded_MUTF8", "string", "NX_CHAR", [
                u'Hello UTF8! Pr\xf3ba \u6d4b' for c in self._bools])
        self._sc.checkScalarField(
            det, "ScalarState", "string", "NX_CHAR",
            ["ON" for c in self._bools])

        # writing encoded attributes not supported for tango 7.2.3

        self._sc.checkSingleScalarField(
            det, "InitScalarULong", "uint32", "NX_UINT32",

            abs(self._counter[1]))
        self._sc.checkSingleScalarField(
            det, "FinalScalarDouble", "float64", "NX_FLOAT64",
            self._dcounter[steps - 1], error=1e-14)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoImage_bsfilter(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        if BSFILTER:
            xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">


       <field units="" type="NX_BOOLEAN" name="ImageBoolean">
          <strategy mode="STEP"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageBoolean"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT8" name="ImageUChar">
          <strategy mode="STEP"   compression="32008"
 compression_opts="0,0" grows="2" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUChar"/>
          </datasource>
        </field>

       <field units="" type="NX_INT16" name="ImageShort">
          <strategy mode="STEP"    compression="32008"  grows="3"
 shuffle="false"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageShort"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT16" name="ImageUShort">
          <strategy mode="STEP"   grows="1"   />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUShort"/>
          </datasource>
        </field>

       <field units="" type="NX_INT32" name="ImageLong">
          <strategy mode="STEP" grows="2">
            <filter index="0" name="shuffle" />
            <filter index="1" id="32008" cd_values="0,2" />
          </strategy>
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT32" name="ImageULong">
          <strategy mode="STEP"  grows="3"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong"/>
          </datasource>
        </field>


       <field units="" type="NX_INT64" name="ImageLong64">
          <strategy mode="STEP"  compression="32008"  grows="1"
 shuffle="false"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong64"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT64" name="ImageULong64">
          <strategy mode="STEP"  compression="32008"
 compression_opts="0,0"  grows="2"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT32" name="ImageFloat">
          <strategy mode="STEP"  compression="32008"
 compression_opts="0,2"  grows="3"
 shuffle="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT64" name="ImageDouble">
          <strategy mode="STEP"  compression="32008"  grows="1"   />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageDouble"/>
          </datasource>
        </field>

       <field units="" type="NX_CHAR" name="ImageString">
          <strategy mode="STEP"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageString"/>
          </datasource>
        </field>



       <field units="" type="NX_UINT64" name="InitImageULong64">
          <strategy mode="INIT" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="FinalImageFloat">
          <strategy mode="FINAL"  compression="32008"  shuffle="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>



      </group>
    </group>
  </group>
</definition>
"""

            xml = xml.replace("localhost", self._dbhost)

            self._simps.dp.ImageBoolean = self._logical2[0]
            self._simps.dp.ImageUChar = self._pco1[0]
            self._simps.dp.ImageShort = self._pco1[0]
            self._simps.dp.ImageUShort = self._pco1[0]
            self._simps.dp.ImageLong = self._pco1[0]
            self._simps.dp.ImageULong = self._pco1[0]
            self._simps.dp.ImageLong64 = self._pco1[0]
            self._simps.dp.ImageULong64 = self._pco1[0]
            self._simps.dp.ImageFloat = self._fpco1[0]
            self._simps.dp.ImageDouble = self._fpco1[0]
            self._simps.dp.ImageString = self._dates2[0]

    #        print self._fmca1[0]

            decoder = '"decoders":' \
                      '{"MLIMA":"nxswriter.DecoderPool.VDEOdecoder"}'
            tdw = self.openWriter(fname, xml, json='{ ' + decoder + ' }')

            dp = tango.DeviceProxy("stestp09/testss/s1r228")
            self.assertTrue(ProxyHelper.wait(dp, 10000))

            steps = min(len(self._pco1), len(self._logical2),
                        len(self._fpco1))
            for i in range(steps):
                self._simps.dp.ImageBoolean = self._logical2[i]
                self._simps.dp.ImageUChar = self._pco1[i]
                self._simps.dp.ImageShort = self._pco1[i]
                self._simps.dp.ImageUShort = self._pco1[i]
                self._simps.dp.ImageLong = self._pco1[i]
                self._simps.dp.ImageULong = self._pco1[i]
                self._simps.dp.ImageLong64 = self._pco1[i]
                self._simps.dp.ImageULong64 = self._pco1[i]
                self._simps.dp.ImageFloat = self._fpco1[i]
                self._simps.dp.ImageDouble = self._fpco1[i]
                self._simps.dp.ImageString = self._dates2[i]

                self.record(tdw, '{}')
                pass
            self.closeWriter(tdw)

            # check the created file

            FileWriter.writer = H5PYWriter
            f = FileWriter.open_file(fname, readonly=True)
            det = self._sc.checkFieldTree(f, fname, 13)
            self._sc.checkImageField(
                det, "ImageBoolean", "bool", "NX_BOOLEAN",
                self._logical2[:steps])
            self._sc.checkImageField(
                det, "ImageUChar", "uint8", "NX_UINT8", self._pco1[:steps],
                grows=2)
            self._sc.checkImageField(
                det, "ImageShort", "int16", "NX_INT16", self._pco1[:steps],
                grows=3)
            self._sc.checkImageField(
                det, "ImageUShort", "uint16", "NX_UINT16", self._pco1[:steps],
                grows=1)
            self._sc.checkImageField(
                det, "ImageLong", "int32", "NX_INT32", self._pco1[:steps],
                grows=2)
            self._sc.checkImageField(
                det, "ImageULong", "uint32", "NX_UINT32", self._pco1[:steps],
                grows=3)
            self._sc.checkImageField(
                det, "ImageLong64", "int64", "NX_INT64", self._pco1[:steps],
                grows=1)
            self._sc.checkImageField(
                det, "ImageULong64", "uint64", "NX_UINT64", self._pco1[:steps],
                grows=2)
            self._sc.checkImageField(
                det, "ImageFloat", "float32", "NX_FLOAT32",
                self._fpco1[:steps],
                grows=3, error=1.0e-6)
            self._sc.checkImageField(
                det, "ImageDouble", "float64", "NX_FLOAT64",
                self._fpco1[:steps],
                grows=1, error=1.0e-14)
            self._sc.checkImageField(
                det, "ImageString", "string", "NX_CHAR", self._dates2[:steps])

            self._sc.checkSingleImageField(
                det, "InitImageULong64", "uint64", "NX_UINT64", self._pco1[0])
            self._sc.checkSingleImageField(
                det, "FinalImageFloat", "float32", "NX_FLOAT32",
                self._fpco1[steps - 1], error=1.0e-6)
            f.close()
            os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoScalar_canfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

       <field units="m" type="NX_BOOLEAN" name="ScalarBoolean">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarBoolean"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT8" name="ScalarUChar">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarUChar"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT16" name="ScalarShort">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarShort"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT16" name="ScalarUShort">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarUShort"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT" name="ScalarLong">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarLong"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT" name="ScalarULong">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarULong"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT64" name="ScalarLong64">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarLong64"/>
          </datasource>
        </field>


        <field units="m" type="NX_UINT64" name="ScalarULong64">
          <strategy mode="STEP"  canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarULong64"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT32" name="ScalarFloat">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarFloat"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT64" name="ScalarDouble">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarDouble"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarString">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarString"/>
          </datasource>
        </field>

        <field units="m" type="NX_CHAR" name="ScalarEncoded">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
            <record name="ScalarEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="UTF8"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarEncoded_MUTF8">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
            <record name="ScalarEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="MUTF8"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarState">
          <strategy mode="STEP" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="State"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT32" name="InitScalarULong">
          <strategy mode="INIT" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarULong_canfail"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT64" name="FinalScalarDouble">
          <strategy mode="FINAL" canfail="true"/>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarDouble"/>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        xml = xml.replace("localhost", self._dbhost)

        self._simps.dp.ScalarULong = abs(self._counter[0])

        decoder = '"decoders":{"MUTF8":"nxswriter.DecoderPool.UTF8decoder"}'

        tdw = self.openWriter(fname, xml, json='{ ' + decoder + ' }')

        steps = min(len(self._counter), len(self._fcounter), len(self._bools))
        for i in range(steps):
            if i % 2:
                self._simps.setUp()
                self._simps.dp.ScalarBoolean = Types.Converters.toBool(
                    self._bools[i])
                self._simps.dp.ScalarUChar = abs(self._counter[i])
                self._simps.dp.ScalarShort = self._counter[i]
                self._simps.dp.ScalarUShort = abs(self._counter[i])
                self._simps.dp.ScalarLong = self._counter[i]
                self._simps.dp.ScalarULong = abs(self._counter[i])
                self._simps.dp.ScalarLong64 = self._counter[i]
                self._simps.dp.ScalarFloat = self._fcounter[i]
                self._simps.dp.ScalarDouble = self._dcounter[i]
                self._simps.dp.ScalarString = self._bools[i]
                self._simps.dp.ScalarULong64 = int(abs(self._counter[i]))
            else:
                self._simps.tearDown()

            self.record(tdw, '{}')

        self._simps.tearDown()
        self.closeWriter(tdw)
        self._simps.setUp()
        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 16)
        self._sc.checkScalarField(
            det, "ScalarBoolean", "bool", "NX_BOOLEAN",
            [(Types.Converters.toBool(self._bools[i]) if i % 2 else False)
             for i in range(steps)],
            attrs={
                "type": "NX_BOOLEAN", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "ScalarUChar", "uint8", "NX_UINT8",
            [(abs(self._counter[i]) if i % 2
              else numpy.iinfo(getattr(numpy, 'uint8')).max)
             for i in range(steps)],
            attrs={"type": "NX_UINT8", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "ScalarShort", "int16", "NX_INT16",
            [(self._counter[i] if i % 2
              else numpy.iinfo(getattr(numpy, 'int16')).max)
             for i in range(steps)],
            attrs={"type": "NX_INT16", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "ScalarUShort", "uint16", "NX_UINT16",
            [(abs(self._counter[i]) if i % 2
              else numpy.iinfo(getattr(numpy, 'uint16')).max)
             for i in range(steps)],
            attrs={
                "type": "NX_UINT16", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "ScalarLong", "int64", "NX_INT",
            [(self._counter[i] if i % 2
              else numpy.iinfo(getattr(numpy, 'int64')).max)
             for i in range(steps)],
            attrs={"type": "NX_INT", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "ScalarULong", "uint64", "NX_UINT",
            [(abs(self._counter[i]) if i % 2
              else numpy.iinfo(getattr(numpy, 'uint64')).max)
             for i in range(steps)],
            attrs={"type": "NX_UINT", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "ScalarLong64", "int64", "NX_INT64",
            [(self._counter[i] if i % 2
              else numpy.iinfo(getattr(numpy, 'int64')).max)
             for i in range(steps)],
            attrs={"type": "NX_INT64", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": None, "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "ScalarULong64", "uint64", "NX_UINT",
            [(abs(self._counter[i]) if i % 2
              else numpy.iinfo(getattr(numpy, 'uint64')).max)
             for i in range(steps)],
            attrs={
                "type": "NX_UINT64", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "ScalarFloat", "float32", "NX_FLOAT32",
            [(self._fcounter[i] if i % 2
              else numpy.finfo(getattr(numpy, 'float32')).max)
             for i in range(steps)],
            attrs={
                "type": "NX_FLOAT32", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1e-6)

        self._sc.checkScalarField(
            det, "ScalarDouble", "float64", "NX_FLOAT64",
            [(self._dcounter[i] if i % 2
              else numpy.finfo(getattr(numpy, 'float64')).max)
             for i in range(steps)],
            attrs={
                "type": "NX_FLOAT64", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1e-14)

        self._sc.checkScalarField(
            det, "ScalarString", "string", "NX_CHAR",
            [(self._bools[i] if i % 2 else '') for i in range(steps)],
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkScalarField(
            det, "ScalarEncoded", "string", "NX_CHAR",
            [(u'Hello UTF8! Pr\xf3ba \u6d4b' if i % 2 else '')
             for i in range(steps)],
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkScalarField(
            det, "ScalarEncoded_MUTF8", "string", "NX_CHAR",
            [(u'Hello UTF8! Pr\xf3ba \u6d4b' if i % 2 else '')
             for i in range(steps)],
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkScalarField(
            det, "ScalarState", "string", "NX_CHAR",
            [("ON" if i % 2 else '') for i in range(steps)],
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        # writing encoded attributes not supported for tango 7.2.3
        self._sc.checkSingleScalarField(
            det, "InitScalarULong", "uint32", "NX_UINT32",
            numpy.iinfo(getattr(numpy, 'uint32')).max,
            attrs={
                "type": "NX_UINT32", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleScalarField(
            det, "FinalScalarDouble", "float64", "NX_FLOAT64",
            numpy.finfo(getattr(numpy, 'float64')).max,
            attrs={
                "type": "NX_FLOAT64", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoSpectrum_canfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

       <field units="" type="NX_BOOLEAN" name="SpectrumBoolean">
          <strategy mode="STEP" canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumBoolean"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT8" name="SpectrumUChar">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="false" canfail="true" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumUChar"/>
          </datasource>
        </field>

       <field units="" type="NX_INT16" name="SpectrumShort">
          <strategy mode="STEP"  compression="true"  grows="3"
 shuffle="True"  canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumShort"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT16" name="SpectrumUShort">
          <strategy mode="STEP"   grows="2"  canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumUShort"/>
          </datasource>
        </field>



       <field units="" type="NX_INT32" name="SpectrumLong">
          <strategy mode="STEP"  compression="true"   shuffle="false"
 canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT32" name="SpectrumULong">
          <strategy mode="STEP"   compression="true"  grows="1"
 canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumULong"/>
          </datasource>
        </field>




       <field units="" type="NX_INT64" name="SpectrumLong64">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="True" canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT64" name="SpectrumULong64">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="True" canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumULong64"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT32" name="SpectrumFloat">
          <strategy mode="STEP"  canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumFloat"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT64" name="SpectrumDouble">
          <strategy mode="STEP"  compression="true"  grows="1"
 shuffle="false" canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumDouble"/>
          </datasource>
        </field>

       <field units="" type="NX_CHAR" name="SpectrumString">
          <strategy mode="STEP" canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumString"/>
          </datasource>
        </field>

        <field units="" type="NX_INT32" name="SpectrumEncoded">
          <strategy mode="STEP" canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
            <record name="SpectrumEncoded"/>
            <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="UINT32"/>
          </datasource>
        </field>


        <field units="" type="NX_INT32" name="SpectrumEncoded_MUINT32">
          <strategy mode="STEP" canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
            <record name="SpectrumEncoded"/>
            <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="MUINT32"/>
          </datasource>
        </field>



       <field units="" type="NX_INT64" name="InitSpectrumLong64">
          <strategy mode="INIT"  compression="true"  shuffle="True"
 canfail="true"/>
          <dimensions rank="1">
            <dim value="256" index="1"/>
          </dimensions>
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong64_canfail"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT32" name="FinalSpectrumFloat">
          <strategy mode="FINAL"  canfail="true"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumFloat"/>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        xml = xml.replace("localhost", self._dbhost)

        self._simps.dp.SpectrumBoolean = self._logical[0]
        self._simps.dp.SpectrumUChar = self._mca2[0]
        self._simps.dp.SpectrumShort = self._mca1[0]
        self._simps.dp.SpectrumUShort = self._mca2[0]
        self._simps.dp.SpectrumLong = self._mca1[0]
        self._simps.dp.SpectrumULong = self._mca2[0]
        self._simps.dp.SpectrumLong64 = self._mca1[0]
        self._simps.dp.SpectrumULong64 = self._mca2[0]
        self._simps.dp.SpectrumFloat = self._fmca1[0]
        self._simps.dp.SpectrumDouble = self._fmca1[0]
        self._simps.dp.SpectrumString = self._dates[0]

        decoder = '"decoders":{"MUINT32":' + \
                  '"nxswriter.DecoderPool.UINT32decoder"}'
        tdw = self.openWriter(fname, xml, json='{ ' + decoder + ' }')

        dp = tango.DeviceProxy("stestp09/testss/s1r228")
        self.assertTrue(ProxyHelper.wait(dp, 10000))

        steps = min(len(self._logical), len(
            self._mca1), len(self._mca2), len(self._dates))
        self._simps.tearDown()
        for i in range(steps):
            if not i % 2:
                self._simps.setUp()

                self._simps.dp.SpectrumBoolean = self._logical[i]
                self._simps.dp.SpectrumUChar = self._mca2[i]
                self._simps.dp.SpectrumShort = self._mca1[i]
                self._simps.dp.SpectrumUShort = self._mca2[i]
                self._simps.dp.SpectrumLong = self._mca1[i]
                self._simps.dp.SpectrumULong = self._mca2[i]
                self._simps.dp.SpectrumLong64 = self._mca1[i]
                self._simps.dp.SpectrumULong64 = self._mca2[i]
                self._simps.dp.SpectrumFloat = self._fmca1[i]
                self._simps.dp.SpectrumDouble = self._fmca1[i]
                self._simps.dp.SpectrumString = self._dates[i]

            else:
                self._simps.tearDown()

            self.record(tdw, '{}')

        self._simps.tearDown()
        self.closeWriter(tdw)
        self._simps.setUp()

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 15)
        self._sc.checkSpectrumField(
            det, "SpectrumBoolean", "bool", "NX_BOOLEAN",
            [(self._logical[i] if not i % 2 else [False] *
              len(self._logical[i]))
             for i in range(steps)],
            attrs={
                "type": "NX_BOOLEAN", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSpectrumField(
            det, "SpectrumUChar", "uint8", "NX_UINT8",
            [(self._mca2[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'uint8')).max] *
              len(self._mca2[i]))
             for i in range(steps)],
            attrs={"type": "NX_UINT8", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=2)
        self._sc.checkSpectrumField(
            det, "SpectrumShort", "int16", "NX_INT16",
            [(self._mca1[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'int16')).max] *
              len(self._mca1[i]))
             for i in range(steps)],
            attrs={"type": "NX_INT16", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=3)
        self._sc.checkSpectrumField(
            det, "SpectrumUShort", "uint16", "NX_UINT16",
            [(self._mca2[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'uint16')).max] *
              len(self._mca2[i]))
             for i in range(steps)],
            attrs={"type": "NX_UINT16", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=2)

        self._sc.checkSpectrumField(
            det, "SpectrumLong", "int32", "NX_INT32",
            [(self._mca1[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'int32')).max] *
              len(self._mca1[i]))
             for i in range(steps)],
            attrs={"type": "NX_INT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSpectrumField(
            det, "SpectrumULong", "uint32", "NX_UINT32",
            [(self._mca2[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'uint32')).max] *
              len(self._mca2[i]))
             for i in range(steps)],
            attrs={"type": "NX_UINT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=1)

        self._sc.checkSpectrumField(
            det, "SpectrumLong64", "int64", "NX_INT64",
            [(self._mca1[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'int64')).max] *
              len(self._mca1[i]))
             for i in range(steps)],
            attrs={"type": "NX_INT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=2)
        self._sc.checkSpectrumField(
            det, "SpectrumULong64", "uint64", "NX_UINT64",
            [(self._mca2[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'uint64')).max] *
              len(self._mca2[i]))
             for i in range(steps)],
            attrs={"type": "NX_UINT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=2)

        self._sc.checkSpectrumField(
            det, "SpectrumFloat", "float32", "NX_FLOAT32",
            [(self._fmca1[i] if not i % 2
              else [numpy.finfo(getattr(numpy, 'float32')).max] *
              len(self._fmca1[i]))
             for i in range(steps)],
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            grows=0, error=1e-6)

        self._sc.checkSpectrumField(
            det, "SpectrumDouble", "float64", "NX_FLOAT64",
            [(self._fmca1[i] if not i % 2
              else [numpy.finfo(getattr(numpy, 'float64')).max] *
              len(self._fmca1[i]))
             for i in range(steps)],
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            grows=1, error=1e-14)

        self._sc.checkSpectrumField(
            det, "SpectrumString", "string", "NX_CHAR",
            [(self._dates[i] if not i % 2 else [''] * len(self._dates[i]))
             for i in range(steps)],
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        # writing encoded attributes not supported for tango 7.2.3

        self._sc.checkSpectrumField(
            det, "SpectrumEncoded", "int32", "NX_INT32",
            [(self._mca2[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'int32')).max] *
              len(self._mca2[i]))
             for i in range(steps)],
            attrs={"type": "NX_INT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkSpectrumField(
            det, "SpectrumEncoded_MUINT32", "int32", "NX_INT32",
            [(self._mca2[i] if not i % 2
              else [numpy.iinfo(getattr(numpy, 'int32')).max] *
              len(self._mca2[i]))
             for i in range(steps)],
            attrs={"type": "NX_INT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkSingleSpectrumField(
            det, "InitSpectrumLong64", "int64", "NX_INT64",
            [numpy.iinfo(getattr(numpy, 'int64')).max] * len(self._mca1[0]),
            attrs={"type": "NX_INT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkSingleSpectrumField(
            det, "FinalSpectrumFloat", "float32", "NX_FLOAT32",
            [numpy.finfo(getattr(numpy, 'float32')).max] * len(self._fmca1[0]),
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1.0e-06)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoSpectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

       <field units="" type="NX_BOOLEAN" name="SpectrumBoolean">
          <strategy mode="STEP"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumBoolean"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT8" name="SpectrumUChar">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="false" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumUChar"/>
          </datasource>
        </field>

       <field units="" type="NX_INT16" name="SpectrumShort">
          <strategy mode="STEP"  compression="true"  grows="3"
 shuffle="True" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumShort"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT16" name="SpectrumUShort">
          <strategy mode="STEP"   grows="2" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumUShort"/>
          </datasource>
        </field>



       <field units="" type="NX_INT32" name="SpectrumLong">
          <strategy mode="STEP"  compression="true"   shuffle="false" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT32" name="SpectrumULong">
          <strategy mode="STEP"   compression="true"  grows="1" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumULong"/>
          </datasource>
        </field>




       <field units="" type="NX_INT64" name="SpectrumLong64">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="True"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT64" name="SpectrumULong64">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="True"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumULong64"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT32" name="SpectrumFloat">
          <strategy mode="STEP" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumFloat"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT64" name="SpectrumDouble">
          <strategy mode="STEP"  compression="true"  grows="1"
 shuffle="false"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumDouble"/>
          </datasource>
        </field>

       <field units="" type="NX_CHAR" name="SpectrumString">
          <strategy mode="STEP"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumString"/>
          </datasource>
        </field>

        <field units="" type="NX_INT32" name="SpectrumEncoded">
          <strategy mode="STEP"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
            <record name="SpectrumEncoded"/>
            <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="UINT32"/>
          </datasource>
        </field>


        <field units="" type="NX_INT32" name="SpectrumEncoded_MUINT32">
          <strategy mode="STEP"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
            <record name="SpectrumEncoded"/>
            <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="MUINT32"/>
          </datasource>
        </field>



       <field units="" type="NX_INT64" name="InitSpectrumLong64">
          <strategy mode="INIT"  compression="true"  shuffle="True"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT32" name="FinalSpectrumFloat">
          <strategy mode="FINAL" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumFloat"/>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        xml = xml.replace("localhost", self._dbhost)

        self._simps.dp.SpectrumBoolean = self._logical[0]
        self._simps.dp.SpectrumUChar = self._mca2[0]
        self._simps.dp.SpectrumShort = self._mca1[0]
        self._simps.dp.SpectrumUShort = self._mca2[0]
        self._simps.dp.SpectrumLong = self._mca1[0]
        self._simps.dp.SpectrumULong = self._mca2[0]
        self._simps.dp.SpectrumLong64 = self._mca1[0]
        self._simps.dp.SpectrumULong64 = self._mca2[0]
        self._simps.dp.SpectrumFloat = self._fmca1[0]
        self._simps.dp.SpectrumDouble = self._fmca1[0]
        self._simps.dp.SpectrumString = self._dates[0]

        decoder = '"decoders":{"MUINT32":' + \
                  '"nxswriter.DecoderPool.UINT32decoder"}'
        tdw = self.openWriter(fname, xml, json='{ ' + decoder + ' }')

        dp = tango.DeviceProxy("stestp09/testss/s1r228")
        self.assertTrue(ProxyHelper.wait(dp, 10000))

        steps = min(len(self._logical), len(
            self._mca1), len(self._mca2), len(self._dates))
        for i in range(steps):
            self._simps.dp.SpectrumBoolean = self._logical[i]
            self._simps.dp.SpectrumUChar = self._mca2[i]
            self._simps.dp.SpectrumShort = self._mca1[i]
            self._simps.dp.SpectrumUShort = self._mca2[i]
            self._simps.dp.SpectrumLong = self._mca1[i]
            self._simps.dp.SpectrumULong = self._mca2[i]
            self._simps.dp.SpectrumLong64 = self._mca1[i]
            self._simps.dp.SpectrumULong64 = self._mca2[i]
            self._simps.dp.SpectrumFloat = self._fmca1[i]
            self._simps.dp.SpectrumDouble = self._fmca1[i]
            self._simps.dp.SpectrumString = self._dates[i]

            self.record(tdw, '{}')

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 15)
        self._sc.checkSpectrumField(
            det, "SpectrumBoolean", "bool", "NX_BOOLEAN",
            self._logical[:steps])
        self._sc.checkSpectrumField(
            det, "SpectrumUChar", "uint8", "NX_UINT8", self._mca2[:steps],
            grows=2)
        self._sc.checkSpectrumField(
            det, "SpectrumShort", "int16", "NX_INT16", self._mca1[:steps],
            grows=3)
        self._sc.checkSpectrumField(
            det, "SpectrumUShort", "uint16", "NX_UINT16", self._mca2[:steps],
            grows=2)
        self._sc.checkSpectrumField(
            det, "SpectrumLong", "int32", "NX_INT32", self._mca1[:steps])
        self._sc.checkSpectrumField(
            det, "SpectrumULong", "uint32", "NX_UINT32", self._mca2[:steps],
            grows=1)
        self._sc.checkSpectrumField(
            det, "SpectrumLong64", "int64", "NX_INT64", self._mca1[:steps],
            grows=2)
        self._sc.checkSpectrumField(
            det, "SpectrumULong64", "uint64", "NX_UINT64", self._mca2[:steps],
            grows=2)
        self._sc.checkSpectrumField(
            det, "SpectrumFloat", "float32", "NX_FLOAT32", self._fmca1[:steps],
            error=1e-6)
        self._sc.checkSpectrumField(
            det, "SpectrumDouble", "float64", "NX_FLOAT64", self._fmca1[
                :steps],
            grows=1, error=1e-14)
        self._sc.checkSpectrumField(
            det, "SpectrumDouble", "float64", "NX_FLOAT64", self._fmca1[
                :steps],
            error=1e-14)

        self._sc.checkSpectrumField(
            det, "SpectrumString", "string", "NX_CHAR", self._dates[:steps])
        # writing encoded attributes not supported for tango 7.2.3

        self._sc.checkSpectrumField(
            det, "SpectrumEncoded", "int32", "NX_INT32", self._mca2[:steps])

        self._sc.checkSpectrumField(
            det, "SpectrumEncoded_MUINT32", "int32", "NX_INT32",
            self._mca2[:steps])

        self._sc.checkSingleSpectrumField(
            det, "InitSpectrumLong64", "int64", "NX_INT64", self._mca1[0])

        self._sc.checkSingleSpectrumField(
            det, "FinalSpectrumFloat", "float32", "NX_FLOAT32", self._fmca1[
                steps - 1],
            error=1.0e-06)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoImage(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        if not PYTG_BUG_213:
            xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">


       <field units="" type="NX_BOOLEAN" name="ImageBoolean">
          <strategy mode="STEP"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageBoolean"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT8" name="ImageUChar">
          <strategy mode="STEP"   compression="true"  grows="2" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUChar"/>
          </datasource>
        </field>

       <field units="" type="NX_INT16" name="ImageShort">
          <strategy mode="STEP"    compression="true"  grows="3"
 shuffle="false"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageShort"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT16" name="ImageUShort">
          <strategy mode="STEP"   grows="1"   />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUShort"/>
          </datasource>
        </field>

       <field units="" type="NX_INT32" name="ImageLong">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT32" name="ImageULong">
          <strategy mode="STEP"  grows="3"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong"/>
          </datasource>
        </field>


       <field units="" type="NX_INT64" name="ImageLong64">
          <strategy mode="STEP"  compression="true"  grows="1"
 shuffle="false"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT64" name="ImageULong64">
          <strategy mode="STEP"  compression="true"  grows="2"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="ImageFloat">
          <strategy mode="STEP"  compression="true"  grows="3"
shuffle="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT64" name="ImageDouble">
          <strategy mode="STEP"  compression="true"  grows="1"   />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageDouble"/>
          </datasource>
        </field>

       <field units="" type="NX_CHAR" name="ImageString">
          <strategy mode="STEP"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageString"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT8" name="ImageEncoded">
          <strategy mode="STEP"  compression="true"  shuffle="false"
 grows="3"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
            <record name="ImageEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="LIMA_VIDEO_IMAGE"/>
          </datasource>
        </field>


        <field units="" type="NX_UINT8" name="ImageEncoded_MLIMA">
          <strategy mode="STEP"  compression="true"  shuffle="false"
 grows="3"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
            <record name="ImageEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="MLIMA"/>
          </datasource>
        </field>



       <field units="" type="NX_UINT64" name="InitImageULong64">
          <strategy mode="INIT" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="FinalImageFloat">
          <strategy mode="FINAL"  compression="true"  shuffle="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>



      </group>
    </group>
  </group>
</definition>
"""
        else:
            xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">


       <field units="" type="NX_BOOLEAN" name="ImageBoolean">
          <strategy mode="STEP"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageBoolean"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT8" name="ImageUChar">
          <strategy mode="STEP"   compression="true"  grows="2" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUChar"/>
          </datasource>
        </field>

       <field units="" type="NX_INT16" name="ImageShort">
          <strategy mode="STEP"    compression="true"  grows="3"
 shuffle="false"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageShort"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT16" name="ImageUShort">
          <strategy mode="STEP"   grows="1"   />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUShort"/>
          </datasource>
        </field>

       <field units="" type="NX_INT32" name="ImageLong">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT32" name="ImageULong">
          <strategy mode="STEP"  grows="3"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong"/>
          </datasource>
        </field>


       <field units="" type="NX_INT64" name="ImageLong64">
          <strategy mode="STEP"  compression="true"  grows="1"
 shuffle="false"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT64" name="ImageULong64">
          <strategy mode="STEP"  compression="true"  grows="2"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="ImageFloat">
          <strategy mode="STEP"  compression="true"  grows="3"
 shuffle="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT64" name="ImageDouble">
          <strategy mode="STEP"  compression="true"  grows="1"   />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageDouble"/>
          </datasource>
        </field>

       <field units="" type="NX_CHAR" name="ImageString">
          <strategy mode="STEP"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageString"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT64" name="InitImageULong64">
          <strategy mode="INIT" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="FinalImageFloat">
          <strategy mode="FINAL"  compression="true"  shuffle="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>



      </group>
    </group>
  </group>
</definition>
"""

        xml = xml.replace("localhost", self._dbhost)

        self._simps.dp.ImageBoolean = self._logical2[0]
        self._simps.dp.ImageUChar = self._pco1[0]
        self._simps.dp.ImageShort = self._pco1[0]
        self._simps.dp.ImageUShort = self._pco1[0]
        self._simps.dp.ImageLong = self._pco1[0]
        self._simps.dp.ImageULong = self._pco1[0]
        self._simps.dp.ImageLong64 = self._pco1[0]
        self._simps.dp.ImageULong64 = self._pco1[0]
        self._simps.dp.ImageFloat = self._fpco1[0]
        self._simps.dp.ImageDouble = self._fpco1[0]
        self._simps.dp.ImageString = self._dates2[0]

#        print self._fmca1[0]

        decoder = '"decoders":{"MLIMA":"nxswriter.DecoderPool.VDEOdecoder"}'
        tdw = self.openWriter(fname, xml, json='{ ' + decoder + ' }')

        dp = tango.DeviceProxy("stestp09/testss/s1r228")
        self.assertTrue(ProxyHelper.wait(dp, 10000))

        steps = min(len(self._pco1), len(self._logical2), len(self._fpco1))
        for i in range(steps):
            self._simps.dp.ImageBoolean = self._logical2[i]
            self._simps.dp.ImageUChar = self._pco1[i]
            self._simps.dp.ImageShort = self._pco1[i]
            self._simps.dp.ImageUShort = self._pco1[i]
            self._simps.dp.ImageLong = self._pco1[i]
            self._simps.dp.ImageULong = self._pco1[i]
            self._simps.dp.ImageLong64 = self._pco1[i]
            self._simps.dp.ImageULong64 = self._pco1[i]
            self._simps.dp.ImageFloat = self._fpco1[i]
            self._simps.dp.ImageDouble = self._fpco1[i]
            self._simps.dp.ImageString = self._dates2[i]

            self.record(tdw, '{}')
            pass
        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 15 if not PYTG_BUG_213 else 13)
        self._sc.checkImageField(
            det, "ImageBoolean", "bool", "NX_BOOLEAN", self._logical2[:steps])
        self._sc.checkImageField(
            det, "ImageUChar", "uint8", "NX_UINT8", self._pco1[:steps],
            grows=2)
        self._sc.checkImageField(
            det, "ImageShort", "int16", "NX_INT16", self._pco1[:steps],
            grows=3)
        self._sc.checkImageField(
            det, "ImageUShort", "uint16", "NX_UINT16", self._pco1[:steps],
            grows=1)
        self._sc.checkImageField(
            det, "ImageLong", "int32", "NX_INT32", self._pco1[:steps],
            grows=2)
        self._sc.checkImageField(
            det, "ImageULong", "uint32", "NX_UINT32", self._pco1[:steps],
            grows=3)
        self._sc.checkImageField(
            det, "ImageLong64", "int64", "NX_INT64", self._pco1[:steps],
            grows=1)
        self._sc.checkImageField(
            det, "ImageULong64", "uint64", "NX_UINT64", self._pco1[:steps],
            grows=2)
        self._sc.checkImageField(
            det, "ImageFloat", "float32", "NX_FLOAT32", self._fpco1[:steps],
            grows=3, error=1.0e-6)
        self._sc.checkImageField(
            det, "ImageDouble", "float64", "NX_FLOAT64", self._fpco1[:steps],
            grows=1, error=1.0e-14)
        self._sc.checkImageField(
            det, "ImageString", "string", "NX_CHAR", self._dates2[:steps])
        if not PYTG_BUG_213:
            self._sc.checkImageField(
                det, "ImageEncoded", "uint8", "NX_UINT8", self._pco1[:steps],
                grows=3)

        if not PYTG_BUG_213:
            self._sc.checkImageField(
                det, "ImageEncoded_MLIMA", "uint8", "NX_UINT8",
                self._pco1[:steps],
                grows=3)

        self._sc.checkSingleImageField(
            det, "InitImageULong64", "uint64", "NX_UINT64", self._pco1[0])
        self._sc.checkSingleImageField(
            det, "FinalImageFloat", "float32", "NX_FLOAT32",
            self._fpco1[steps - 1], error=1.0e-6)
        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoImage_canfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        if not PYTG_BUG_213:
            xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">


       <field units="" type="NX_BOOLEAN" name="ImageBoolean">
          <strategy mode="STEP"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageBoolean"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT8" name="ImageUChar">
          <strategy mode="STEP"   compression="true"  grows="2"
  canfail="true"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUChar"/>
          </datasource>
        </field>

       <field units="" type="NX_INT16" name="ImageShort">
          <strategy mode="STEP"    compression="true"  grows="3"
 shuffle="false" canfail="true"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageShort"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT16" name="ImageUShort">
          <strategy mode="STEP"   grows="1"  canfail="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUShort"/>
          </datasource>
        </field>

       <field units="" type="NX_INT32" name="ImageLong">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="true"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT32" name="ImageULong">
          <strategy mode="STEP"  grows="3"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong"/>
          </datasource>
        </field>


       <field units="" type="NX_INT64" name="ImageLong64">
          <strategy mode="STEP"  compression="true"  grows="1"
 shuffle="false"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT64" name="ImageULong64">
          <strategy mode="STEP"  compression="true"  grows="2"
 canfail="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="ImageFloat">
          <strategy mode="STEP"  compression="true"  grows="3"
 shuffle="true"  canfail="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT64" name="ImageDouble">
          <strategy mode="STEP"  compression="true"  grows="1"
 canfail="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageDouble"/>
          </datasource>
        </field>

       <field units="" type="NX_CHAR" name="ImageString">
          <strategy mode="STEP"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageString"/>
          </datasource>
        </field>

        <field units="" type="NX_UINT8" name="ImageEncoded">
          <strategy mode="STEP"  compression="true"  shuffle="false"
 grows="3"  canfail="true"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
            <record name="ImageEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="LIMA_VIDEO_IMAGE"/>
          </datasource>
        </field>


        <field units="" type="NX_UINT8" name="ImageEncoded_MLIMA">
          <strategy mode="STEP"  compression="true"  shuffle="false"
 grows="3"  canfail="true"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
            <record name="ImageEncoded"/>
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" encoding="MLIMA"/>
          </datasource>
        </field>



       <field units="" type="NX_UINT64" name="InitImageULong64">
          <strategy mode="INIT"  canfail="true" />
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <datasource type="TANGO">
           <device member="attribute"
name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64_canfail"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="FinalImageFloat">
          <strategy mode="FINAL"  compression="true"  shuffle="true"
  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>



      </group>
    </group>
  </group>
</definition>
"""
        else:
            xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">


       <field units="" type="NX_BOOLEAN" name="ImageBoolean">
          <strategy mode="STEP"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageBoolean"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT8" name="ImageUChar">
          <strategy mode="STEP"   compression="true"  grows="2"
 canfail="true"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUChar"/>
          </datasource>
        </field>

       <field units="" type="NX_INT16" name="ImageShort">
          <strategy mode="STEP"    compression="true"  grows="3"
 shuffle="false" canfail="true"/>
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageShort"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT16" name="ImageUShort">
          <strategy mode="STEP"   grows="1"  canfail="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageUShort"/>
          </datasource>
        </field>

       <field units="" type="NX_INT32" name="ImageLong">
          <strategy mode="STEP"  compression="true"  grows="2"
 shuffle="true"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT32" name="ImageULong">
          <strategy mode="STEP"  grows="3"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong"/>
          </datasource>
        </field>


       <field units="" type="NX_INT64" name="ImageLong64">
          <strategy mode="STEP"  compression="true"  grows="1"
 shuffle="false"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT64" name="ImageULong64">
          <strategy mode="STEP"  compression="true"  grows="2"
 canfail="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="ImageFloat">
          <strategy mode="STEP"  compression="true"  grows="3"
 shuffle="true"  canfail="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT64" name="ImageDouble">
          <strategy mode="STEP"  compression="true"  grows="1"
  canfail="true"  />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageDouble"/>
          </datasource>
        </field>

       <field units="" type="NX_CHAR" name="ImageString">
          <strategy mode="STEP"  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageString"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT64" name="InitImageULong64">
          <strategy mode="INIT"  canfail="true" />
          <dimensions rank="2">
            <dim value="10" index="1"/>
            <dim value="8" index="2"/>
          </dimensions>
          <datasource type="TANGO">
           <device member="attribute"
name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageULong64_canfail"/>
          </datasource>
        </field>



       <field units="" type="NX_FLOAT32" name="FinalImageFloat">
          <strategy mode="FINAL"  compression="true"  shuffle="true"
  canfail="true" />
          <dimensions rank="2" />
          <datasource type="TANGO">
           <device member="attribute"
 name="stestp09/testss/s1r228" port="10000" />
           <record name="ImageFloat"/>
          </datasource>
        </field>



      </group>
    </group>
  </group>
</definition>
"""

        xml = xml.replace("localhost", self._dbhost)

        self._simps.dp.ImageBoolean = self._logical2[0]
        self._simps.dp.ImageUChar = self._pco1[0]
        self._simps.dp.ImageShort = self._pco1[0]
        self._simps.dp.ImageUShort = self._pco1[0]
        self._simps.dp.ImageLong = self._pco1[0]
        self._simps.dp.ImageULong = self._pco1[0]
        self._simps.dp.ImageLong64 = self._pco1[0]
        self._simps.dp.ImageULong64 = self._pco1[0]
        self._simps.dp.ImageFloat = self._fpco1[0]
        self._simps.dp.ImageDouble = self._fpco1[0]
        self._simps.dp.ImageString = self._dates2[0]

#        print self._fmca1[0]

        decoder = '"decoders":{"MLIMA":"nxswriter.DecoderPool.VDEOdecoder"}'
        tdw = self.openWriter(fname, xml, json='{ ' + decoder + ' }')

        dp = tango.DeviceProxy("stestp09/testss/s1r228")
        self.assertTrue(ProxyHelper.wait(dp, 10000))

        steps = min(len(self._pco1), len(self._logical2), len(self._fpco1))
        self._simps.tearDown()
        for i in range(steps):
            if not i % 2:
                self._simps.setUp()
                self._simps.dp.ImageBoolean = self._logical2[i]
                self._simps.dp.ImageUChar = self._pco1[i]
                self._simps.dp.ImageShort = self._pco1[i]
                self._simps.dp.ImageUShort = self._pco1[i]
                self._simps.dp.ImageLong = self._pco1[i]
                self._simps.dp.ImageULong = self._pco1[i]
                self._simps.dp.ImageLong64 = self._pco1[i]
                self._simps.dp.ImageULong64 = self._pco1[i]
                self._simps.dp.ImageFloat = self._fpco1[i]
                self._simps.dp.ImageDouble = self._fpco1[i]
                self._simps.dp.ImageString = self._dates2[i]
            else:
                self._simps.tearDown()

            self.record(tdw, '{}')

        self._simps.tearDown()
        self.closeWriter(tdw)
        self._simps.setUp()

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 15 if not PYTG_BUG_213 else 13)
        self._sc.checkImageField(
            det, "ImageBoolean", "bool", "NX_BOOLEAN",
            [(self._logical2[i] if not i % 2
              else [[False] *
                    len(self._logical2[i][0])] * len(self._logical2[i]))
             for i in range(steps)],
            attrs={
                "type": "NX_BOOLEAN", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkImageField(
            det, "ImageUChar", "uint8", "NX_UINT8",
            [(self._pco1[i] if not i % 2 else
              [[numpy.iinfo(getattr(numpy, 'uint8')).max] *
               len(self._pco1[i][0])] * len(self._pco1[i]))
             for i in range(steps)],
            attrs={"type": "NX_UINT8", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=2)

        self._sc.checkImageField(
            det, "ImageShort", "int16", "NX_INT16",
            [(self._pco1[i] if not i % 2 else
              [[numpy.iinfo(getattr(numpy, 'int16')).max] *
               len(self._pco1[i][0])] * len(self._pco1[i]))
             for i in range(steps)],
            attrs={"type": "NX_INT16", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=3)
        self._sc.checkImageField(
            det, "ImageUShort", "uint16", "NX_UINT16",
            [(self._pco1[i] if not i % 2 else
              [[numpy.iinfo(getattr(numpy, 'uint16')).max] *
               len(self._pco1[i][0])] * len(self._pco1[i]))
             for i in range(steps)],
            attrs={"type": "NX_UINT16", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=1)

        self._sc.checkImageField(
            det, "ImageLong", "int32", "NX_INT32",
            [(self._pco1[i] if not i % 2 else
              [[numpy.iinfo(getattr(numpy, 'int32')).max] *
               len(self._pco1[i][0])] * len(self._pco1[i]))
             for i in range(steps)],
            attrs={"type": "NX_INT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=2)
        self._sc.checkImageField(
            det, "ImageULong", "uint32", "NX_UINT32",
            [(self._pco1[i] if not i % 2 else
              [[numpy.iinfo(getattr(numpy, 'uint32')).max] *
               len(self._pco1[i][0])] * len(self._pco1[i]))
             for i in range(steps)],
            attrs={"type": "NX_UINT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=3)

        self._sc.checkImageField(
            det, "ImageLong64", "int64", "NX_INT64",
            [(self._pco1[i] if not i % 2 else
              [[numpy.iinfo(getattr(numpy, 'int64')).max] *
               len(self._pco1[i][0])] * len(self._pco1[i]))
             for i in range(steps)],
            attrs={"type": "NX_INT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=1)
        self._sc.checkImageField(
            det, "ImageULong64", "uint64", "NX_UINT64",
            [(self._pco1[i] if not i % 2 else
              [[numpy.iinfo(getattr(numpy, 'uint64')).max] *
               len(self._pco1[i][0])] * len(self._pco1[i]))
             for i in range(steps)],
            attrs={"type": "NX_UINT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None},
            grows=2)

        self._sc.checkImageField(
            det, "ImageFloat", "float32", "NX_FLOAT32",
            [(self._fpco1[i] if not i % 2 else
              [[numpy.finfo(getattr(numpy, 'float32')).max] *
               len(self._fpco1[i][0])] * len(self._fpco1[i]))
             for i in range(steps)],
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            grows=3, error=1.0e-6)
        self._sc.checkImageField(
            det, "ImageDouble", "float64", "NX_FLOAT64",
            [(self._fpco1[i] if not i % 2 else
              [[numpy.finfo(getattr(numpy, 'float64')).max] *
               len(self._fpco1[i][0])] * len(self._fpco1[i]))
             for i in range(steps)],
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            grows=1, error=1.0e-14)

        self._sc.checkImageField(
            det, "ImageString", "string", "NX_CHAR",
            [(self._dates2[i] if not i % 2 else
              [[''] * len(self._dates2[i][0])] * len(self._dates2[i]))
             for i in range(steps)],
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        if not PYTG_BUG_213:
            self._sc.checkImageField(
                det, "ImageEncoded", "uint8", "NX_UINT8",
                [(self._pco1[i] if not i % 2 else
                  [[numpy.iinfo(getattr(numpy, 'uint8')).max] *
                   len(self._pco1[i][0])] * len(self._pco1[i]))
                 for i in range(steps)],
                attrs={
                    "type": "NX_UINT8", "units": "", "nexdatas_source": None,
                    "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                    "nexdatas_canfail_error": None},
                grows=3)

            self._sc.checkImageField(
                det, "ImageEncoded_MLIMA", "uint8", "NX_UINT8",
                [(self._pco1[i] if not i % 2 else
                  [[numpy.iinfo(getattr(numpy, 'uint8')).max] *
                   len(self._pco1[i][0])] * len(self._pco1[i]))
                 for i in range(steps)],
                attrs={
                    "type": "NX_UINT8", "units": "", "nexdatas_source": None,
                    "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                    "nexdatas_canfail_error": None},
                grows=3)

        self._sc.checkSingleImageField(
            det, "InitImageULong64", "uint64", "NX_UINT64",
            [[numpy.iinfo(getattr(numpy, 'uint64')).max] * len(
                self._pco1[0][0])] * len(self._pco1[0]),
            attrs={"type": "NX_UINT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleImageField(
            det, "FinalImageFloat", "float32", "NX_FLOAT32",
            [[numpy.finfo(getattr(numpy, 'float32')).max] * len(
                self._fpco1[0][0])] * len(self._fpco1[0]),
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        f.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
