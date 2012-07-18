#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \file ElementThread.py
# ElementThread

from threading import *                                                                       
import Queue
import thread
import time


## Single Thread Element
class ElementThread(Thread):
    ## constructor
    # \brief It creates ElementThread from the runnable element
    # \param index the current thread index
    # \param queue queue with tasks
    def __init__(self, index, queue):
        Thread.__init__(self)
        ## thread index
        self.index = index
        ## queue with runnable elements
        self._queue = queue
        ## lock for safe printing messeges
        self._safeprint = thread.allocate_lock()

    ## runner
    # \brief It runs the defined thread
    def run(self):
        with self._safeprint:
            print "Running THREAD: %s" % self.index
        full = True    
        while full:
            time.sleep(0.0001)
            try:
                elem = self._queue.get(block=False)
                if hasattr(elem, "run") and callable(elem.run):
                    elem.run()
                    
            except Queue.Empty:
                full = False    
                pass
                


