# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

from flowData import Status;
from collections import OrderedDict;

class GoogleDBView(object):
    '''
    Maintains local view of the database and handles events.
    '''

    def __init__(self, database, tablename, flowname, rolename, stepname, flowDataClass):
        self.database = database;
        self.tablename = tablename;
        self.flowname = flowname;
        self.rolename = rolename;
        self.stepname = stepname;
        self.flowDataClass = flowDataClass;
        self.table = None;
        self.listeners = [];
        self.status = [];
        self.rows = {};

# PUBLIC:
                  
    def register(self, listener, status=None): 
        print "Registering listener on " + self.rolename + ":" + self.tablename;
        self.listeners.append(listener);
        self.status.append(status);
        # Fire anything that has already been seen:
        upd = self.restrict(self.rows.values(), status);
        if len(upd) > 0:
            listener(upd);
        
    def update(self):
        ''' update the view and fire any events '''
        table = self.get_table();
        if table == None:
            return;
        updated = [];
        results = table.FindRecords('');
        # TODO: use getNext
        for result in results:
            dbData = self.create_flow_data(result);
            if dbData == None:
                continue;
            cacheData = None;
            if dbData.uid in self.rows:
                cacheData = self.rows[dbData.uid];
            if not dbData == cacheData:
                self.rows[dbData.uid] = dbData;
                updated.append(dbData);
        if len(updated) > 0:
            self.fire_updates(updated);

# PRIVATE:

    def create_flow_data(self, result):
        #Hack to attempt to prevent race conditions:
        if 'status' not in result.content:
            return None;        
        status = result.content['status'];
        status = Status.__dict__[status]; #Convert to numeric
        sequence = (int)(result.content['sequence']);
        if 'parents' in result.content and result.content['parents'] != "" and result.content['parents']!=None:
            parents = result.content['parents'].split(",");
        else:
            parents = None;
        data = OrderedDict();
        for field in self.table.fields:
            if field != 'status' and field != 'sequence' and field != 'parents':
                data[field] = result.content[field];
        uid = result.row_id;
        return self.flowDataClass(self.flowname, self.rolename, self.stepname, data, sequence, status, uid, parents);
    
    def fire_updates(self, updated):
        for listener, status in zip(self.listeners, self.status):
            upd = self.restrict(updated, status);
            if len(upd) > 0:
                listener(upd);

    def restrict(self, updated, status):
        if status == None:
            return updated;
        ret = [];
        for r in updated:
            if r.status == status:
                ret.append(r);
        return ret;

    def get_table(self):
        if self.table != None:
            return self.table;
        ts = self.database.GetTables(name=self.tablename);
        if len(ts) == 1:
            ts[0].LookupFields();
            #Hack to attempt to remove race conditions:
            if 'status' not in ts[0].fields:
                return;
            self.table = ts[0];
        return self.table;
