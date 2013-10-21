#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package ndts nexdatas
## \file EField.py
# NeXus runnable elements

""" Definitions of field tag evaluation classes """

import sys

import numpy

from .DataHolder import DataHolder
from .Element import Element
from .FElement import FElementWithAttr
from .FieldArray import FieldArray
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)
from . import Streams

import pni.io.nx.h5 as nx



## field H5 tag element
class EField(FElementWithAttr):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        FElementWithAttr.__init__(self, "field", attrs, last)
        ## rank of the field
        self.rank = "0"
        ## shape of the field
        self.lengths = {}
        ## if field is stored in STEP mode
        self.__extraD = False
        ## if field array is splitted into columns
        self.__splitArray = False
        ## strategy, i.e. INIT, STEP, FINAL, POSTRUN
        self.strategy = None
        ## trigger for asynchronous writing
        self.trigger = None
        ## growing dimension
        self.grows = None
        ## label for postprocessing data
        self.postrun = ""
        ## compression flag
        self.compression = False
        ## compression rate
        self.rate = 5
        ## compression shuffle
        self.shuffle = True
        ## data format
        self.__format = ''

    ## checks if it is growing in extra dimension
    # \brief It checks if it is growing in extra dimension 
    # and setup internal variables     
    def __isgrowing(self):
        self.__extraD = False
        if self.source and self.source.isValid() and self.strategy == "STEP":
            self.__extraD = True
            if not self.grows:
                self.grows = 1
        else:
            self.grows = None

    ## provides type and name of the field
    # \returns (type, name) tuple        
    def __typeAndName(self):
        if "name" in self._tagAttrs.keys():
            nm = self._tagAttrs["name"]
            if "type" in self._tagAttrs.keys():
                tp = NTP.nTnp[self._tagAttrs["type"]]
            else:
                tp = "string"
            return tp, nm    
        else:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "FElement::__typeAndName() - Field without a name"

            raise XMLSettingSyntaxError, "Field without a name"

    ## provides shape
    # \param dtypy object type    
    # \returns object shape    
    def __getShape(self, dtype):
        try:
            if dtype.encode() == "string":
                shape = self._findShape(self.rank, self.lengths, 
                                        self.__extraD, self.grows)
            else:
                shape = self._findShape(self.rank, self.lengths, 
                                        self.__extraD, self.grows, True)
