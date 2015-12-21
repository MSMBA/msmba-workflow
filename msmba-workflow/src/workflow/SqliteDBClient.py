# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

import sys
from xmlrpclib import ServerProxy
import traceback;

from flowData import Status
from task import Task
from result import Result
from joinedListener import JoinedListener
from allTableListener import AllTableListener
from SqliteDBUtils import TableReference, get_serverparams

class SqliteDBClient(object):
    '''
    Manages storing the workflow data in the database.
    This is a db client that sits in every process.
    Communication is by XMLRPC
    '''
    
    ''' How many poll cycles to do before checking for all tables.'''
    ALL_TABLE_POLL_CYCLES = 1

    def __init__(self, flowname):
        """ flowname is the database file backing this flow """
        self.flowname = flowname
        serverparams = get_serverparams()
        sys.stdout.write("Connecting to server... ")
        self.rpcclient = self._create_client(serverparams)
        print "Login Complete."
        self.rpcclient.ensure_database(self.flowname)
        self.tables = {} # TableReference -> _TableView
        self.all_table_listeners = []
        self.poll_count = 0
        
# PUBLIC
    
    def add(self, flowData):
        table = self._get_table_flowdata(flowData)
        table.add_row(flowData)
        
    def update_status(self, flowData, status):
        table = self._get_table_flowdata(flowData)
        table.update_row(flowData.uid, "status", Status.reverse_mapping[status])

    def register_result_listener(self, rolename, stepname, listener, status=None):
        self.register_listener(rolename, stepname, Result, listener, status)

    def register_task_listener(self, rolename, stepname, listener, status=None):
        self.register_listener(rolename, stepname, Task, listener, status)

    def register_listener(self, rolename, stepname, flowDataCls, listener, status=None):
        tableref = TableReference(rolename, stepname, flowDataCls)
        table = self._get_table(tableref)
        table.register(listener, status)
        
    def register_joined_listener(self, listenlist, predicate, listener):
        '''
        Listen to one or more result tables, and fires when predicate says so.  
        Note: bins by 'sequence' field you only get results associated with the same sequence number 
        Arguments:
        listenlist: a list of tuples, each of the form (rolename, stepname, flowDataCls, status) to listen to.  FlowDataCls is Task or Result, If omitted, status defaults to Status.NEW
        predicate: a function, that takes a set of results obtained so far.  return True iff the set is complete and the event should fire.
        listener: the function to fire.  it takes a list of the results.
        '''
        JoinedListener(self, listenlist, predicate, listener)
        
    def register_all_table_listener(self, listener, status=None):
        ''' register a listener on all the tables. '''
        self.all_table_listeners.append(AllTableListener(self, listener, status))

# Private

    def _create_client(self, serverparams):
        ''' Connect tot he server. '''
        url = "http://"+serverparams.address + ":" + str(serverparams.port)
        return ServerProxy(url)

    def _get_table_flowdata(self, flowData):
        ''' Get the _Table that would store the given object'''
        if flowData.flowname != self.flowname:
            raise Exception("Mismatched flow names: " + flowData.flowname)
        tableref = TableReference(flowData.rolename, flowData.stepname, flowData.__class__)
        table = self._get_table(tableref)
        table.check_columns(flowData.data.keys())
        return table

    def _get_table(self, tableref):
        ''' Get the table for the given reference '''
        if tableref not in self.tables:
            self.tables[tableref] = _TableView(self.rpcclient, self.flowname, tableref)
        table = self.tables[tableref]
        return table
        
    def _get_table_references(self):
        ''' Get the table references -- all of them in the DB, not just the cache. '''
        self.rpcclient.get_table_references()
    
    def poll(self):
        ''' Call this in the worker thread periodically.  All callbacks will occur within this context.'''
        for table in self.tables.values():
            try:
                table.update();
            except Exception, e:
                print "Exception updating table: " + str(type(e)) + ": " + str(e);
                print traceback.format_exc();
        # Only do this every 5 polls:
        if self.poll_count%SqliteDBClient.ALL_TABLE_POLL_CYCLES==0:
            tablerefs = self._get_table_references();
            for listener in self.all_table_listeners:
                try:
                    listener.poll(tablerefs);
                except Exception, e:
                    print "Exception updating all table listener: " + str(type(e)) + ": " + str(e);
                    print traceback.format_exc();
        self.poll_count = self.poll_count+1;
    
        
class _TableView(object):
    """
    A View of a particular table in the database.
    - Caches the content locally
    - Maintains the ability to fire listeners against changes in this data
    
    """        
    def __init__(self, rpcclient, flowname, tableref):
        self.rpcclient = rpcclient
        self.flowname = flowname
        self.tableref = tableref
        self.listeners = [] # Tuples, (Status, Listener)
        self.rows = [] # FlowData subclass
        self.ensure_exists()
    
    def ensure_exists(self):
        """ Ensure the table exists in the DB """
        self.rpcclient.ensure_exists(self.flowname, self.tableref)
    
    def check_columns(self, fieldnames):
        """ Check that the columns are all present.  Can cache names so this is fast."""
        self.rpcclient.check_columns(self.flowname, self.tableref, fieldnames)
    
    def register(self, listener, status=None):
        """ Register a listener for the given status.  None means get all events"""
        self.listeners.append((status,listener))
        # Fire any existing rows against the listener:
        if status == None:
            updated = self.rows;
        else:
            updated= [];
            for r in self.rows:
                if r.status == status:
                    updated.append(r);
        if len(updated) > 0:
            listener(updated);
    
    def add_row(self, flowData):
        """ Add the given row to the table."""
        self.rpcclient.add_row(self.flowname, self.tableref, flowData)
    
    def update_row(self, uid, column, value):
        """ Update a given field in a given row."""
        self.rpcclient.update_row(uid, column, value)
