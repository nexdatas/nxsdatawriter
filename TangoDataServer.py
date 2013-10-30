#	"$Name:  $";
#	"$Header:  $";
#=============================================================================
#
# file :        TangoDataServer.py
#
# description : Python source for the TangoDataServer and its commands. 
#                The class is derived from Device. It represents the
#                CORBA servant object which will be accessed from the
#                network. All commands which can be executed on the
#                TangoDataServer are implemented in this file.
#
# project :     TANGO Device Server
#
# $Author:  $
#
# $Revision:  $
#
# $Log:  $
#
# copyleft :    European Synchrotron Radiation Facility
#               BP 220, Grenoble 38043
#               FRANCE
#
#=============================================================================
#  		This file is generated by POGO
#	(Program Obviously used to Generate tango Object)
#
#         (c) - Software Engineering Group - ESRF
#=============================================================================
#


import PyTango
import sys

import ndts
from ndts.TangoDataWriter import TangoDataWriter as TDW

#==================================================================
#   TangoDataServer Class Description:
#
#         Tango Server to store data in H5 files
#
#==================================================================
# 	Device States Description:
#
#   DevState.ON :       NeXuS Data Server is switch on
#   DevState.OFF :      NeXuS Data Writer is switch off
#   DevState.EXTRACT :  H5 file is open
#   DevState.OPEN :     XML configuration is initialzed
#   DevState.RUNNING :  NeXus Data Server is writing
#==================================================================


