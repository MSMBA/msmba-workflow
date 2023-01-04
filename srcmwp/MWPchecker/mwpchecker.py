'''
This program does some basic analysis and reporting on a MWP workflow
in order to assist with debugging.
'''
import glob     # allows pattern matching for lists of files
import os.path  # manipulate file pathnames
import re       # regular expressions
import ConfigParser # to store settings for the checker

def build_dir_path(target_dir):
    '''
    create proper path to top level folder
    by prepending ../
    
    at the moment there is no error checking
    '''
    return '../%s/' % target_dir
    
def get_directory():
    '''
    prompt user for directory to target for check.
    assume directory is top level in workflow project
    so we prepend ../ when returning it.
    
    store latest answer in .cfg file and use it for default later
    '''
    configfile = "MWPchecker.cfg"
    
    # read existing config file
    if os.path.exists(configfile):
        config = ConfigParser.RawConfigParser()
        config.read(configfile)
        default_dir = config.get("Basics", "TargetDirectory")
    # else make new config file
    else:
        config = ConfigParser.RawConfigParser()
        config.add_section("Basics")
        default_dir = ''

    # prompt user for config with default
    basic_prompt = 'Please specify name of folder to check'
    if default_dir == '':
        dir_prompt = basic_prompt + ":  "
    else:
        dir_prompt = basic_prompt + (' [Press enter for "%s"]:  ' % default_dir)
    getting_prompt = True
    while getting_prompt:
        target_dir = raw_input(dir_prompt)
        if not target_dir:
            target_dir = default_dir
        if os.path.exists(build_dir_path(target_dir)):
            getting_prompt = False
        else:
            print "Could not find that directory.  Please try again."
    
    # save latest choice of directory 
    print "\n"
    config.set("Basics","TargetDirectory", target_dir)
    with open(configfile, 'wb') as cfile:
        config.write(cfile) 
           
    return build_dir_path(target_dir)
    
def file_read(target):
    '''
    open target, and return its contents as a string, then close it.
    this is not scalable but will work for our purposes
    '''
    f_handle = open(target, "r")
    data = f_handle.read()
    f_handle.close()
    return data

def MWPtype(content):
    '''
    look in content to see if we have a subclass of Backend or RoleApplication
    and then return type of backend or frontend accordingly.  if neither found,
    then type is none
    '''
    file_type = 'None'
    if re.search(r'class .*\(Backend\):',content):
        file_type = 'backend'
    if re.search(r'class .*\(RoleApplication\):',content):
        file_type = 'frontend'
    return file_type

def get_flow(MWPtype,content):
    '''
    return flow name for backend or frontend.  None if not found.
    '''
    if MWPtype == 'frontend':
        match = re.search(r'super\(.*, *self\).__init__\( *(.*) *,',content)
        if match:
            return match.group(1) # return the captured flow name
        else:
            return 'None' # there was no match, so no flow
    elif MWPtype == 'backend':
        match = re.search(r'Backend\.__init__\( *self, *(.*) *,',content)
        if match:
            return match.group(1) # return the captured flow name
        else:
            return 'None' # there was no match, so no flow
    else:
        return 'None'

def get_task_lines(MWPtype, content):
    '''
    given contents of a file, returns a list of all lines of code
    related to tasks.  for backend this will be from the wired() 
    method.  for frontend this will be from __init__
    '''
    if MWPtype == 'backend':
        return re.findall(r'self\.register_.+_listener\( *.* *, *.* *, *self\..* *\)',content)
    elif MWPtype == 'frontend':
        return re.findall(r'self\.register_.+_step\( *.* *, *self\..* *\)',content)
    else:
        return []

def get_methods(content):
    '''
    intent is to return name of all methods (for backend) other than __init__ and wire
    what it actually does is return all methods that take a parameter other than self. 
    '''
    handlers = re.findall(r'def *(.*)\( *self *, *.*\):',content)
    return handlers

def get_frontend_role(content):
    '''
    gets role from super() call in frontend init
    '''
    match = re.search(r'super\(.*, *self\).__init__\( *.* *, *(.*) *\)',content)
    if match:
        return match.group(1) # return the captured flow name
    else:
        return 'None' # there was no match, so no flow

