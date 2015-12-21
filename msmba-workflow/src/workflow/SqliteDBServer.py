# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

import sys
from threading import Thread
from SimpleXMLRPCServer import SimpleXMLRPCServer

from flowData import Status
from task import Task
from result import Result
from SqliteDBUtils import TableReference, get_serverparams

class SqliteDBServer(object):
    '''
    Presently a pretty thin wrapper around SQLite.  
    
    All public methods of this class are made available over the network.
    '''
    
    def __init__(self):
        serverparams = get_serverparams()
        sys.stdout.write("Starting Server... ")
        # We always start the server on localhost at the given port.
        self.server = SimpleXMLRPCServer(("localhost", int(serverparams.port)))
        # All public methods of this class are registered
        self.server.register_instance(self) 
        # Create a thread to handle the requests
        self.thread = _ServerThread(self.server)
        self.thread.start()
        print "done."
        
# Public
    
    def stop_server(self, join=True):
        ''' Stop the server.  (Note: available over the network)
            if join==True, then we join against the server thread to block until shutdown
        '''
        self.server.shutdown()
        self.server.server_close()
        if join:
            self.thread.join()

# Private

    def _get_tablename(self, rolename, stepname, flowDataCls):
        if flowDataCls == Task:
            tablename = self._get_task_tablename(rolename, stepname);
        elif flowDataCls == Result:
            tablename = self.get_result_tablename(rolename, stepname)
        else:
            raise Exception("Unknown flowData: " + str(flowDataCls));
        return tablename
    
    
class _ServerThread(Thread):
    ''' Super simple thread that will execute the server'''
    def __init__(self, server):
        self.server = server
    def run(self):
        self.server.serve_forever() # Internal server loop that handles requests
        