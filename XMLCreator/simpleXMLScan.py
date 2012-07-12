#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from simpleXML import *

if __name__ == "__main__":
	df=XMLFile("scan.xml")
	
	en = NGroup(df.root,"entry1","NXentry")

	## instrument
	ins = NGroup(en.elem,"instrument","NXinstrument")
#	NXsource	
	src = NGroup(ins.elem,"source","NXsource")
	f = NField(src.elem,"counter1","NX_FLOAT")
	f.setUnits("m")
#	f.setText("0.2")
	sr=NDSource(f.elem,"STEP")
	sr.initClient("p09/counter/exp.01");


	f = NField(src.elem,"counter2","NX_FLOAT")
	f.setUnits("s")
#	f.setText("0.2")
	sr=NDSource(f.elem,"STEP")
	sr.initClient("p09/counter/exp.02");
	

	f = NField(src.elem,"mca","NX_FLOAT")
	f.setUnits("")

	d=NDimensions(f.elem,"1")
	d.dim("1","2048")

#	f.setText("0.2")
	sr=NDSource(f.elem,"STEP")
	sr.initClient("p09/mca/exp.02");

	df.dump()

 