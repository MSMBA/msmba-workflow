# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

import sys;
import os.path;
import ConfigParser;
from collections import OrderedDict;
from gdata.spreadsheet.text_db import DatabaseClient;
from gdata.spreadsheet.text_db import Record;
import gdata.spreadsheet;
from flowData import Status;
from flowData import FlowDataReference;
from googleDBView import GoogleDBView;
from result import Result;
from task import Task;
from googleJoinedListener import GoogleJoinedListener;
from collections import namedtuple;
from allTableListener import AllTableListener;
import traceback;
from util import convert_flowname_to_db;
from util import convert_rolename_to_db;
from util import convert_stepname_to_db;

TableReference = namedtuple("TableReference", "rolename stepname flowDataCls");

class GoogleDB(object):
    '''
    Manages storing the workflow data in the database.
    '''

    def __init__(self, flowname):
        """ name is the spreadsheet backing this flow """
        self.flowname = convert_flowname_to_db(flowname);
        username, password = self.get_credentials();
        sys.stdout.write("Logging into Google... ");
        self.client = DatabaseClient(username=username, password=password);
        print "Login Complete.";
        self.ensure_workflow_document();
        self.default_sheet_checked = False;
        self.tables = {};
        self.views = {};
        self.all_table_listeners = [];
        self.poll_count = 0;

# PUBLIC
    
    def add(self, flowData):
        # TODO: potential race condition here...  What happens if some other process has already added the same item?
        table = self.get_flowdata_table(flowData);
        self.add_row(table, flowData);
        self.check_for_delete_default_sheet();

    def update_status(self, flowData, status):
        table = self.get_flowdata_table(flowData);
        self.update_row(table, flowData.uid, "status", Status.reverse_mapping[status]);

    def register_result_listener(self, rolename, stepname, listener, status=None):
        self.register_listener(rolename, stepname, Result, listener, status);

    def register_task_listener(self, rolename, stepname, listener, status=None):
        self.register_listener(rolename, stepname, Task, listener, status);
        
    def register_listener(self, rolename, stepname, flowDataCls, listener, status=None):
        rolename = convert_rolename_to_db(rolename);
        stepname = convert_stepname_to_db(stepname);
        if flowDataCls == Task:
            tablename = self.get_task_tablename(rolename, stepname);
        elif flowDataCls == Result:
            tablename = self.get_result_tablename(rolename, stepname);
        else:
            raise Exception("Unkown flowData class " + str(flowDataCls));  
        if tablename not in self.views:
            self.views[tablename] = GoogleDBView(self.database, tablename, self.flowname, rolename, stepname, flowDataCls);
        self.views[tablename].register(listener, status);
        
        
    def register_joined_listener(self, listenlist, predicate, listener):
        '''
        Listen to one or more result tables, and fires when predicate says so.  
        Note: bins by 'sequence' field; you only get results associated with the same sequence number 
        Arguments:
        listenlist: a list of tuples, each of the form (rolename, stepname, flowDataCls, status) to listen to.  FlowDataCls is Task or Result, If omitted, status defaults to Status.NEW
        predicate: a function, that takes a set of results obtained so far.  return True iff the set is complete and the event should fire.
        listener: the function to fire.  it takes a list of the results.
        '''
        GoogleJoinedListener(self, listenlist, predicate, listener);
        
    def register_all_table_listener(self, listener, status=None):
        ''' register a listener on all the tables. '''
        self.all_table_listeners.append(AllTableListener(self, listener, status));
