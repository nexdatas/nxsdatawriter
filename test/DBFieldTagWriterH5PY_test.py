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
# \file DBFieldTagWriterTest.py
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

from nxswriter.TangoDataWriter import TangoDataWriter

try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker

from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter

try:
    import MySQLdb
except Exception:
    import pymysql as MySQLdb
    MySQLdb.install_as_MySQLdb()


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

if sys.version_info > (3,):
    long = int


# test fixture
class DBFieldTagWriterH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        try:
            # random seed
            self.seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.seed = long(time.time() * 256)  # use fractional seconds

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
        self._mydb = None

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self._largs = None

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        try:
            args = {}
            args["db"] = 'tango'
            # args["host"] = 'localhost'
            args["read_default_file"] = '/etc/my.cnf'
            self._mydb = MySQLdb.connect(**args)
        except Exception:
            from os.path import expanduser
            home = expanduser("~")
            args2 = {
                # 'host': u'localhost',
                'db': u'tango',
                'read_default_file': u'%s/.my.cnf' % home,
                'use_unicode': True}
            self._mydb = MySQLdb.connect(**args2)
            self._largs = args2
            print("ARGS: %s" % str(args2))

        print("SEED = %s" % self.seed)
        print("CHECKER SEED = %s" % self._sc.seed)

    def setmycnf(self, xml):
        if not self._largs or 'read_default_file' not in self._largs.keys():
            return str(xml.replace("$mycnf", ""))
        else:
            return str(xml.replace(
                "$mycnf",
                'mycnf="%s"' % self._largs['read_default_file']))

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")
        self._mydb.close()

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

    # opens writer
    # \param fname file name
    # \param xml XML settings
    # \param json JSON Record with client settings
    # \returns Tango Data Writer instance
    def openWriter(self, fname, xml, json=None):
        tdw = TangoDataWriter()
        tdw.fileName = fname
        tdw.numberOfThreads = 1
        tdw.writer = "h5py"

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

    # performs one record step
    def record(self, tdw, string):
        tdw.record(string)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbScalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

        <field units="m" name="pid_scalar_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"
$mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field units="m" name="pid_scalar2_string" type="NX_CHAR">
          <dimensions rank="1" />
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar3_string" type="NX_CHAR">
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field units="m" name="pid_scalar4_string" type="NX_CHAR">
          <dimensions rank="0" />
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field  units="m" name="pid_scalar_uint" type="NX_UINT">
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>



        <field  units="m" name="pid_scalar_int64" type="NX_INT64">
          <strategy mode="STEP"/>
          <dimensions rank="0" />
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar_float64" type="NX_FLOAT64">
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar_float32" type="NX_FLOAT32">
          <dimensions rank="0" />
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid2_image_string" type="NX_CHAR" units="m" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="pid3_image_string" type="NX_CHAR" units="m" >
          <dimensions rank="2" />
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="init_pid_scalar_int32" type="NX_INT32">
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="init_pid_scalar_string" type="NX_CHAR">
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="final_pid_scalar_float32" type="NX_FLOAT32">
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="final_pid_scalar_float64" type="NX_FLOAT64">
          <dimensions rank="0" />
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="final_pid_scalar_string" type="NX_CHAR" units="m" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"

 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="final_pid2_scalar_string" type="NX_CHAR" units="m" >
          <dimensions rank="1"/>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>




        <field name="final_pid3_scalar_string" type="NX_CHAR" units="m" >
          <dimensions rank="0"/>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        xml = self.setmycnf(xml)

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        scalar = str(cursor.fetchone()[0])
        cursor.close()

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 17)
        self._sc.checkSpectrumField(
            det, "pid_scalar_string", "string", "NX_CHAR", [[scalar]] * 3,
            attrs={"type": "NX_CHAR", "units": "m",
                   "nexdatas_source": None, "nexdatas_strategy": "STEP"})
        self._sc.checkSpectrumField(
            det, "pid_scalar2_string", "string", "NX_CHAR", [[scalar]] * 3,
            attrs={"type": "NX_CHAR", "units": "m",
                   "nexdatas_source": None, "nexdatas_strategy": "STEP"})
        self._sc.checkScalarField(
            det, "pid_scalar3_string", "string", "NX_CHAR", [scalar] * 3)
        self._sc.checkScalarField(
            det, "pid_scalar4_string", "string", "NX_CHAR", [scalar] * 3)
        self._sc.checkScalarField(
            det, "pid_scalar_uint", "uint64", "NX_UINT", [int(scalar)] * 3)
        self._sc.checkScalarField(
            det, "pid_scalar_int64", "int64", "NX_INT64", [int(scalar)] * 3)
        self._sc.checkScalarField(
            det, "pid_scalar_float64", "float64", "NX_FLOAT64", [
                float(scalar)] * 3, error=1e-14)
        self._sc.checkScalarField(
            det, "pid_scalar_float32", "float32", "NX_FLOAT32", [
                float(scalar)] * 3,
            error=1e-5)
        self._sc.checkImageField(
            det, "pid2_image_string", "string", "NX_CHAR",
            [[[str(scalar)]]] * 3,
            attrs={"type": "NX_CHAR", "units": "m",
                   "nexdatas_source": None, "nexdatas_strategy": "STEP"})
        self._sc.checkImageField(
            det, "pid3_image_string", "string", "NX_CHAR",
            [[[str(scalar)]]] * 3,
            attrs={"type": "NX_CHAR", "units": "m",
                   "nexdatas_source": None, "nexdatas_strategy": "STEP"})

        self._sc.checkSingleScalarField(
            det, "init_pid_scalar_int32", "int32", "NX_INT32", int(scalar))
        self._sc.checkSingleStringScalarField(
            det, "init_pid_scalar_string", "string", "NX_CHAR", scalar)
        self._sc.checkSingleScalarField(
            det, "final_pid_scalar_float32", "float32", "NX_FLOAT32",
            float(scalar), error=1e-6)
        self._sc.checkSingleScalarField(
            det, "final_pid_scalar_float64", "float64", "NX_FLOAT64",
            float(scalar), error=1e-14)
        self._sc.checkSingleImageField(
            det, "final_pid_scalar_string", "string", "NX_CHAR",
            [[str(scalar)]],
            attrs={"type": "NX_CHAR", "units": "m",
                   "nexdatas_source": None, "nexdatas_strategy": "FINAL"})
        self._sc.checkSingleScalarField(
            det, "final_pid2_scalar_string", "string", "NX_CHAR",
            str(scalar))
        self._sc.checkSingleStringScalarField(
            det, "final_pid3_scalar_string", "string", "NX_CHAR",
            str(scalar))

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbScalar_canfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

        <field units="m" name="pid_scalar_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field units="m" name="pid_scalar2_string" type="NX_CHAR">
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar3_string" type="NX_CHAR">
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field units="m" name="pid_scalar4_string" type="NX_CHAR">
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field  units="m" name="pid_scalar_uint" type="NX_UINT">
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>



        <field  units="m" name="pid_scalar_int64" type="NX_INT64">
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar_float64" type="NX_FLOAT64">
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar_float32" type="NX_FLOAT32">
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid2_image_string" type="NX_CHAR" units="m" >
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="pid3_image_string" type="NX_CHAR" units="m" >
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="init_pid_scalar_int32" type="NX_INT32">
          <strategy mode="INIT" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="init_pid_scalar_string" type="NX_CHAR">
          <strategy mode="INIT" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="final_pid_scalar_float32" type="NX_FLOAT32">
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="final_pid_scalar_float64" type="NX_FLOAT64">
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="final_pid_scalar_string" type="NX_CHAR" units="m" >
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="final_pid2_scalar_string" type="NX_CHAR" units="m" >
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>




        <field name="final_pid3_scalar_string" type="NX_CHAR" units="m" >
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        # scalar =
        str(cursor.fetchone()[0])
        cursor.close()

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 17)
        self._sc.checkSpectrumField(
            det, "pid_scalar_string", "string", "NX_CHAR", [['']] * 3,
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "pid_scalar2_string", "string", "NX_CHAR", [''] * 3,
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "pid_scalar3_string", "string", "NX_CHAR", [''] * 3,
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "pid_scalar4_string", "string", "NX_CHAR", [''] * 3,
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "pid_scalar_uint", "uint64", "NX_UINT", [
                numpy.iinfo(getattr(numpy, 'uint64')).max] * 3,
            attrs={"type": "NX_UINT", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "pid_scalar_int64", "int64", "NX_INT64", [
                numpy.iinfo(getattr(numpy, 'int64')).max] * 3,
            attrs={"type": "NX_INT64", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "pid_scalar_float64", "float64", "NX_FLOAT64", [
                numpy.finfo(getattr(numpy, 'float64')).max] * 3,
            attrs={
                "type": "NX_FLOAT64", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1e-14)
        self._sc.checkScalarField(
            det, "pid_scalar_float32", "float32", "NX_FLOAT32", [
                numpy.finfo(getattr(numpy, 'float32')).max] * 3,
            attrs={
                "type": "NX_FLOAT32", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1e-5)
        self._sc.checkScalarField(
            det, "pid2_image_string", "string", "NX_CHAR", [''] * 3,
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkScalarField(
            det, "pid3_image_string", "string", "NX_CHAR", [''] * 3,
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

#
        self._sc.checkSingleScalarField(
            det, "init_pid_scalar_int32", "int32", "NX_INT32", numpy.iinfo(
                getattr(numpy, 'int32')).max,
            attrs={"type": "NX_INT32", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleStringScalarField(
            det, "init_pid_scalar_string", "string", "NX_CHAR", '',
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleScalarField(
            det, "final_pid_scalar_float32", "float32", "NX_FLOAT32",
            numpy.finfo(
                getattr(numpy, 'float32')).max,
            attrs={
                "type": "NX_FLOAT32", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1e-6)
        self._sc.checkSingleScalarField(
            det, "final_pid_scalar_float64", "float64", "NX_FLOAT64",
            numpy.finfo(
                getattr(numpy, 'float64')).max,
            attrs={
                "type": "NX_FLOAT64", "units": "m", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None},
            error=1e-14)
        self._sc.checkSingleStringScalarField(
            det, "final_pid_scalar_string", "string", "NX_CHAR", '',
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleStringScalarField(
            det, "final_pid2_scalar_string", "string", "NX_CHAR", '',
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleStringScalarField(
            det, "final_pid3_scalar_string", "string", "NX_CHAR", '',
            attrs={"type": "NX_CHAR", "units": "m", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbSpectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">



        <field units="" name="pid_spectrum_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field units="" name="pid_spectrum_int32" type="NX_UINT32">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="STEP" grows="2"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field units="" name="pid_spectrum_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="STEP" comporession="true" rate="4" shuffle="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field  units="" name="pid_scalar_int32" type="NX_INT32">
          <dimensions rank="1" />
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>





        <field  units="" name="pid_scalar_int64" type="NX_INT64">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="pid_scalar_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="name_spectrum_string" type="NX_CHAR" units="" >
          <dimensions rank="2" />
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT name FROM device limit 6
            </query>
          </datasource>
        </field>





        <field  units="" name="init_pid_spectrum_int32" type="NX_INT32">
          <dimensions rank="1" />
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field  units="" name="final_pid_spectrum_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field  units="" name="final_pid_scalar_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="init_pid_spectrum_string" type="NX_CHAR">
          <dimensions rank="1" />
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="final_pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="final_pid_spectrum_string" type="NX_CHAR" units="" >
          <dimensions rank="1" />
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>






      </group>
    </group>
  </group>
</definition>
"""
        xml = self.setmycnf(xml)

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        scalar = str(cursor.fetchone()[0])
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 6")
        spectrum = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name FROM device limit 6")
        name = cursor.fetchall()
        cursor.close()

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 13)
        self._sc.checkSpectrumField(
            det, "pid_spectrum_string", "string", "NX_CHAR",
            [[str(sub[0]) for sub in spectrum]] * 3)
        self._sc.checkSpectrumField(
            det, "pid_spectrum_int32", "uint32", "NX_UINT32",
            [[sub[0] for sub in spectrum]] * 3, grows=2)
        self._sc.checkSpectrumField(
            det, "pid_spectrum_float64", "float64", "NX_FLOAT64",
            [[float(sub[0]) for sub in spectrum]] * 3)
        self._sc.checkSpectrumField(
            det, "pid_scalar_int64", "int64", "NX_INT64",
            [[int(scalar)]] * 3)
        self._sc.checkSpectrumField(
            det, "pid_scalar_float64", "float64", "NX_FLOAT64",
            [[float(scalar)]] * 3)
        self._sc.checkImageField(
            det, "name_spectrum_string", "string", "NX_CHAR",
            [[[str(sub[0])] for sub in name]] * 3)
        self._sc.checkSingleSpectrumField(
            det, "init_pid_spectrum_int32", "int32", "NX_INT32",
            [sub[0] for sub in spectrum])
        self._sc.checkSingleSpectrumField(
            det, "final_pid_spectrum_float64", "float64", "NX_FLOAT64",
            [sub[0] for sub in spectrum])

        self._sc.checkSingleSpectrumField(
            det, "init_pid_spectrum_string", "string", "NX_CHAR",
            [str(sub[0]) for sub in spectrum])
        self._sc.checkSingleSpectrumField(
            det, "final_pid_scalar_string", "string", "NX_CHAR",
            [scalar])
        self._sc.checkSingleImageField(
            det, "final_pid_image_string", "string", "NX_CHAR",
            [[str(sub[0])] for sub in spectrum])
        self._sc.checkSingleSpectrumField(
            det, "final_pid_spectrum_string", "string", "NX_CHAR",
            [str(sub[0]) for sub in spectrum])

        self._sc.checkSpectrumField(
            det, "pid_scalar_int32", "int32", "NX_INT32",
            [[int(scalar)]] * 3)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbSpectrum_canfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">



        <field units="" name="pid_spectrum_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field units="" name="pid_spectrum_int32" type="NX_UINT32">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="STEP" grows="2" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field units="" name="pid_spectrum_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="STEP" comporession="true" rate="4" shuffle="true"
 canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field  units="" name="pid_scalar_int32" type="NX_INT32">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>





        <field  units="" name="pid_scalar_int64" type="NX_INT64">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="pid_scalar_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="name_spectrum_string" type="NX_CHAR" units="" >
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT pname FROM device limit 6
            </query>
          </datasource>
        </field>





        <field  units="" name="init_pid_spectrum_int32" type="NX_INT32">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="INIT" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field  units="" name="final_pid_spectrum_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field  units="" name="final_pid_scalar_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="init_pid_spectrum_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="INIT" canfail="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="final_pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="final_pid_spectrum_string" type="NX_CHAR" units="" >
          <dimensions rank="1">
            <dim index="1" value="6"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>






      </group>
    </group>
  </group>
</definition>
"""

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        # scalar =
        str(cursor.fetchone()[0])
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 6")
        spectrum = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name FROM device limit 6")
        name = cursor.fetchall()
        cursor.close()

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 13)
        self._sc.checkSpectrumField(
            det, "pid_spectrum_string", "string", "NX_CHAR",
            [[''] * len(spectrum)] * 3,
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSpectrumField(
            det, "pid_spectrum_int32", "uint32", "NX_UINT32",
            [[numpy.iinfo(getattr(numpy, 'uint32')).max] * len(spectrum)] * 3,
            grows=2,
            attrs={"type": "NX_UINT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSpectrumField(
            det, "pid_spectrum_float64", "float64", "NX_FLOAT64",
            [[numpy.finfo(getattr(numpy, 'float64')).max] * len(
                spectrum)] * 3,
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSpectrumField(
            det, "pid_scalar_int64", "int64", "NX_INT64",
            [[numpy.iinfo(
                getattr(numpy, 'int64')).max]] * 3,
            attrs={"type": "NX_INT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSpectrumField(
            det, "pid_scalar_float64", "float64", "NX_FLOAT64",
            [[numpy.finfo(
                getattr(numpy, 'float64')).max]] * 3,
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSpectrumField(
            det, "name_spectrum_string", "string", "NX_CHAR",
            [[''] * len(name)] * 3,
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleSpectrumField(
            det, "init_pid_spectrum_int32", "int32", "NX_INT32",
            [numpy.iinfo(getattr(numpy, 'int32')).max] * len(
                spectrum),
            attrs={"type": "NX_INT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleSpectrumField(
            det, "final_pid_spectrum_float64", "float64", "NX_FLOAT64",
            [numpy.finfo(getattr(numpy, 'float64')).max] * len(
                spectrum),
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkSingleSpectrumField(
            det, "init_pid_spectrum_string", "string", "NX_CHAR",
            ['' for sub in spectrum],
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleSpectrumField(
            det, "final_pid_scalar_string", "string", "NX_CHAR",
            [''],
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleSpectrumField(
            det, "final_pid_image_string", "string", "NX_CHAR",
            ['' for sub in spectrum],
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleSpectrumField(
            det, "final_pid_spectrum_string", "string", "NX_CHAR",
            ['' for sub in spectrum],
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkSpectrumField(
            det, "pid_scalar_int32", "int32", "NX_INT32",
            [[numpy.iinfo(
                getattr(numpy, 'int32')).max]] * 3,
            attrs={"type": "NX_INT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbSpectrum_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">




        <field  units="" name="init_pid_scalar_int64" type="NX_INT64">
          <dimensions rank="1"/>
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="final_pid_scalar_float32" type="NX_FLOAT32">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>



      </group>
    </group>
  </group>
</definition>
"""
        xml = self.setmycnf(xml)

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        scalar = str(cursor.fetchone()[0])
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 6")
        # spectrum =
        cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name FROM device limit 6")
        # name =
        cursor.fetchall()
        cursor.close()

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

    # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 2)
        self._sc.checkSingleSpectrumField(
            det, "init_pid_scalar_int64", "int64", "NX_INT64",
            [int(scalar)])
        self._sc.checkSingleSpectrumField(
            det, "final_pid_scalar_float32", "float32", "NX_FLOAT32",
            [float(scalar)])
        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbImage(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

        <field name="name_pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="IMAGE">
              SELECT name, pid FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="name_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="IMAGE">
              SELECT name FROM device limit 6
            </query>
          </datasource>
        </field>



        <field name="pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>




        <field name="pid_image_int" type="NX_INT" units="" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid_image_uint" type="NX_UINT" units="" >
          <dimensions rank="2"/>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="init_pid_spectrum_float64" type="NX_FLOAT64" units="" >
          <dimensions rank="2"/>
          <strategy mode="INIT"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field name="pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="pid_image_int32" type="NX_INT32" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" grows="2" compression="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="pid_image_int64" type="NX_INT64" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" grows="3"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="pid_exported_image_int" type="NX_INT" units="">
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP"  />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="pid_exported_image_uint32" type="NX_UINT32" units="">
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" grows="3" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="final_pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2" />
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid_exported_image_float32" type="NX_FLOAT32" units="">
          <dimensions rank="2" />
          <strategy mode="STEP" compression="true" rate="2" shuffle="false"
 grows="2" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="init_pid_exported_image_int64" type="NX_INT64" units="">
          <dimensions rank="2" />
          <strategy mode="INIT" compression="true" grows="3" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="init_pid_exported_image_string" type="NX_CHAR" units="">
          <dimensions rank="2" />
          <strategy mode="INIT" compression="true" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="pid_spectrum_float32" type="NX_FLOAT32" units="" >
          <dimensions rank="2" />
          <strategy mode="STEP" grows="2"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field name="final_pid_exported_image_float64" type="NX_FLOAT64"
 units="">
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="FINAL" compression="true" rate="2" shuffle="false"
 grows="2" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 6
            </query>
          </datasource>
        </field>



        <field name="final_pid_image_float64" type="NX_FLOAT64" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 6
            </query>
          </datasource>
        </field>




        <field name="init_pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2" >
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="INIT"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"
 $mycnf/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        xml = self.setmycnf(xml)

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name, pid FROM device limit 6")
        name_pid = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name FROM device limit 6")
        name = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 6")
        pid = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid, exported FROM device limit 6")
        pid_exported = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        scalar = str(cursor.fetchone()[0])
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 6")
        spectrum = cursor.fetchall()
        cursor.close()

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 19)
        self._sc.checkImageField(
            det, "name_pid_image_string", "string", "NX_CHAR",
            [[[str(it) for it in sub] for sub in name_pid]] * 3)
        self._sc.checkImageField(
            det, "name_image_string", "string", "NX_CHAR",
            [[[str(it) for it in sub] for sub in name]] * 3)
        self._sc.checkImageField(
            det, "pid_image_string", "string", "NX_CHAR",
            [[[str(it) for it in sub] for sub in pid]] * 3)
        self._sc.checkImageField(
            det, "pid_image_float", "float64", "NX_FLOAT",
            [[[float(it) for it in sub] for sub in pid]] * 3)
        self._sc.checkImageField(
            det, "pid_image_int32", "int32", "NX_INT32",
            [[[int(it) for it in sub] for sub in pid]] * 3, grows=2)
        self._sc.checkImageField(
            det, "pid_image_int", "int64", "NX_INT",
            [[[int(pid[0][0])]]] * 3)
        self._sc.checkImageField(
            det, "pid_image_int64", "int64", "NX_INT64",
            [[[int(it) for it in sub] for sub in pid]] * 3, grows=3)
        self._sc.checkImageField(
            det, "pid_exported_image_int", "int64", "NX_INT",
            [pid_exported] * 3)
        self._sc.checkImageField(
            det, "pid_exported_image_uint32", "uint32", "NX_UINT32",
            [pid_exported] * 3, grows=3)
        self._sc.checkImageField(
            det, "pid_exported_image_float32", "float32", "NX_FLOAT32",
            [pid_exported] * 3, grows=2, error=1e-6)
        self._sc.checkSingleImageField(
            det, "init_pid_exported_image_string", "string", "NX_CHAR",
            [[str(it) for it in sub] for sub in pid_exported])
        self._sc.checkSingleImageField(
            det, "init_pid_exported_image_int64", "int64", "NX_INT64",
            pid_exported, grows=3)
        self._sc.checkSingleImageField(
            det, "final_pid_exported_image_float64", "float64", "NX_FLOAT64",
            pid_exported, grows=2, error=1e-6)
        self._sc.checkSingleImageField(
            det, "final_pid_image_float64", "float64", "NX_FLOAT64",
            [[float(sub[0])] for sub in pid])
        self._sc.checkSingleImageField(
            det, "init_pid_image_float", "float64", "NX_FLOAT",
            [[float(pid[0][0])]])

        self._sc.checkImageField(
            det, "pid_image_uint", "uint64", "NX_UINT",
            [[[int(scalar)]]] * 3)
        self._sc.checkSingleImageField(
            det, "final_pid_image_float", "float64", "NX_FLOAT",
            [[float(scalar)]])

        self._sc.checkSingleImageField(
            det, "init_pid_spectrum_float64", "float64", "NX_FLOAT64",
            [[float(sub[0])] for sub in spectrum])

        self._sc.checkImageField(
            det, "pid_spectrum_float32", "float32", "NX_FLOAT32",
            [[[float(sub[0])] for sub in spectrum]] * 3, grows=2)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbImage_canfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

        <field name="name_pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="IMAGE">
              SELECT pname, pid FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="name_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="IMAGE">
              SELECT pname FROM device limit 6
            </query>
          </datasource>
        </field>



        <field name="pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>




        <field name="pid_image_int" type="NX_INT" units="" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid_image_uint" type="NX_UINT" units="" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="init_pid_spectrum_float64" type="NX_FLOAT64" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="INIT" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field name="pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="pid_image_int32" type="NX_INT32" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" grows="2" compression="true" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="pid_image_int64" type="NX_INT64" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" grows="3" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="pid_exported_image_int" type="NX_INT" units="">
          <dimensions rank="2">
            <dim index="1" value="3"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"  canfail="true" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="IMAGE">
              SELECT ppid, exported FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="pid_exported_image_uint32" type="NX_UINT32" units="">
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" grows="3" canfail="true" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="IMAGE">
              SELECT ppid, exported FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="final_pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid_exported_image_float32" type="NX_FLOAT32" units="">
          <dimensions rank="2">
            <dim index="1" value="2"/>
            <dim index="2" value="6"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="2" shuffle="false"
 grows="2"  canfail="true"/>
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="IMAGE">
              SELECT ppid, exported FROM device limit 6
            </query>
          </datasource>
        </field>

        <field name="init_pid_exported_image_int64" type="NX_INT64" units="">
          <dimensions rank="2">
            <dim index="1" value="2"/>
            <dim index="2" value="6"/>
          </dimensions>
          <strategy mode="INIT" compression="true" grows="3"  canfail="true"/>
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="IMAGE">
              SELECT ppid, exported FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="init_pid_exported_image_string" type="NX_CHAR" units="">
          <dimensions rank="2">
            <dim index="1" value="2"/>
            <dim index="2" value="6"/>
          </dimensions>
          <strategy mode="INIT" compression="true" canfail="true" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="IMAGE">
              SELECT ppid, exported FROM device limit 6
            </query>
          </datasource>
        </field>


        <field name="pid_spectrum_float32" type="NX_FLOAT32" units="" >
          <dimensions rank="2">
            <dim index="1" value="2"/>
            <dim index="2" value="6"/>
          </dimensions>
          <strategy mode="STEP" grows="2" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>



        <field name="final_pid_exported_image_float64" type="NX_FLOAT64"
 units="">
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="FINAL" compression="true" rate="2" shuffle="false"
 grows="2"  canfail="true"/>
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="IMAGE">
              SELECT ppid, exported FROM device limit 6
            </query>
          </datasource>
        </field>



        <field name="final_pid_image_float64" type="NX_FLOAT64" units="" >
          <dimensions rank="2">
            <dim index="1" value="6"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="FINAL" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SPECTRUM">
              SELECT ppid FROM device limit 6
            </query>
          </datasource>
        </field>




        <field name="init_pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2" >
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="INIT" canfail="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL"/>
            <query format="SCALAR">
              SELECT ppid FROM device limit 1
            </query>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name, pid FROM device limit 6")
        name_pid = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name FROM device limit 6")
        name = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 6")
        pid = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid, exported FROM device limit 6")
        # pid_exported =
        cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        # scalar =
        str(cursor.fetchone()[0])
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 6")
        spectrum = cursor.fetchall()
        cursor.close()

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file

        FileWriter.writer = H5PYWriter
        f = FileWriter.open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 19)
        self._sc.checkImageField(
            det, "name_pid_image_string", "string", "NX_CHAR",
            [[['' for it in sub]
              for sub in name_pid]] * 3,
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "name_image_string", "string", "NX_CHAR",
            [[['' for it in sub]
              for sub in name]] * 3,
            attrs={
                "type": "NX_CHAR", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pid_image_string", "string", "NX_CHAR",
            [[['' for it in sub]
              for sub in pid]] * 3,
            attrs={
                "type": "NX_CHAR", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pid_image_float", "float64", "NX_FLOAT",
            [[[numpy.finfo(getattr(numpy, 'float64')).max for it in sub]
              for sub in pid]] * 3,
            attrs={
                "type": "NX_FLOAT", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pid_image_int32", "int32", "NX_INT32",
            [[[numpy.iinfo(getattr(numpy, 'int32')).max for it in sub] for
              sub in pid]] * 3, grows=2,
            attrs={
                "type": "NX_INT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": None, "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pid_image_int", "int64", "NX_INT",
            [[[numpy.iinfo(
                getattr(numpy, 'int64')).max]]] * 3,
            attrs={
                "type": "NX_INT", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pid_image_int64", "int64", "NX_INT64",
            [[[numpy.iinfo(getattr(numpy, 'int64')).max for it in sub]
              for sub in pid]] * 3,
            grows=3,
            attrs={
                "type": "NX_INT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pid_exported_image_int", "int64", "NX_INT",
            [[[numpy.iinfo(getattr(numpy, 'int64')).max]]
             * 3] * 3,
            attrs={"type": "NX_INT", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pid_exported_image_uint32", "uint32", "NX_UINT32",
            [[[numpy.iinfo(getattr(numpy, 'uint32')).max] * 2] * 6] * 3,
            grows=3,
            attrs={"type": "NX_UINT32", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkImageField(
            det, "pid_exported_image_float32", "float32", "NX_FLOAT32",
            [[[numpy.finfo(getattr(numpy, 'float32')).max] * 6] * 2] * 3,
            grows=2, error=1e-6,
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleImageField(
            det, "init_pid_exported_image_string", "string", "NX_CHAR",
            [[''] * 6] * 2,
            attrs={"type": "NX_CHAR", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleImageField(
            det, "init_pid_exported_image_int64", "int64", "NX_INT64",
            [[numpy.iinfo(getattr(numpy, 'int64')).max] * 6] * 2, grows=3,
            attrs={"type": "NX_INT64", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})
        self._sc.checkSingleImageField(
            det, "final_pid_exported_image_float64", "float64", "NX_FLOAT64",
            [[numpy.finfo(getattr(numpy, 'float64')).max] * 2] * 6, grows=2,
            error=1e-6,
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleImageField(
            det, "final_pid_image_float64", "float64", "NX_FLOAT64",
            [[numpy.finfo(
                getattr(numpy, 'float64')).max]] * 6,
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleImageField(
            det, "init_pid_image_float", "float64", "NX_FLOAT",
            [[numpy.finfo(
                getattr(numpy, 'float64')).max]],
            attrs={"type": "NX_FLOAT", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkImageField(
            det, "pid_image_uint", "uint64", "NX_UINT",
            [[[numpy.iinfo(getattr(numpy, 'uint64')).max]]] * 3,
            attrs={
                "type": "NX_UINT", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})
        self._sc.checkSingleImageField(
            det, "final_pid_image_float", "float64", "NX_FLOAT",
            [[numpy.finfo(
                getattr(numpy, 'float64')).max]],
            attrs={"type": "NX_FLOAT", "units": "", "nexdatas_source": None,
                   "nexdatas_strategy": "FINAL", "nexdatas_canfail": "FAILED",
                   "nexdatas_canfail_error": None})

        self._sc.checkSingleImageField(
            det, "init_pid_spectrum_float64", "float64", "NX_FLOAT64",
            [[numpy.finfo(getattr(numpy, 'float64')).max]
             for sub in spectrum],
            attrs={
                "type": "NX_FLOAT64", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "INIT", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        self._sc.checkImageField(
            det, "pid_spectrum_float32", "float32", "NX_FLOAT32",
            [[[numpy.finfo(
                getattr(
                    numpy, 'float32')).max] * 6] * 2] * 3,
            grows=2,
            attrs={
                "type": "NX_FLOAT32", "units": "", "nexdatas_source": None,
                "nexdatas_strategy": "STEP", "nexdatas_canfail": "FAILED",
                "nexdatas_canfail_error": None})

        f.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
