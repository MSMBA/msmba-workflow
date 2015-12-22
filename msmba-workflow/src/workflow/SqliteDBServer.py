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
from collections import OrderedDict;
from xmlrpclib import Binary
import cPickle as pickle


from flowData import Status, FlowDataReference;
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
        serverparams = get_serverparams(alwayslocalhost=True)
        sys.stdout.write("Starting Server... ")
        self.server = self._create_server(serverparams)
        # Create a thread to handle the requests
        self.thread = _ServerThread(self.server.xmlserver)
        self.thread.start()
        print "done."
        
# Public
    
    def stop_server(self, join=False):
        ''' Stop the server.  (Note: available over the network)
            if join==True, then we join against the server thread to block until shutdown
        '''
        sys.stdout.write("Stopping server... ")
        self.server.shutdown()
        self.server.server_close()
        for db in self.db.values():
            # Note: anything happening right now will be lost... (No commit)
            db.close()        
        if join:
            self.thread.join()
        print "done."

    def ensure_database_exists(self, flowname):
        ''' Make sure a database for the given flowname exists. '''
        if not flowname in self.db:
            self.db[flowname] = sqlite3.connect(flowname+".db") 
            print "Opened DB file: " + flowname + ".db"
    
    def get_table_references(self, flowname):
        ''' Get all the table references in the DB. '''
        sys.stdout.write("Getting all tables... ")
        ret = set();
        with closing(self.db[flowname].cursor()) as c:
            # We can get all the table names with following SQL:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            for r in c.fetchall():
                ref = self._get_tableref(r.name);
                if ref != None:
                    ret.add(ref);
        print "done."
        return ret;
    
    def ensure_table_exists(self, flowname, tableref):
        """ Ensure the table exists in the DB """
        sys.stdout.write('Ensuring existence of ' + str(tableref) + "... ")
        with closing(self.db[flowname].cursor()) as c:
            tablename = self._get_tablename(tableref)
            # Can't do tablename with parameter...
            c.execute("CREATE TABLE IF NOT EXISTS "+tablename+"(sequence INT, status INT);") 
            self.db[flowname].commit()
        print "done."
                    
    def ensure_all_fields_present(self, flowname, tableref, fieldnames):
        """ Update the table so that it definitely includes all the columns provided.
            Returns: the current set of field (column) names.
        """
        sys.stdout.write('Ensuring existence of columns in' + tableref + "... ")
        fieldnames = set(fieldnames)
        with closing(self.db[flowname].cursor()) as c:
            # First get the existing names
            tablename = self._get_tablename(tableref)
            c.execute("PRAGMA table_info(?);", (tablename,))
            columns = set([r.name for r in c.fetchall()])
            # Now any names not already present need to be added:
            toadd =  fieldnames.difference(columns)
            for field in toadd:
                c.execute("'ALTER TABLE ? ADD COLUMN ?;", (tablename, field))
            c.commit()
            if len(toadd) > 0:
                print "Added columns: " + ", ".join(toadd)
            else:
                print "done."
        return columns.union(toadd)

    def add_table_row(self, flowname, flowData):
        """ Add the given row to the db """
        tableref = self._get_tableref_for_data(flowData)
        tablename = self._get_tablename(tableref)
        sys.stdout.write('Adding to ' + tableref + ": " +  str(flowData.sequence) + "." + str(flowData.uid) + "... ");
        # First build up a dictionary of the values:
        row = OrderedDict(flowData.data);
        row['status'] = Status.reverse_mapping[flowData.status];
        if flowData.sequence == None:
            flowData.sequence = self._get_new_sequence(flowname, tableref);
        row['sequence'] = flowData.sequence;
        if flowData.parents == None:
            row['parents'] = "";
        else:
            row['parents'] = ",".join([FlowDataReference.to_string(p) for p in flowData.parents]);
        # Now run the insert:
        with closing(self.db[flowname].cursor()) as c:
            # Just build with some strings to make it easier, if not as secure...
            columns = ",".join(row.keys())
            slots = ",".join(["?"]*len(columns)) # Make comma separated '?'
            c.execute("INSERT INTO " + tablename + " (" + columns + ") VALUES (" + slots + ");", row.values())
            c.commit()
        print "done.";

    def update_table_row(self, flowname, tableref, uid, column, value):
        """ Update the given row/column in the DB """
        sys.stdout.write('Updating ' + tableref + " (" +  str(uid) + ") " + column + "<-" + str(value) + "... ")
        tablename = self._get_tablename(tableref)
        with closing(self.db[flowname].cursor()) as c:
            c.execute("UPDATE ? SET ? = ? where uid = ?;",(tablename, column, value, uid))
            c.commit()
        print "done."

    def get_records(self, flowname, tableref):
        """ Get the records for the table """
        sys.stdout.write('Getting rows for ' + tableref + "... ")
        tablename = self._get_tablename(tableref)
        ret = []
        with closing(self.db[flowname].cursor()) as c:
            c.execute("select rowid, * from ?;",(tablename, ))
            for r in c.fetchall():
                data = self.create_flow_data(flowname, tableref, r)
                if data != None:
                    ret.append(data)
        print "done."
        return ret