# PRIVATE

    def check_for_delete_default_sheet(self):
        '''
        Worksheets must have at least one sheet, and a default one is always created.  We check if we need to remove it.
        '''
        if self.default_sheet_checked == False:
            
            sys.stdout.write("Checking for default spreadsheet... ");
            t = self.database.GetTables(name="Sheet 1");
            if len(t) == 1:
                sys.stdout.write("Found it.  Removing it... ")
                t[0].Delete();
            print "Done.";
            self.default_sheet_checked = True;

    def get_flowdata_table(self, flowData):
        if flowData.flowname != self.flowname:
            raise Exception("Mismatched flow names: " + flowData.flowname);
        if flowData.__class__ == Task:
            tablename = self.get_task_tablename(flowData.rolename, flowData.stepname);
        elif flowData.__class__ == Result:
            tablename = self.get_result_tablename(flowData.rolename, flowData.stepname)
        else:
            raise Exception("Unknown flowData: " + str(flowData));
        table = self.get_table(tablename, flowData.data.keys());
        return table;

    def poll(self):
        ''' Call this in the worker thread periodically.  All callbacks will occur within this context.'''
        for view in self.views.values():
            try:
                view.update();
            except Exception, e:
                print "Exception updating view: " + str(type(e)) + ": " + str(e);
                print traceback.format_exc();
        # Only do this every 5 polls:
        if self.poll_count%5==0:
            tablerefs = self.get_table_references();
            for listener in self.all_table_listeners:
                try:
                    listener.poll(tablerefs);
                except Exception, e:
                    print "Exception updating all table listener: " + str(type(e)) + ": " + str(e);
                    print traceback.format_exc();
        self.poll_count = self.poll_count+1;

    def get_credentials(self):
        credentialfile = "credentials.cfg";
        if os.path.exists(credentialfile):
            config = ConfigParser.RawConfigParser();
            config.read(credentialfile);
            username = config.get("Credentials", "Username");
            if not username.endswith("@gmail.com"):
                username = username + "@gmail.com";
            password = config.get("Credentials", "Password");
        else:
            print("I don't have your TEAM Google Credentials.  Please Supply them...")
            username = raw_input("Enter TEAM username: ");
            password = raw_input("Enter TEAM password: ");

            if not username.endswith("@gmail.com"):
                username = username + "@gmail.com";
            
            config = ConfigParser.RawConfigParser();
            config.add_section("Credentials");
            config.set("Credentials", "Username", username);
            config.set("Credentials", "Password", password);
            with open(credentialfile, 'wb') as cfile:
                config.write(cfile)        
        return (username, password);
        
    def ensure_workflow_document(self):
        sys.stdout.write("Looking for " + self.flowname + " worksheet... ");
        databases = self.client.GetDatabases(name=self.flowname)
        if len(databases) == 0:
            #Add it:
            sys.stdout.write("\nNot present, adding it... ");
            self.database = self.client.CreateDatabase(self.flowname);
            print "Done.";
            return;
        if len(databases) > 1:
            raise Exception("Should only be one database called: " + self.flowname);
        # Get the one and only:
        print "Found it.";
        self.database = databases[0];

    def get_result_tablename(self, rolename, stepname):
        return "R_" + stepname + "_" + rolename;

    def get_task_tablename(self, rolename, stepname):
        return "T_" + stepname + "_" + rolename;

    def get_table_reference(self, string):
        s = string.split("_");
        if s[0] == "R":
            flowDataCls = Result;
        elif s[0] == "T":
            flowDataCls = Task;
        else:
            return None;
        return TableReference(rolename=s[2], stepname=s[1], flowDataCls=flowDataCls);

    def get_table_references(self):
        ret = set();
        tables = self.database.GetTables();
        for table in tables:
            name = table.name;
            ref = self.get_table_reference(name);
            if ref != None:
                ret.add(ref);
        return ret;

    def get_fieldnames(self, fieldnames):
        ret = OrderedDict();
        for k in fieldnames:
            ret[k]=None;
        ret['sequence']=None;
        ret['parents'] = None;
        ret['status']=None;
        return ret;

    def get_table(self, tablename, fieldnames):
        self.ensure_table(tablename, fieldnames);
        return self.tables[tablename];
    
    def ensure_table(self, tablename, fieldnames):  
        if tablename in self.tables:
            return;
        fieldnames = self.get_fieldnames(fieldnames);
        # First See if the table is there:
        sys.stdout.write("Checking for table " + tablename + "... ");
        ts = self.database.GetTables(name=tablename);
        if len(ts) > 1:
            raise Exception("Expected 0 or 1 spreadsheets named " + tablename + " but there are: " + len(ts));
        if len(ts) == 0:
            sys.stdout.write("\nTable not found, adding " + tablename + "... ");
            self.tables[tablename] = self.database.CreateTable(tablename, fieldnames)
            print "Done.";
            return;
        # TODO: ensure it has the right columns:
        ts[0].LookupFields();
        dbNotFields = set(ts[0].fields).difference(set(fieldnames));
        fieldsNotDB = set(fieldnames).difference(set(ts[0].fields));
        
        if len(fieldsNotDB) == 0:
            self.tables[tablename] = ts[0];
            if len(dbNotFields) == 0:
                print "Found table with matching fields.";
            else:
                print "Found table and using it, but it has EXTRA columns: (" + ", ".join(dbNotFields) + ").";
            return;
        else:
            sys.stdout.write("Table is missing columns (" + ", ".join(fieldsNotDB) + "), re-initializing it: ");
            # TODO: Should copy existing data.  For now, just delete.
            sys.stdout.write("Deleting... ");
            temp = self.database.CreateTable("Temp", ['Temp']); # Make sure we have at least one table, otherwise the delete fails.
            ts[0].Delete();
            sys.stdout.write("Done.  Creating... ");
            self.tables[tablename] = self.database.CreateTable(tablename, fieldnames)
            temp.Delete();#Get rid of the temporary table.
            print "Done.";

    def add_row(self, table, flowData):
        sys.stdout.write('Adding to ' + table.name + ": " +  str(flowData) + "... ");
        row = OrderedDict(flowData.data);
        row['status'] = Status.reverse_mapping[flowData.status];
        if flowData.sequence == None:
            flowData.sequence = self.get_new_sequence(table);
        row['sequence'] = flowData.sequence;
        if flowData.parents == None:
            row['parents'] = "";
        else:
            row['parents'] = ",".join([FlowDataReference.to_string(p) for p in flowData.parents]);
        row = self.stringify(row);
        table.AddRecord(row);
        print "Done.";
        
        
    def update_row(self, table, uid, field, value):
        if uid == None:
            raise Exception("Empty uid!");
        record = table.GetRecord(row_id = uid);
        record.content[field] = value;
        sys.stdout.write("Setting " + table.name + ":" + uid + "." + field + " = " + value + "... ");
        record.Push();
        print "Done.";
        
    def get_new_sequence(self, table):
        records = FindRecords(table, "", orderby="sequence", reverse=True, limit=1);
        if len(records) == 0:
            return 1;
        record = records[0];
        seq = (int)(record.content['sequence']) + 1;
        print "Determined new sequence number: " + str(seq);
        return seq;
        
    def stringify(self, dictionary):
        ret = OrderedDict()
        for key, value in dictionary.items():
            ret[str(key)] = str(value);
        return ret;       
        
