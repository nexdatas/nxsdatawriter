#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2026 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
#
# \file TangoDataWriterH5Map_test.py
# unittests for TangoDataWriter with the h5map writer
#
import json
import os
import tempfile
import unittest

import nxswriter.TangoDataWriter as TDW

try:
    from nxstools import h5mapwriter as H5MapWriter
except Exception:
    H5MapWriter = None


XML = """<definition>
 <group type="NXentry" name="entry1">
  <group type="NXinstrument" name="instrument">
   <group type="NXdetector" name="det">
    <field units="m" type="NX_FLOAT32" name="counter">
     <strategy mode="STEP"/>
     <datasource type="CLIENT" name="c01"><record name="exp_c01"/></datasource>
    </field>
    <field type="NX_INT64" name="init_val">
     <strategy mode="INIT"/>
     <datasource type="CLIENT" name="ival"><record name="ival"/></datasource>
    </field>
    <field type="NX_CHAR" name="end_time">
     <strategy mode="FINAL"/>
     <datasource type="CLIENT" name="end_time">
      <record name="end_time"/>
     </datasource>
    </field>
   </group>
  </group>
  <group type="NXdata" name="data">
   <link name="counter" target="/entry1/instrument/det/counter"/>
  </group>
 </group>
</definition>"""


@unittest.skipIf(H5MapWriter is None, "nxstools.h5mapwriter not available")
class TangoDataWriterH5MapTest(unittest.TestCase):

    def test_writer(self):
        self.assertEqual(TDW.WRITERS["h5map"], H5MapWriter)
        self.assertTrue("h5map" not in TDW.DEFAULTWRITERS)

    def test_h5map(self):
        fname = os.path.join(tempfile.mkdtemp(), "h5map.nxs")
        streams = {"c01": "scan:exp_c01"}
        tdw = TDW.TangoDataWriter()
        tdw.writer = "h5map"
        tdw.fileName = fname
        tdw.openFile()
        tdw.xmlsettings = XML
        tdw.jsonrecord = json.dumps({"data": {"ival": 7}})
        tdw.openEntry()
        start = tdw.getFile().h5map(streams, skip=["FINAL"])
        tdw.jsonrecord = json.dumps(
            {"data": {"end_time": "2026-11-25T10:00:00"}})
        tdw.closeEntry()
        end = tdw.getFile().h5maps(streams)
        tdw.closeFile()
        self.assertFalse(os.path.exists(fname))
        os.rmdir(os.path.dirname(fname))

        self.assertEqual(list(end.keys()), [fname])
        end = end[fname]
        json.dumps(start, allow_nan=False)
        json.dumps(end, allow_nan=False)

        def det(h5map):
            return h5map["children"]["entry1"]["children"][
                "instrument"]["children"]["det"]["children"]

        self.assertEqual(sorted(det(start)), ["counter", "init_val"])
        self.assertEqual(
            sorted(det(end)), ["counter", "end_time", "init_val"])
        self.assertEqual(
            det(end)["counter"]["value"],
            {"type": "stream", "stream": "scan:exp_c01"})
        self.assertEqual(
            det(end)["init_val"]["value"],
            {"type": "inline", "dtype": "int64", "value": [7]})
        self.assertEqual(
            det(end)["end_time"]["value"], "2026-11-25T10:00:00")


if __name__ == '__main__':
    unittest.main()