#            print "ifstring", nm, shape, self.grows
            if self.grows > len(shape):
                self.grows = len(shape)

            if len(shape) > 1 and dtype.encode() == "string":
                self.__splitArray = True
                shape = self._findShape(self.rank, self.lengths, self.__extraD)
                if self.__extraD:
                    self.grows = 1
                    
            return shape
        except XMLSettingSyntaxError:
            if self.strategy == "POSTRUN": 
                self.__splitArray = False
                if self.rank and int(self.rank) >=0:
                    shape = [0]*int(self.rank)
                else:
                    shape = [0]
                return shape
            else:
                if Streams.log_error:
                    print >> Streams.log_error, \
                        "FElement::__getShape() - "\
                        "Shape of %s cannot be found  " % self._tagAttrs["name"]
                raise XMLSettingSyntaxError, \
                    "Wrongly defined %sshape: %s"% \
                    (self._tagAttrs["name"] + " " , str(self.source)) 
            

    ## creates H5 object
    # \param dtype object type    
    # \param name object name
    # \param shape object shape    
    # \returns H5 object
    def __createObject(self, dtype, name, shape):
        chunk = [s if s > 0 else 1 for s in shape]  
        deflate = None
        # create Filter
        if self.compression:
            deflate = nx.NXDeflateFilter()
            deflate.rate = self.rate
            deflate.shuffle = self.shuffle
       
        try:    
            if shape:
                if self.__splitArray:
                    f = FieldArray(self._lastObject(), name.encode(), 
                                   dtype.encode(), shape)
                else:
                    if not chunk:
                        f = self._lastObject().create_field(
                            name.encode(), dtype.encode(), shape, [],
                            deflate)
                    else:
                        f = self._lastObject().create_field(
                            name.encode(), dtype.encode(), shape, chunk, 
                            deflate)
            else:
                f = self._lastObject().create_field(
                    name.encode(), dtype.encode(), [], [], deflate)
        except:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "EField::__createObject() - "\
                    "The field '%s' of '%s' type cannot be created" % \
                    (name.encode(), dtype.encode())
            raise XMLSettingSyntaxError, \
                "The fieled '%s' of '%s' type cannot be created" % \
                (name.encode(),dtype.encode())
                 
        return f
        

    ## creates attributes 
    # \brief It creates attributes in h5Object
    def __setAttributes(self):
        for key in self._tagAttrs.keys():
            if key not in ["name"]:
                if key in NTP.aTn.keys():
                    if hasattr(self._tagAttrs[key],"encode"):
                        try:
                            (self.h5Object.attr(
                                    key.encode(), 
                                    NTP.nTnp[NTP.aTn[key]].encode())).value = \
                                    self._tagAttrs[key].strip().encode()
                        except:
                            (self.h5Object.attr(
                                    key.encode(), 
                                    NTP.nTnp[NTP.aTn[key]].encode())).value = \
                                    NTP.convert[
                                        str(self.h5Object.attr(key.encode()
                                                               ).dtype)
                                        ](self._tagAttrs[key].strip().encode())
                    else:
                        try:
                            (self.h5Object.attr(
                                    key.encode(), NTP.nTnp[NTP.aTn[key]
                                                           ].encode())
                             ).value = self._tagAttrs[key]
                        except:
                            (self.h5Object.attr(
                                    key.encode(), 
                                    NTP.nTnp[NTP.aTn[key]].encode())
                             ).value = \
                             NTP.convert[str(self.h5Object.attr(
                                         key.encode()).dtype)
                                         ](self._tagAttrs[key])
                             
                elif key in NTP.aTnv.keys():
                    shape = (len(self._tagAttrs[key]),)
                    (self.h5Object.attr(
                            key.encode(), 
                            NTP.nTnp[NTP.aTnv[key]].encode(),shape)
                     ).value = \
                     numpy.array(self._tagAttrs[key])
                else:
                    (self.h5Object.attr(key.encode(), "string")).value = \
                        self._tagAttrs[key].strip().encode()

        self._createAttributes()        
                
        if self.strategy == "POSTRUN":
            self.h5Object.attr("postrun".encode(), 
                               "string".encode()).value = \
                self.postrun.encode().strip()




    ## provides strategy or fill the value in
    # \param name object name
    # \returns strategy or strategy,trigger it trigger defined 
    def __setStrategy(self, name):
        if self.source:
            if  self.source.isValid() :
                return self.strategy, self.trigger
        else:
            val = ("".join(self.content)).strip().encode()   
            if val:
                if not self.rank or int(self.rank) == 0:
                    dh = DataHolder("SCALAR", val, "DevString", [1, 0])
                elif  int(self.rank) == 1:
                    spec = val.split()
                    dh = DataHolder("SPECTRUM", spec, 
                                    "DevString", [len(spec), 0])
                elif  int(self.rank) == 2:
                    lines = val.split("\n")
                    image = [ln.split() for ln in lines ]
                    dh = DataHolder("IMAGE", image, "DevString", 
                                    [len(image),len(image[0])])
                else:    
                    if Streams.log_error:
                        print >> Streams.log_error, \
                            "EField::__setStrategy() - "\
                            "Case with not supported rank = %s" % self.rank

                    raise XMLSettingSyntaxError, \
                        "Case with not supported rank = %s" % self.rank


                if self.h5Object.dtype != "string" or not self.rank \
                        or int(self.rank) == 0:
                    self.h5Object[...] = dh.cast(self.h5Object.dtype)