def get_method_dict(content):
    '''
    takes as input some source code
    and returns a dictionary where each method name is a key whose value is its code
    
    assumes a typical frontend or backend file format
    
    assumes that the very first thing in the file is NOT a method declaration and thus the 
    first item in the list we get when we split on method names is thrown away
    
    the last method in the list will include all the non-method code at the bottom of the
    file, which is not a problem for our purposes
    '''
    method_list = re.split(r'[ \t]*def (.*)\(.*\):', content)
    del method_list[0]
    return dict(zip(*[iter(method_list)]*2)) #  very clever bit of code:  http://stackoverflow.com/questions/6900955/python-convert-list-to-dictionary


class MWPtask():
    '''
    task information from backend and frontend.
    '''
    def __init__(self, MWPfile, register_line):
        self.MWPtype = MWPfile.MWPtype
        
        if self.MWPtype == 'backend':
            match = re.search(r'self\.register_.+_listener\( *(.*) *, *(.*) *, *self\.(.*) *\)',register_line)
            self.role = match.group(1)
            self.task = match.group(2)
            self.handler = match.group(3)
        elif self.MWPtype == 'frontend':
            match = re.search(r'self\.register_.+_step\( *(.*) *, *self\.(.\w*) *,?[^\n]*\)',register_line)
            self.role = MWPfile.role
            self.task = match.group(1)
            self.handler = match.group(2)
        else:
            pass    # nothing to do if it isn't a frontend or backend 
        
    def __str__(self):
        '''
        display task info in nicely formatted string
        called automatically for things like print
        '''
        return "Task: Role=%s, Step=%s, Handler=%s" % (self.role, self.task, self.handler)

class MWPform():
    '''
    captures information found in form_creator associated with frontend
    '''
    def __init__(self,form_name,form_code):
        '''
        takes two parameters:  name of form and form code
        '''
        self.name = form_name
        
        # add all the fields (except task_label)
        self.fields = re.findall(r'form.add_field\( *Type.\w+ *, *"([^"]+)"\)',form_code)
        

class MWPhandler():
    '''
    captures information associated with a results handler associated with the backend
    '''

    def __init__(self,handler_name,handler_code):
        '''
        takes two parameters:  name of handler and handler code
        '''
        self.name = handler_name
        
        # add all new tasks
        # note that these tasks are just dictionaries with role and taskname
        self.new_tasks = []
        task_lines = re.findall(r'Task.construct_from_result\( *result *, *.* *, *.* *\)',handler_code)
        for task in task_lines:
            match = re.search(r'Task\.construct_from_result\( *result *, *([^,]*) *, *([^,]*).*\)',task)
            new_task = {'role':match.group(1), 'task':match.group(2)}
            self.new_tasks.append(new_task)
        
    def roles(self):
        '''
        return a list of all roles found in the handler
        '''
        roles_list = []
        for task in self.new_tasks:
            roles_list.append(task['role'])
        return list(set(roles_list))
    
    def tasks(self):
        '''
        return a list of all tasks found in the handler
        '''
        task_list = []
        for task in self.new_tasks:
            task_list.append(task['task'])
        return list(set(task_list))