class TangoDataServer(PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------

#------------------------------------------------------------------
#	Device constructor
#------------------------------------------------------------------
	def __init__(self,cl, name):
		PyTango.Device_4Impl.__init__(self,cl,name)
		TangoDataServer.init_device(self)

#------------------------------------------------------------------
#	Device destructor
#------------------------------------------------------------------
	def delete_device(self):
		print "[Device delete_device method] for device", self.get_name()
		if hasattr(self,'tdw') and  self.tdw :
			if hasattr(self.tdw,'closeNXFile'):
				self.tdw.closeNXFile()
			del self.tdw
			self.tdw = None
		self.set_state(PyTango.DevState.OFF)


#------------------------------------------------------------------
#	Device initialization
#------------------------------------------------------------------
	def init_device(self):
		print "In ", self.get_name(), "::init_device()"
		try:
			self.set_state(PyTango.DevState.RUNNING)
			if hasattr(self,'tdw') and self.tdw:
				if hasattr(self.tdw,'closeNXFile'):
					self.tdw.closeNXFile()
				del self.tdw
				self.tdw = None
			self.tdw = TDW(self)
			self.set_state(PyTango.DevState.ON)
 		finally:
			if self.get_state() == PyTango.DevState.RUNNING:
				self.set_state(PyTango.DevState.OFF)
			
		self.get_device_properties(self.get_device_class())

#------------------------------------------------------------------
#	Always excuted hook method
#------------------------------------------------------------------
	def always_executed_hook(self):
		print "In ", self.get_name(), "::always_excuted_hook()"


#------------------------------------------------------------------
#	Device constructor
#------------------------------------------------------------------
	def __init__(self, cl, name):
		PyTango.Device_4Impl.__init__(self,cl,name)
		self.tdw = TDW(self)
		TangoDataServer.init_device(self)


#------------------------------------------------------------------
#	Read Attribute Hardware
#------------------------------------------------------------------
	def read_attr_hardware(self, data):
		print "In ", self.get_name(), "::read_attr_hardware()"

#==================================================================
#
#	TangoDataServer read/write attribute methods
#
#==================================================================
#------------------------------------------------------------------
#	Read Attribute Hardware
#------------------------------------------------------------------
	def read_attr_hardware(self,data):
		print "In ", self.get_name(), "::read_attr_hardware()"



#------------------------------------------------------------------
#	Read TheXMLSettings attribute
#------------------------------------------------------------------
	def read_TheXMLSettings(self, attr):
		print "In ", self.get_name(), "::read_TheXMLSettings()"
		
		#	Add your own code here
 		
		attr.set_value(self.tdw.xmlSettings)


#------------------------------------------------------------------
#	Write TheXMLSettings attribute
#------------------------------------------------------------------
	def write_TheXMLSettings(self, attr):
		print "In ", self.get_name(), "::write_TheXMLSettings()"
		self.tdw.xmlSettings = attr.get_write_value()
		print "Attribute value = ", self.tdw.xmlSettings


#---- TheXMLSettings attribute State Machine -----------------
	def is_TheXMLSettings_allowed(self, req_type):
		if self.get_state() in [PyTango.DevState.OFF,
		                        PyTango.DevState.EXTRACT,
		                        PyTango.DevState.RUNNING]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True


#------------------------------------------------------------------
#	Read TheJSONRecord attribute
#------------------------------------------------------------------
	def read_TheJSONRecord(self, attr):
		print "In ", self.get_name(), "::read_TheJSONRecord()"
		
		#	Add your own code here
		
		attr.set_value(self.tdw.thejson)


#------------------------------------------------------------------
#	Write TheJSONRecord attribute
#------------------------------------------------------------------
	def write_TheJSONRecord(self, attr):
		print "In ", self.get_name(), "::write_TheJSONRecord()"
		self.tdw.thejson = attr.get_write_value()
		print "Attribute value = ", self.tdw.thejson

		#	Add your own code here


#---- TheJSONRecord attribute State Machine -----------------
	def is_TheJSONRecord_allowed(self, req_type):
		if self.get_state() in [PyTango.DevState.OFF,
		                        PyTango.DevState.RUNNING]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True


#------------------------------------------------------------------
#	Read FileName attribute
#------------------------------------------------------------------
	def read_FileName(self, attr):
		print "In ", self.get_name(), "::read_FileName()"
		
		#	Add your own code here
		
		attr.set_value(self.tdw.fileName)


#------------------------------------------------------------------
#	Write FileName attribute
#------------------------------------------------------------------
	def write_FileName(self, attr):
		print "In ", self.get_name(), "::write_FileName()"
		if self.is_FileName_write_allowed():
			self.tdw.fileName = attr.get_write_value()

			print "Attribute value = ", self.tdw.fileName
		else:
			print >> self.log_warn , "To change the file name please close the file"
			raise Exception, "To change the file name please close the file"
		#	Add your own code here


#---- FileName attribute State Machine -----------------
	def is_FileName_allowed(self, req_type):
		if self.get_state() in [PyTango.DevState.OFF]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True


#---- FileName attribute Write State Machine -----------------
	def is_FileName_write_allowed(self):
		if self.get_state() in [PyTango.DevState.OFF,
		                        PyTango.DevState.EXTRACT,
		                        PyTango.DevState.OPEN,
		                        PyTango.DevState.RUNNING]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True



#==================================================================
#
#	TangoDataServer command methods
#
#==================================================================

#------------------------------------------------------------------
#	Record command:
#
#	Description: Record setting for one step
#                
#	argin:  DevString	JSON string with data
#------------------------------------------------------------------
	def Record(self, argin):
		print "In ", self.get_name(), "::Record()"
		#	Add your own code here
		self.set_state(PyTango.DevState.RUNNING)
		print "In ", self.get_name(), "::Record()"
		#	Add your own code here
		try:
			self.tdw.record(argin)
		finally:
			self.set_state(PyTango.DevState.EXTRACT)


#---- Record command State Machine -----------------
	def is_Record_allowed(self):
		if self.get_state() in [PyTango.DevState.ON,
		                        PyTango.DevState.OFF,
		                        PyTango.DevState.OPEN,
		                        PyTango.DevState.RUNNING]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True


#------------------------------------------------------------------
#	OpenFile command:
#
#	Description: Open the H5 file
#                
#------------------------------------------------------------------
	def OpenFile(self):
		print "In ", self.get_name(), "::OpenFile()"
		#	Add your own code here
		self.set_state(PyTango.DevState.RUNNING)
		try:
			self.tdw.openNXFile()
			self.set_state(PyTango.DevState.OPEN)
 		finally:
			if self.get_state() == PyTango.DevState.RUNNING:
				self.set_state(PyTango.DevState.ON)


#---- OpenFile command State Machine -----------------
	def is_OpenFile_allowed(self):
		if self.get_state() in [PyTango.DevState.OFF,
		                        PyTango.DevState.EXTRACT,
		                        PyTango.DevState.OPEN,
		                        PyTango.DevState.RUNNING]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True


#------------------------------------------------------------------
#	CloseFile command:
#
#	Description: Close the H5 file
#                
#------------------------------------------------------------------
	def CloseFile(self):
		print "In ", self.get_name(), "::CloseFile()"
		#	Add your own code here
		if self.get_state() in [PyTango.DevState.EXTRACT,
		                        PyTango.DevState.RUNNING]:
			self.CloseEntry()
		self.set_state(PyTango.DevState.RUNNING)
		try:
			self.tdw.closeNXFile()
			self.set_state(PyTango.DevState.ON)
 		finally:
			if self.get_state() == PyTango.DevState.RUNNING:
				self.set_state(PyTango.DevState.OPEN)


#---- CloseFile command State Machine -----------------
	def is_CloseFile_allowed(self):
		if self.get_state() in [PyTango.DevState.ON,
		                        PyTango.DevState.OFF,
		                        PyTango.DevState.RUNNING]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True


#------------------------------------------------------------------
#	OpenEntry command:
#
#	Description: Creating the new entry
#                
#------------------------------------------------------------------
	def OpenEntry(self):
		print "In ", self.get_name(), "::OpenEntry()"
		#	Add your own code here
		self.set_state(PyTango.DevState.RUNNING)
		try:
			self.get_device_properties(self.get_device_class())
			self.tdw.numThreads = self.NumberOfThreads
			self.tdw.openEntry()
			self.set_state(PyTango.DevState.EXTRACT)
 		finally:
			if self.get_state() == PyTango.DevState.RUNNING:
				self.set_state(PyTango.DevState.OPEN)


#---- OpenEntry command State Machine -----------------
	def is_OpenEntry_allowed(self):
		if self.get_state() in [PyTango.DevState.ON,
		                        PyTango.DevState.OFF,
		                        PyTango.DevState.EXTRACT,
		                        PyTango.DevState.RUNNING]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True


#------------------------------------------------------------------
#	CloseEntry command:
#
#	Description: Closing the entry
#                
#------------------------------------------------------------------
	def CloseEntry(self):
		print "In ", self.get_name(), "::CloseEntry()"
		#	Add your own code here
		self.set_state(PyTango.DevState.RUNNING)
		try:
			self.tdw.closeEntry()
			self.set_state(PyTango.DevState.OPEN)
 		finally:
			if self.get_state() == PyTango.DevState.RUNNING:
				self.set_state(PyTango.DevState.EXTRACT)


#---- CloseEntry command State Machine -----------------
	def is_CloseEntry_allowed(self):
		if self.get_state() in [PyTango.DevState.ON,
		                        PyTango.DevState.OFF,
		                        PyTango.DevState.OPEN,
		                        PyTango.DevState.RUNNING]:
			#	End of Generated Code
			#	Re-Start of Generated Code
			return False
		return True


#==================================================================
#
#	TangoDataServerClass class definition
#
#==================================================================
class TangoDataServerClass(PyTango.DeviceClass):

	#	Class Properties
	class_property_list = {
		}


	#	Device Properties
	device_property_list = {
		'NumberOfThreads':
			[PyTango.DevLong,
			"maximal number of threads",
			[ 100 ] ],
		}


	#	Command definitions
	cmd_list = {
		'Record':
			[[PyTango.DevString, "JSON string with data"],
			[PyTango.DevVoid, ""]],
		'OpenFile':
			[[PyTango.DevVoid, ""],
			[PyTango.DevVoid, ""]],
		'CloseFile':
			[[PyTango.DevVoid, ""],
			[PyTango.DevVoid, ""]],
		'OpenEntry':
			[[PyTango.DevVoid, ""],
			[PyTango.DevVoid, ""]],
		'CloseEntry':
			[[PyTango.DevVoid, ""],
			[PyTango.DevVoid, ""]],
		}


	#	Attribute definitions
	attr_list = {
		'TheXMLSettings':
			[[PyTango.DevString,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'label':"XML Configuration",
				'description':"An XML string with Nexus configuration.",
				'Display level':PyTango.DispLevel.EXPERT,
			} ],
		'TheJSONRecord':
			[[PyTango.DevString,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'label':"JSON string with client data",
				'description':"A JSON string with global client data.",
				'Display level':PyTango.DispLevel.EXPERT,
			} ],
		'FileName':
			[[PyTango.DevString,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'label':"Output file with its path",
				'description':"A name of H5 output file with its full path",
			} ],
		}


#------------------------------------------------------------------
#	TangoDataServerClass Constructor
#------------------------------------------------------------------
	def __init__(self, name):
		PyTango.DeviceClass.__init__(self, name)
		self.set_type(name);
		print "In TangoDataServerClass  constructor"

#==================================================================
#
#	TangoDataServer class main method
#
#==================================================================
if __name__ == '__main__':
	try:
		py = PyTango.Util(sys.argv)
		py.add_TgClass(TangoDataServerClass, TangoDataServer, 'TangoDataServer')

		U = PyTango.Util.instance()
		U.server_init()
		U.server_run()

	except PyTango.DevFailed, e:
		print '-------> Received a DevFailed exception:', e
	except Exception, e:
		print '-------> An unforeseen exception occured....', e