#                    self.h5Object.write(dh.cast(self.h5Object.dtype))
                elif int(self.rank) == 1:
                    sts = dh.cast(self.h5Object.dtype)
                    for i in range(len(sts)):
                        self.h5Object[i] = sts[i] 
                elif int(self.rank) == 2:        
                    sts = dh.cast(self.h5Object.dtype)
                    for i in range(len(sts)):
                        for j in range(len(sts[i])):
                            self.h5Object[i, j] = sts[i][j] 

            elif self.strategy != "POSTRUN":
                if self.h5Object.dtype != "string": 
                    if Streams.log_error:
                        print >> Streams.log_error, \
                            "EField::__setStrategy() - "\
                            "Warning: Invalid datasource for %s" % name
                    raise ValueError, \
                        "Warning: Invalid datasource for %s" % name
                else:
                    print >> sys.stderr, \
                        "EField::__setStrategy() - "\
                        "Warning: Empty value for the field:", name

            
    ## stores the tag content
    # \param xml xml setting 
    # \param globalJSON global JSON string
    # \returns (strategy, trigger)
    def store(self, xml = None, globalJSON = None):
        
        # if it is growing in extra dimension
        self.__isgrowing()
        # type and name
        tp, nm = self.__typeAndName()
        # shape
        shape = self.__getShape(tp)
        # create h5 object
        self.h5Object = self.__createObject(tp, nm, shape)
        # create attributes
        self.__setAttributes()

        # return strategy or fill the value in
        return self.__setStrategy(nm)



    ## writes non-growing data
    # \param holder data holder
    def __writeData(self, holder):
        if len(self.h5Object.shape) == 1 and self.h5Object.shape[0] >1 \
                and self.h5Object.dtype == "string":
            sts = holder.cast(self.h5Object.dtype)
            if len(holder.shape) > 1 and holder.shape[0] == 1:
                for i in range(len(sts[0])):
                    self.h5Object[i] = sts[0][i] 
            elif len(holder.shape) > 1 and holder.shape[1] == 1:
                for i in range(len(sts)):
                    self.h5Object[i] = sts[i][0] 
            else:
                for i in range(len(sts)):
                    self.h5Object[i] = sts[i] 
        elif len(self.h5Object.shape) == 1 and self.h5Object.shape[0] == 1 :
            sts = holder.cast(self.h5Object.dtype)
            if hasattr(sts, "__iter__")  and type(sts).__name__ != 'str':
                if self.h5Object.dtype == "string":
                    if hasattr(sts[0], "__iter__")  and \
                            type(sts[0]).__name__ != 'str':
                        self.h5Object.write(sts[0][0])
                    else:
                        self.h5Object.write(sts[0])
                else:
                    try:
                        self.h5Object.write(sts)
                    except:    
                        if Streams.log_error:
                            print >> Streams.log_error, \
                                "EField::__writedata() - "\
                                "Storing one-dimension single fields"\
                                " not supported by pniio"
                        raise Exception(
                            "Storing one-dimension single fields"\
                                " not supported by pniio")
            else:
                self.h5Object.write(sts)

        elif  len(self.h5Object.shape) == 2 \
                and self.h5Object.dtype == "string":       
            sts = holder.cast(self.h5Object.dtype)
            if str(holder.format).split('.')[-1] == "IMAGE":
                for i in range(len(sts)):
                    for j in range(len(sts[i])):
                        self.h5Object[i, j] = sts[i][j] 
            elif str(holder.format).split('.')[-1] == "SPECTRUM":
                for i in range(len(sts)):
                    self.h5Object[i, :] = sts[i]
            else:            
                self.h5Object[:, :] = sts
        elif  len(self.h5Object.shape) == 3 \
                and self.h5Object.dtype == "string":       
            sts = holder.cast(self.h5Object.dtype)
            if str(holder.format).split('.')[-1] == "VERTEX":
                for i in range(len(sts)):
                    for j in range(len(sts[i])):
                        for k in range(len(sts[i][j])):
                            self.h5Object[i, j, k] = sts[i][j][k] 
            if str(holder.format).split('.')[-1] == "IMAGE":
                for i in range(len(sts)):
                    for j in range(len(sts[i])):
                        self.h5Object[i, j, :] = sts[i][j] 
            elif str(holder.format).split('.')[-1] == "SPECTRUM":
                for i in range(len(sts)):
                    self.h5Object[i, :, :] = sts[i]
            else:            
                self.h5Object[:, :, :] = sts
        else:
            try:
                self.h5Object.write(holder.cast(self.h5Object.dtype))
            except:    
                if Streams.log_error:
                    print >> Streams.log_error, \
                        "EField::__writedata() - "\
                        "Storing two-dimension single fields "\
                        "not supported by pniio"
                raise Exception("Storing two-dimension single fields"\
                                    " not supported by pniio")


    ## writes growing scalar data
    # \param holder data holder
    def __writeScalarGrowingData(self, holder):
            
        arr = holder.cast(self.h5Object.dtype)
        if len(self.h5Object.shape) == 1:
            print "arr", arr, type(arr)
            print "h5", self.h5Object[self.h5Object.shape[0]-1], self.h5Object.shape, self.h5Object.shape[0]-1
            self.h5Object[self.h5Object.shape[0]-1] = arr
            print "h52", self.h5Object[self.h5Object.shape[0]-1], self.h5Object.shape, self.h5Object.shape[0]-1
        elif  len(self.h5Object.shape) == 2:
            if self.grows == 2:
                self.h5Object[:, self.h5Object.shape[0]-1] = arr
            else:
                self.h5Object[self.h5Object.shape[0]-1, :] = arr
        elif  len(self.h5Object.shape) == 3:
            if self.grows == 3:
                self.h5Object[:, :, self.h5Object.shape[0]-1] = arr
            if self.grows == 2:
                self.h5Object[:, self.h5Object.shape[0]-1, :] = arr
            else:
                self.h5Object[self.h5Object.shape[0]-1, :, :] = arr


    ## writes growing spectrum data
    # \param holder data holder
    def __writeSpectrumGrowingData(self, holder):

        # way around for a bug in pniio
        arr = holder.cast(self.h5Object.dtype)
        if self.grows == 1:
            if isinstance(arr, numpy.ndarray) \
                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                if len(self.h5Object.shape) == 2 \
                        and self.h5Object.shape[1] == 1:
                    self.h5Object[self.h5Object.shape[0]-1, :] = arr
                if len(self.h5Object.shape) == 2:
                    self.h5Object[self.h5Object.shape[0]-1, :] = arr
                else:                      
                    self.h5Object[self.h5Object.shape[0]-1] = arr
            else:
                if len(self.h5Object.shape) == 3:
                    self.h5Object[self.h5Object.shape[0]-1, :, :] = arr
                elif  len(self.h5Object.shape) == 2:
                    self.h5Object[self.h5Object.shape[0]-1, :] = arr
                else:
                    if hasattr(arr,"__iter__") and type(arr).__name__!= 'str' \
                            and len(arr) == 1:
                        self.h5Object[self.h5Object.shape[0]-1] = arr[0]
                    else:
                        self.h5Object[self.h5Object.shape[0]-1] = arr

        else:
            if isinstance(arr, numpy.ndarray) \
                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                self.h5Object[:, self.h5Object.shape[1]-1] = arr
            else:
                if len(self.h5Object.shape) == 3: 
                    if self.grows == 2:
                        self.h5Object[:, self.h5Object.shape[1]-1, :] = arr
                    else:
                        self.h5Object[:, :, self.h5Object.shape[2]-1] = arr
                else:
                    self.h5Object[:, self.h5Object.shape[1]-1] = arr


    ## writes growing spectrum data
    # \param holder data holder
    def __writeImageGrowingData(self, holder):

        arr = holder.cast(self.h5Object.dtype)
        if self.grows == 1:
            if len(self.h5Object.shape) == 3:
                self.h5Object[self.h5Object.shape[0]-1, :, :] = arr
            elif len(self.h5Object.shape) == 2:
                if len(holder.shape) == 1 :
                    self.h5Object[self.h5Object.shape[0]-1, :] = arr[0]
                elif len(holder.shape) > 1  and holder.shape[0] == 1:
                    self.h5Object[self.h5Object.shape[0]-1, :] \
                        = [c[0] for c in arr]
                elif len(holder.shape) > 1  and holder.shape[1] == 1:
                    self.h5Object[self.h5Object.shape[0]-1, :] = arr[:, 0]
            elif len(self.h5Object.shape) == 2:
                self.h5Object[self.h5Object.shape[0]-1, :] = arr[0]
            elif len(self.h5Object.shape) == 1:
                self.h5Object[self.h5Object.shape[0]-1] = arr[0][0]
        elif self.grows == 2:
            if len(self.h5Object.shape) == 3:
                self.h5Object[:, self.h5Object.shape[1]-1, :] = arr
            elif len(self.h5Object.shape) == 2:
                self.h5Object[:, self.h5Object.shape[1]-1] = arr[0]
        else:
            self.h5Object[:, :, self.h5Object.shape[2]-1] = arr        



    ## writes growing data
    # \param holder data holder
    def __writeGrowingData(self, holder):
        if str(holder.format).split('.')[-1] == "SCALAR":
            self.__writeScalarGrowingData(holder)
        elif str(holder.format).split('.')[-1] == "SPECTRUM":
            self.__writeSpectrumGrowingData(holder)
        elif str(holder.format).split('.')[-1] == "IMAGE":
            self.__writeImageGrowingData(holder)
        else:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "Case with %s format not supported "% \
                    str(holder.format).split('.')[-1] 
            raise XMLSettingSyntaxError, \
                "Case with %s  format not supported " % \
                str(holder.format).split('.')[-1]

    ## grows the h5 field    
    # \brief Ir runs the grow command of h5Object with grows-1 parameter
    def __grow(self):
        if self.grows and self.grows > 0 and hasattr(self.h5Object, "grow"):
            self.h5Object.grow(self.grows-1)
                

    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        try:
            if self.source:
                self.__grow()
                dt = self.source.getData()
                dh = None
                if dt:
                    dh = DataHolder(**dt)
                if not dh:
                    message = self.setMessage("Data without value")
                    self.error = message
                elif not hasattr(self.h5Object,'shape'):
                    message = self.setMessage("PNI Object not created")
                    self.error = message
                else:
                    if not self.__extraD:
                        self.__writeData(dh)
                    else:
                        self.__writeGrowingData(dh)
        except:
            info = sys.exc_info()
            import traceback
            message = self.setMessage(
                str(info[1].__str__()) +"\n "+ (" ").join(
                    traceback.format_tb(sys.exc_info()[2]) ))
