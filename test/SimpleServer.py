#	"$Name:  $";
#	"$Header:  $";
#=============================================================================
#
# file :        SimpleServer.py
#
# description : Python source for the SimpleServer and its commands. 
#                The class is derived from Device. It represents the
#                CORBA servant object which will be accessed from the
#                network. All commands which can be executed on the
#                SimpleServer are implemented in this file.
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


#==================================================================
#   SimpleServer Class Description:
#
#         My Simple Server
#
#==================================================================
# 	Device States Description:
#
#   DevState.ON :  Server On
#==================================================================


class SimpleServer(PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------

#------------------------------------------------------------------
#	Device constructor
#------------------------------------------------------------------
	def __init__(self,cl, name):
		PyTango.Device_4Impl.__init__(self,cl,name)
		SimpleServer.init_device(self)

#------------------------------------------------------------------
#	Device destructor
#------------------------------------------------------------------
	def delete_device(self):
		print "[Device delete_device method] for device",self.get_name()


#------------------------------------------------------------------
#	Device initialization
#------------------------------------------------------------------
	def init_device(self):
		print "In ", self.get_name(), "::init_device()"
		self.set_state(PyTango.DevState.ON)
		self.get_device_properties(self.get_device_class())

		self.attr_ScalarBoolean=[True]
		self.attr_ScalarShort=[12]
		self.attr_ScalarUShort=[12]
		self.attr_ScalarLong=[123]
		self.attr_ScalarULong=[123]
		self.attr_ScalarLong64=[123]
		self.attr_ScalarULong64=[123]

#------------------------------------------------------------------
#	Always excuted hook method
#------------------------------------------------------------------
	def always_executed_hook(self):
		print "In ", self.get_name(), "::always_excuted_hook()"

#==================================================================
#
#	SimpleServer read/write attribute methods
#
#==================================================================
#------------------------------------------------------------------
#	Read Attribute Hardware
#------------------------------------------------------------------
	def read_attr_hardware(self,data):
		print "In ", self.get_name(), "::read_attr_hardware()"



#------------------------------------------------------------------
#	Read ScalarLong attribute
#------------------------------------------------------------------
	def read_ScalarLong(self, attr):
		print "In ", self.get_name(), "::read_ScalarLong()"
		
		#	Add your own code here		
		attr.set_value(self.attr_ScalarLong[0])


#------------------------------------------------------------------
#	Write ScalarLong attribute
#------------------------------------------------------------------
	def write_ScalarLong(self, attr):
		print "In ", self.get_name(), "::write_ScalarLong()"

		#	Add your own code here
		self.attr_ScalarLong = []
		attr.get_write_value(self.attr_ScalarLong)
		print "Attribute value = ", self.attr_ScalarLong


#------------------------------------------------------------------
#	Read ScalarBoolean attribute
#------------------------------------------------------------------
	def read_ScalarBoolean(self, attr):
		print "In ", self.get_name(), "::read_ScalarBoolean()"
		
		#	Add your own code here
		
		attr.set_value(self.attr_ScalarBoolean[0])


#------------------------------------------------------------------
#	Write ScalarBoolean attribute
#------------------------------------------------------------------
	def write_ScalarBoolean(self, attr):
		print "In ", self.get_name(), "::write_ScalarBoolean()"

		#	Add your own code here
		self.attr_ScalarBoolean = []
		attr.get_write_value(self.attr_ScalarBoolean)
		print "Attribute value = ", self.attr_ScalarBoolean


#------------------------------------------------------------------
#	Read ScalarShort attribute
#------------------------------------------------------------------
	def read_ScalarShort(self, attr):
		print "In ", self.get_name(), "::read_ScalarShort()"
		
		#	Add your own code here
		attr.set_value(self.attr_ScalarShort[0])


#------------------------------------------------------------------
#	Write ScalarShort attribute
#------------------------------------------------------------------
	def write_ScalarShort(self, attr):
		print "In ", self.get_name(), "::write_ScalarShort()"

		#	Add your own code here
		self.attr_ScalarShort = []
		attr.get_write_value(self.attr_ScalarShort)
		print "Attribute value = ", self.attr_ScalarShort


#------------------------------------------------------------------
#	Read ScalarUShort attribute
#------------------------------------------------------------------
	def read_ScalarUShort(self, attr):
		print "In ", self.get_name(), "::read_ScalarUShort()"
		
		#	Add your own code here
		attr.set_value(self.attr_ScalarUShort[0])


#------------------------------------------------------------------
#	Write ScalarUShort attribute
#------------------------------------------------------------------
	def write_ScalarUShort(self, attr):
		print "In ", self.get_name(), "::write_ScalarUShort()"

		#	Add your own code here
		self.attr_ScalarUShort = []
		attr.get_write_value(self.attr_ScalarUShort)
		print "Attribute value = ", self.attr_ScalarUShort


#------------------------------------------------------------------
#	Read ScalarULong attribute
#------------------------------------------------------------------
	def read_ScalarULong(self, attr):
		print "In ", self.get_name(), "::read_ScalarULong()"
		
		#	Add your own code here
		
		attr.set_value(self.attr_ScalarULong[0])


#------------------------------------------------------------------
#	Write ScalarULong attribute
#------------------------------------------------------------------
	def write_ScalarULong(self, attr):
		print "In ", self.get_name(), "::write_ScalarULong()"

		#	Add your own code here
		self.attr_ScalarULong = []
		attr.get_write_value(self.attr_ScalarULong)
		print "Attribute value = ", self.attr_ScalarULong


#------------------------------------------------------------------
#	Read ScalarLong64 attribute
#------------------------------------------------------------------
	def read_ScalarLong64(self, attr):
		print "In ", self.get_name(), "::read_ScalarLong64()"
		
		#	Add your own code here
		attr.set_value(self.attr_ScalarLong64[0])


#------------------------------------------------------------------
#	Write ScalarLong64 attribute
#------------------------------------------------------------------
	def write_ScalarLong64(self, attr):
		print "In ", self.get_name(), "::write_ScalarLong64()"

		#	Add your own code here
		self.attr_ScalarLong64 = []
		attr.get_write_value(self.attr_ScalarLong64)
		print "Attribute value = ", self.attr_ScalarLong64


#------------------------------------------------------------------
#	Read ScalarULong64 attribute
#------------------------------------------------------------------
	def read_ScalarULong64(self, attr):
		print "In ", self.get_name(), "::read_ScalarULong64()"
		
		#	Add your own code here
		attr.set_value(self.attr_ScalarLong64[0])
#		attr.set_value(self.attr_ScalarULong64[0])
#		attr.set_value(123)


#------------------------------------------------------------------
#	Write ScalarULong64 attribute
#------------------------------------------------------------------
	def write_ScalarULong64(self, attr):
		print "In ", self.get_name(), "::write_ScalarULong64()"

		#	Add your own code here
		self.attr_ScalarULong64 = []
		attr.get_write_value(self.attr_ScalarULong64)
		print "Attribute value = ", self.attr_ScalarULong64


#------------------------------------------------------------------
#	Read ScalarFloat attribute
#------------------------------------------------------------------
	def read_ScalarFloat(self, attr):
		print "In ", self.get_name(), "::read_ScalarFloat()"
		
		#	Add your own code here
		
		attr_ScalarFloat_read = 123.43
		attr.set_value(attr_ScalarFloat_read)


#------------------------------------------------------------------
#	Write ScalarFloat attribute
#------------------------------------------------------------------
	def write_ScalarFloat(self, attr):
		print "In ", self.get_name(), "::write_ScalarFloat()"
		data=[]
		attr.get_write_value(data)
		print "Attribute value = ", data

		#	Add your own code here


#------------------------------------------------------------------
#	Read ScalarDouble attribute
#------------------------------------------------------------------
	def read_ScalarDouble(self, attr):
		print "In ", self.get_name(), "::read_ScalarDouble()"
		
		#	Add your own code here
		
		attr_ScalarDouble_read = -12.345
		attr.set_value(attr_ScalarDouble_read)


#------------------------------------------------------------------
#	Write ScalarDouble attribute
#------------------------------------------------------------------
	def write_ScalarDouble(self, attr):
		print "In ", self.get_name(), "::write_ScalarDouble()"
		data=[]
		attr.get_write_value(data)
		print "Attribute value = ", data

		#	Add your own code here


#------------------------------------------------------------------
#	Read ScalarString attribute
#------------------------------------------------------------------
	def read_ScalarString(self, attr):
		print "In ", self.get_name(), "::read_ScalarString()"
		
		#	Add your own code here
		
		attr_ScalarString_read = "Hello Tango world"
		attr.set_value(attr_ScalarString_read)


#------------------------------------------------------------------
#	Write ScalarString attribute
#------------------------------------------------------------------
	def write_ScalarString(self, attr):
		print "In ", self.get_name(), "::write_ScalarString()"
		data=[]
		attr.get_write_value(data)
		print "Attribute value = ", data

		#	Add your own code here


#------------------------------------------------------------------
#	Read ScalarEncoded attribute
#------------------------------------------------------------------
	def read_ScalarEncoded(self, attr):
		print "In ", self.get_name(), "::read_ScalarEncoded()"
		
		#	Add your own code here
		
		attr_ScalarEncoded_read = 1
		attr.set_value(attr_ScalarEncoded_read)


#------------------------------------------------------------------
#	Write ScalarEncoded attribute
#------------------------------------------------------------------
	def write_ScalarEncoded(self, attr):
		print "In ", self.get_name(), "::write_ScalarEncoded()"
		data=[]
		attr.get_write_value(data)
		print "Attribute value = ", data

		#	Add your own code here



#==================================================================
#
#	SimpleServer command methods
#
#==================================================================

#==================================================================
#
#	SimpleServerClass class definition
#
#==================================================================
class SimpleServerClass(PyTango.DeviceClass):

	#	Class Properties
	class_property_list = {
		}


	#	Device Properties
	device_property_list = {
		}


	#	Command definitions
	cmd_list = {
		}


	#	Attribute definitions
	attr_list = {
		'ScalarLong':
			[[PyTango.DevLong,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"test long scalar attribute",
			} ],
		'ScalarBoolean':
			[[PyTango.DevBoolean,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"test scalar bool attribute",
			} ],
		'ScalarShort':
			[[PyTango.DevShort,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"Scalar Short attribute",
			} ],
		'ScalarUShort':
			[[PyTango.DevUShort,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"ScalarUShort attribute",
			} ],
		'ScalarULong':
			[[PyTango.DevULong,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"ScalarULong attribute",
			} ],
		'ScalarLong64':
			[[PyTango.DevLong64,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"ScalarLong64 attribute",
			} ],
		'ScalarULong64':
			[[PyTango.DevULong64,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"ScalarULong64 attribute",
			} ],
		'ScalarFloat':
			[[PyTango.DevFloat,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"ScalarFloat attribute",
			} ],
		'ScalarDouble':
			[[PyTango.DevDouble,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"ScalarDouble attribute",
			} ],
		'ScalarString':
			[[PyTango.DevString,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"ScalarString attribute",
			} ],
		'ScalarEncoded':
			[[PyTango.DevEncoded,
			PyTango.SCALAR,
			PyTango.READ_WRITE],
			{
				'description':"ScalarEncoded attribute",
			} ],
		}


#------------------------------------------------------------------
#	SimpleServerClass Constructor
#------------------------------------------------------------------
	def __init__(self, name):
		PyTango.DeviceClass.__init__(self, name)
		self.set_type(name);
		print "In SimpleServerClass  constructor"

#==================================================================
#
#	SimpleServer class main method
#
#==================================================================
if __name__ == '__main__':
	try:
		py = PyTango.Util(sys.argv)
		py.add_TgClass(SimpleServerClass,SimpleServer,'SimpleServer')

		U = PyTango.Util.instance()
		U.server_init()
		U.server_run()

	except PyTango.DevFailed,e:
		print '-------> Received a DevFailed exception:',e
	except Exception,e:
		print '-------> An unforeseen exception occured....',e