class MWPFile():
    '''
    A MWP file.  captures file path, name, and full contents
    '''
    def __init__(self, file_path):
        '''
        grab file path, name, and data into attributes
        '''
        self.path = file_path
        self.name = os.path.basename(file_path)
        self.data = file_read(file_path)
        self.MWPtype = MWPtype(self.data)
        self.flowname = get_flow(self.MWPtype,self.data)
        self.errors = [] # will use this to hold any errors we find during analysis
        
        # get method dictionary for frontend and backend
        if self.MWPtype in ['frontend', 'backend']:
            self.method_dict = get_method_dict(self.data)
        else:
            self.method_dict = {}

        # add role attribute to frontend now, because
        # we need it before building the list of handlers
        if self.MWPtype == 'frontend':
            self.role = get_frontend_role(self.data)
        
        self.tasks = []
        task_lines = get_task_lines(self.MWPtype, self.data)
        for line in task_lines:
            # skip any joined_listeners since we can't handle them yet
            if "register_joined_listener" not in line:
                self.tasks.append(MWPtask(self, line))
        self.method_names = get_methods(self.data)
        
        # add form or handler objects (for frontend or backend respectively)
        # Note:  for now we only add the ones that are registered as listeners
        # and we complain about any that are missing.
        self.handlers = []
        self.forms = []
        
        # add the handler objects for backend
        if self.MWPtype == 'backend':
            for task in self.tasks:
                if task.handler in self.method_dict:
                    self.handlers.append(MWPhandler(task.handler,self.method_dict[task.handler]))
                else:
                    self.errors.append('Missing handler:  %s' % task.handler)
                    
        # add the form objects for frontend files
        if self.MWPtype == 'frontend':
            for task in self.tasks:
                if task.handler in self.method_dict:
                    self.forms.append(MWPform(task.handler,self.method_dict[task.handler]))
                else:
                    self.errors.append('Missing form:  %s' % task.handler)
    
    def roles(self):    
        '''
        returns a list of roles found anywhere in this file
        
        first we scan all roles in the tasks, then all roles referenced in handlers
        '''
        roles_list = []
        for task in self.tasks:
            roles_list.append(task.role)
        for handler in self.handlers:
            roles_list = roles_list + handler.roles()
        
        # finally remove duplicates by converting to set object and back
        return list(set(roles_list))
    
    def task_list(self):
        '''
        returns a list of tasks found anywhere in this file
        
        first get the name of all tasks associated with this file
        then all tasks mentioned in handlers
        '''
        task_list = []
        for task in self.tasks:
            task_list.append(task.task)
        for handler in self.handlers:
            task_list = task_list + handler.tasks()
        
        # finally remove duplicates by converting to set object and back
        return list(set(task_list))
    
    def field_list(self):
        '''
        returns a list of fields used in any forms associated with this file
        '''
        field_list = []
        for form in self.forms:
            field_list = field_list + form.fields
        
        # finally remove duplicates by converting to set object and back
        return list(set(field_list))
        
    def __str__(self):
        output = 'MWPfile: %s\n' % self.path 
        output += 'Filename:  %s\n' % self.name
        output += 'Type:  %s\n' % self.MWPtype
        output += 'Flowname:  %s\n' % self.flowname
        for task in self.tasks:
            output += str(task) + '\n'
        for method_name in self.method_names:
            output += 'Method:  %s\n' % method_name
        return output + '\n'

# now that we have defined our functions and classes, time to do the checking
if __name__ == '__main__':
    
    # for starter's hard code path to the healthcare directory
    # will change this later to be something user can specify
    target_dir = get_directory()
    
    # get a list of all .py files in target directory
    target_files = glob.glob(target_dir + '*.py')
    
    # build a list of file objects for each of those files
    file_list = [MWPFile(x) for x in target_files]
    
    # note limitations
    print "Note:  joined_listeners are not included in this analysis.\n"
    
    # print list of flows
    flows = []
    for MWPfile in file_list:
        if MWPfile.MWPtype in ['backend','frontend']:
            flows.append(MWPfile.flowname)
    flows = list(set(flows))
    flows.sort()
    print "List of flows found in the code (there should only be one!):"
    for flow in flows:
        print flow
    print
    
    # print list of roles
    roles = []
    for MWPfile in file_list:
        roles = roles + MWPfile.roles()
    roles = list(set(roles))
    roles.sort()
    print "List of roles found in the code (look for misspellings or other issues):"
    for role in roles:
        print role
    print
    
    # print list of tasks
    tasks = []
    for MWPfile in file_list:
        tasks = tasks + MWPfile.task_list()
    tasks = list(set(tasks))
    tasks.sort()
    print "List of task names found in the code (look for misspellings or other issues):"
    for task in tasks:
        print task
    print    
    
    # print list of fields
    fields = []
    for MWPfile in file_list:
        fields = fields + MWPfile.field_list()
    fields = list(set(fields))
    fields.sort()
    print "List of field names found in the code (look for misspellings or other issues):"
    for field in fields:
        print field
    print
    
    # DO NEXT:
    '''
    strategy:  add functions outside of MWPFile
    
    LATER:  fix task to handle multiple results listener
    LATER:  handle tasks constructed from results (not singular)
    LATER:  fix bugs in building of handler tasks
    LATER:  check name_fields
    LATER:  check task_label
    LATER:  check that status set correctly
    LATER:  check illegal names
    LATER:  print out details on each file (str()) - but need to improve first.

    and more:

    print error messages (e.g. missing handlers)
    print list of which task follows which 
    print diagram of flow chart
    
    the code is inefficient because it involves multilple passes through each file.
    at some point fix this.
    '''