#            message = self.setMessage(  sys.exc_info()[1].__str__()  )
            del info
            print >> sys.stderr, "EField::run() - %s\n %s " % \
                (message[0],message[1])
            self.error = message

#            self.error = sys.exc_info()
        finally:
            if self.error:
                if self.canfail:
                    if Streams.log_warn:
                        print >> Streams.log_warn, \
                            "EField::run() - %s  " % str(self.error)
                else:
                    if Streams.log_error:
                        print >> Streams.log_error, \
                            "EField::run() - %s  " % str(self.error)
                print >> sys.stderr, "EField::run() - ERROR", \
                    str(self.error)


    ## fills object with maximum value            
    # \brief It fills object or an extend part of object by default value 
    def __fillMax(self):
        shape = list(self.h5Object.shape)
        nptype = self.h5Object.dtype
        value = ''

        if self.grows:
            shape.pop(self.grows-1)
            
        if nptype == "bool":
            value = False
        elif nptype != "string":
            try:
                value = numpy.iinfo(getattr(numpy, nptype)).max
            except:
                try:
                    value = numpy.asscalar(
                        numpy.finfo(getattr(numpy, nptype)).max)
                except:    
                    value = 0
        else:
            nptype = "str"

            
        dformat = 'SCALAR'
        if shape and  len(shape) > 0  and shape[0] >= 1:
            arr = numpy.empty(shape, dtype=nptype)
            arr.fill(value)
            if len(shape) == 1:
                dformat = 'SPECTRUM'
            else:
                dformat = 'IMAGE'
        else:
            arr = value

        dh = DataHolder(dformat, arr, NTP.npTt[self.h5Object.dtype], shape)    
        
        
        if not self.__extraD:
            self.__writeData(dh)
        else:
            self.__writeGrowingData(dh)

            


    ## marks the field as failed
    # \brief It marks the field as failed            
    def markFailed(self):          
        if self.h5Object:
            self.h5Object.attr("nexdatas_canfail","string").value = "FAILED"
            if Streams.log_info:
                print >> Streams.log_info, \
                    "EField::markFailed() - %s marked as failed" % \
                    (self.h5Object.name) 
            self.__fillMax()
    
