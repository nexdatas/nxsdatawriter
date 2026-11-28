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
# \file PniNexusXML_test.py
# unittests for xml settings of the pninexus xml builder
#
import json
import os
import shutil
import tempfile
import unittest

import h5py
import numpy

from nxswriter.TangoDataWriter import TangoDataWriter
from nxswriter.Types import NTP

try:
    from pninexus import h5cpp  # noqa: F401
    WRITERS = ["h5py", "h5cpp"]
except Exception:
    WRITERS = ["h5py"]


XML = """<definition><group type="NXentry" name="entry">
 <field name="i8" type="i8">-5</field>
 <field name="u16" type="ui16">7</field>
 <field name="f32" type="f32">1.5</field>
 <field name="f64" type="float64">2.5</field>
 <field name="b" type="bool_t">true</field>
 <field name="s" type="str">abc</field>
 <field name="spec" type="NX_INT32">
  <dimensions rank="1"><dim index="1" value="6"/></dimensions>
  <chunk rank="1"><dim index="1" value="3"/></chunk>
  <strategy mode="INIT"/>
  <datasource type="CLIENT" name="spec"><record name="spec"/></datasource>
 </field>
 <field name="img" type="ui32">
  <dimensions rank="2"><dim index="1" value="4"/><dim index="2" value="5"/>
  </dimensions>
  <chunk rank="2"><dim index="0" value="2"/><dim index="1" value="5"/>
  </chunk>
  <strategy mode="STEP"/>
  <datasource type="CLIENT" name="img"><record name="img"/></datasource>
 </field>
 <field name="full" type="NX_FLOAT64">
  <dimensions rank="1"><dim index="1" value="4"/></dimensions>
  <chunk rank="2"><dim index="1" value="2"/><dim index="2" value="2"/>
  </chunk>
  <strategy mode="STEP"/>
  <datasource type="CLIENT" name="full"><record name="full"/></datasource>
 </field>
 <field name="bad" type="NX_FLOAT64">
  <dimensions rank="1"><dim index="1" value="4"/></dimensions>
  <chunk rank="3"><dim index="1" value="1"/><dim index="2" value="1"/>
   <dim index="3" value="1"/></chunk>
  <strategy mode="STEP"/>
  <datasource type="CLIENT" name="bad"><record name="bad"/></datasource>
 </field>
 <attribute name="tattr" type="str">text</attribute>
</group></definition>"""


class PniNexusXMLTest(unittest.TestCase):
    """ xml settings of the pninexus xml builder """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_type_names(self):
        types = {"uint8": "uint8", "ui8": "uint8", "int8": "int8",
                 "i8": "int8", "uint16": "uint16", "ui16": "uint16",
                 "int16": "int16", "i16": "int16", "uint32": "uint32",
                 "ui32": "uint32", "int32": "int32", "i32": "int32",
                 "uint64": "uint64", "ui64": "uint64", "int64": "int64",
                 "i64": "int64", "float32": "float32", "f32": "float32",
                 "float64": "float64", "f64": "float64",
                 "string": "string", "str": "string", "ascii": "string",
                 "bool": "bool", "bool_t": "bool", "ebool": "bool",
                 "ibool": "bool"}
        for name, nptype in types.items():
            self.assertEqual(NTP.nTnp[name], nptype)
        # NeXus type names are not changed
        self.assertEqual(NTP.nTnp["NX_INT16"], "int16")
        self.assertEqual(NTP.nTnp["NX_DATE_TIME"], "string")
        self.assertEqual(NTP.charTypes, ["NX_CHAR", "string", "str", "ascii"])

    def write(self, writer):
        fname = os.path.join(self.tmpdir, "pni_%s.h5" % writer)
        tdw = TangoDataWriter()
        tdw.writer = writer
        tdw.fileName = fname
        tdw.openFile()
        tdw.xmlsettings = XML
        tdw.jsonrecord = json.dumps({"data": {"spec": [1, 2, 3, 4, 5, 6]}})
        tdw.openEntry()
        for i in range(2):
            tdw.record(json.dumps({"data": {
                "img": [[i] * 5] * 4,
                "full": [1.0, 2.0, 3.0, 4.0],
                "bad": [1.0, 2.0, 3.0, 4.0]}}))
        tdw.closeEntry()
        tdw.closeFile()
        return fname

    def test_file(self):
        for writer in WRITERS:
            with h5py.File(self.write(writer), "r") as fl:
                entry = fl["entry"]
                dtypes = {"i8": numpy.int8, "u16": numpy.uint16,
                          "f32": numpy.float32, "f64": numpy.float64,
                          "b": numpy.bool_}
                for name, dtype in dtypes.items():
                    self.assertEqual(entry[name].dtype, dtype, writer)
                self.assertEqual(entry["i8"][()][0], -5)
                self.assertEqual(entry["u16"][()][0], 7)
                self.assertEqual(entry["f32"][()][0], 1.5)
                self.assertEqual(entry["b"][()][0], True)
                svalue = entry["s"][()]
                if isinstance(svalue, bytes):
                    svalue = svalue.decode()
                self.assertEqual(svalue, "abc")
                self.assertEqual(entry.attrs["tattr"], "text")
                # chunks of the chunk tag
                self.assertEqual(entry["spec"].chunks, (3,), writer)
                self.assertEqual(list(entry["spec"][()]), [1, 2, 3, 4, 5, 6])
                # chunks without the growing dimension of STEP fields
                self.assertEqual(entry["img"].shape, (2, 4, 5))
                self.assertEqual(entry["img"].chunks, (1, 2, 5), writer)
                self.assertEqual(entry["img"].dtype, numpy.uint32)
                # chunks with the growing dimension
                self.assertEqual(entry["full"].chunks, (2, 2), writer)
                # chunks not fitting the shape are not used
                self.assertEqual(entry["bad"].shape, (2, 4))
                self.assertEqual(entry["bad"].chunks, (1, 4), writer)


if __name__ == '__main__':
    unittest.main()
