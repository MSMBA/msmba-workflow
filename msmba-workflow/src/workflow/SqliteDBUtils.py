# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

import os.path;
import ConfigParser;
from collections import namedtuple;

TableReference = namedtuple("TableReference", "rolename stepname flowDataCls") # Note flowDataCls is the CLASS not a String
ServerParams = namedtuple("ServerParams", "address port");

def get_serverparams():
    """ Get the address where the server is located"""
    serverparamfile = "server.cfg";
    if os.path.exists(serverparamfile):
        config = ConfigParser.RawConfigParser();
        config.read(serverparamfile);
        address = config.get("Server", "Address");
        port = config.get("Server", "Port");
    else:
        print("Please enter your backend server address...")
        address = raw_input("Enter hostname or ip address (Enter for default): ");
        if address == "":
            address = 'localhost';
        port = raw_input("Enter port (Enter for default): ");
        if port == "":
            port = 9000;
        config = ConfigParser.RawConfigParser();
        config.add_section("Server");
        config.set("Server", "Address", address);
        config.set("Server", "Port", port);
        with open(serverparamfile, 'wb') as cfile:
            config.write(cfile)        
    return ServerParams(address, port);