def FindRecords(table, query_string, orderby=None, reverse=False, limit=None):
    """
    Create a version of FindRecords that orders and reverses and has a limit function.
    """
    row_query = gdata.spreadsheet.service.ListQuery()
    if query_string != "":
        row_query.sq = query_string
    if orderby:
        row_query.orderby = orderby;
    if reverse:
        row_query.reverse = 'true';
    matching_feed = table.client._GetSpreadsheetsClient().GetListFeed(
        table.spreadsheet_key, wksht_id=table.worksheet_id, query=row_query)
    return LimitedRecordResultSet(matching_feed, table.client, 
        table.spreadsheet_key, table.worksheet_id, limit)

class LimitedRecordResultSet(list):

    def __init__(self, feed, client, spreadsheet_key, worksheet_id, limit=None):
        self.client = client
        self.spreadsheet_key = spreadsheet_key
        self.worksheet_id = worksheet_id
        self.feed = feed
        list(self)
        rec=0;
        for entry in self.feed.entry:
            rec=rec+1;
            self.append(Record(content=None, row_entry=entry, 
                spreadsheet_key=spreadsheet_key, worksheet_id=worksheet_id,
                database_client=client))
            if rec >= limit:
                self.feed = None;
                break;
        if limit == None:
            self.limit = None;
        else:
            self.limit = limit - rec;
    
    def GetNext(self):
        next_link = self.feed.GetNextLink()
        if next_link and next_link.href:
            new_feed = self.client._GetSpreadsheetsClient().Get(next_link.href, 
                converter=gdata.spreadsheet.SpreadsheetsListFeedFromString)
            return LimitedRecordResultSet(new_feed, self.client, self.spreadsheet_key,
                self.worksheet_id, self.limit)
