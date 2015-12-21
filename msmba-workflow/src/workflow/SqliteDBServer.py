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
import sqlite3
from contextlib import closing

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
        self.db = {} # Flowname to DB Connection
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
    
    def stop_server(self, join=False):
        ''' Stop the server.  (Note: available over the network)
            if join==True, then we join against the server thread to block until shutdown
        '''
        self.server.shutdown()
        self.server.server_close()
        for db in self.db.values():
            # Note: anything happening right now will be lost... (No commit)
            db.close()        
        if join:
            self.thread.join()

    def ensure_database_exists(self, flowname):
        ''' Make sure a database for the given flowname exists. '''
        if not flowname in self.db:
            self.db[flowname] = sqlite3.connect(flowname+".db") 
            print "Opened DB file: " + flowname + ".db"
    
    def get_table_references(self, flowname):
        ''' Get all the table references in the DB. '''
        ret = set();
        with closing(self.db[flowname].cursor()) as c:
            # We can get all the table names with following SQL:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            for r in c.fetchall():
                ref = self._get_tableref(r.name);
                if ref != None:
                    ret.add(ref);
        return ret;
    
    def ensure_table_exists(self, flowname, tableref):
        """ Ensure the table exists in the DB """
        with closing(self.db[flowname].cursor()) as c:
            tablename = self._get_tablename(tableref)
            c.execute("CREATE TABLE IF NOT EXISTS ? ();", tablename)
            c.commit()
            print "Added table: " + tablename
            
    def ensure_all_fields_present(self, flowname, tableref, fieldnames):
        """ Update the table so that it definitely includes all the columns provided.
            Returns: the current set of field (column) names.
        """
        fieldnames = set(fieldnames)
        with closing(self.db[flowname].cursor()) as c:
            # First get the existing names
            tablename = self._get_tablename(tableref)
            c.execute("PRAGMA table_info(?);", tablename)
            columns = set([r.name for r in c.fetchall()])
            # Now any names not already present need to be added:
            toadd =  fieldnames.difference(columns)
            for field in toadd:
                c.execute("'ALTER TABLE ? ADD COLUMN ?;", tablename, field)
            c.commit()
            print "Added columns: " + ", ".join(toadd)
        return columns.union(toadd)

    def add_table_row(self, flowname, flowData):
        """ Add the given row to the db """
        pass

    def update_table_row(self, flowname, tableref, uid, column, value):
        """ Update the given row/column in the DB """
        pass

    def get_records(self, flowname, tableref):
        """ Get the records for the table """
        pass

# Private

    def _get_tablename(self, tableref):
        if tableref.flowDataCls == Task:
            tablename = "T_" + tableref.stepname + "_" + tableref.rolename;
        elif tableref.flowDataCls == Result:
            tablename = "R_" + tableref.stepname + "_" + tableref.rolename;
        else:
            raise Exception("Unknown flowData: " + str(tableref.flowDataCls));
        return tablename
    
    def _get_tableref(self, string):
        s = string.split("_");
        if s[0] == "R":
            flowDataCls = Result;
        elif s[0] == "T":
            flowDataCls = Task;
        else:
            return None;
        return TableReference(rolename=s[2], stepname=s[1], flowDataCls=flowDataCls);
    
class _ServerThread(Thread):
    ''' Super simple thread that will execute the server'''
    def __init__(self, server):
        self.server = server
    def run(self):
        self.server.serve_forever() # Internal server loop that handles requests
        