# Private

    def _get_new_sequence(self, flowname, tableref):
        sys.stdout.write('Obtain new sequence for ' + tableref + "... ")
        with closing(self.db[flowname].cursor()) as c:
            tablename = self._get_tablename(tableref)
            c.execute("SELECT sequence FROM ? ORDER BY sequence DESC LIMIT 1;", (tablename,))
            seq = c.fetchone()
            if seq == None:
                nseq = 1
            else:
                nseq = seq + 1
        print "done."
        return nseq

    def create_flow_data(self, flowname, tableref, result):
        #Hack to attempt to prevent race conditions:
        if 'status' not in result:
            return None;        
        status = result['status'];
        status = Status.__dict__[status]; #Convert to numeric
        sequence = (int)(result['sequence']);
        if 'parents' in result and result['parents'] != "" and result['parents']!=None:
            parents = result['parents'].split(",");
        else:
            parents = None;
        data = OrderedDict();
        for field in result:
            if field != 'status' and field != 'sequence' and field != 'parents':
                data[field] = result[field];
        uid = result['rowid'];
        return tableref.flowDataCls(flowname, tableref.rolename, tableref.stepname, data, sequence, status, uid, parents);

    def _get_tableref_for_data(self, flowData):
        return TableReference(rolename=flowData.rolename, stepname=flowData.stepname, flowDataCls=flowData.__class__);

    def _get_tablename(self, tableref):
        if tableref.flowDataCls == Task:
            tablename = "T_" + tableref.stepname + "_" + tableref.rolename;
        elif tableref.flowDataCls == Result:
            tablename = "R_" + tableref.stepname + "_" + tableref.rolename;
        else:
            raise Exception("Unknown flowData: " + str(tableref.flowDataCls));
        return tablename
    
    def _get_tableref(self, tablename):
        s = tablename.split("_");
        if s[0] == "R":
            flowDataCls = Result;
        elif s[0] == "T":
            flowDataCls = Task;
        else:
            return None;
        return TableReference(rolename=s[2], stepname=s[1], flowDataCls=flowDataCls);
    
    def _create_server(self, serverparams):
        # We create a wrapper that is a proxy to the server.  We need to do this because we use
        # XMLRPC which we use does not support user-defined classes, so we need to do our own
        # Marshalling via Pickle.

        # Note: self will be the instance to call the members of.
        class ServerWrapper(object):
            ''' A wrapper for the server that handles pickling.  By default just dispatches
                to the server.  But if you need to pickle, define a function explicitly here.
            '''
            def __init__(self, serverparams, instance):
                # We always start the server on localhost at the given port.
                self.xmlserver = SimpleXMLRPCServer((serverparams.address, serverparams.port),\
                                                    allow_none=True,\
                                                    logRequests=False)
                # All public methods of this class are registered
                self.xmlserver.register_instance(self) 
                self.instance = instance
            
            def __getattr__(self, attr):
                # This only gets called for attributes that haven't been defined.
                # If this happens, try to get the attribute from the xmlproxy instead.
                if hasattr(self.instance, attr):
                    return getattr(self.instance, attr)
                else:
                    # If its not defined either in this class, or in the proxy class, then its an error
                    raise AttributeError(attr)
                
            @staticmethod
            def to_bin(obj):
                return Binary(pickle.dumps(obj))

            @staticmethod
            def from_bin(bin):
                return pickle.loads(bin.data)
        
            # Define any methods that need marshalling/unmarshelling here.
            
            def ensure_table_exists(self, flowname, BINtableref):
                self.instance.ensure_table_exists(flowname, self.from_bin(BINtableref))
            
        return ServerWrapper(serverparams, self) #The SqliteDBServer will be the instance to delegate to

        

    
class _ServerThread(Thread):
    ''' Super simple thread that will execute the server'''
    def __init__(self, server):
        Thread.__init__(self)
        self.server = server
    def run(self):
        self.server.serve_forever() # Internal server loop that handles requests
        