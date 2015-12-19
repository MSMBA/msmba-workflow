# application.py

import wx
import sys
from waxconfig import WaxConfig
import font

class Application(wx.App):

    def __init__(self, frameklass, *args, **kwargs):
        # takes a frame *class* plus arbitrary options.  these options will
        # be passed to the frame constructor.
        self.frameklass = frameklass
        self.args = args
        self.kwargs = kwargs

        # when set, the app uses the stdout/stderr window; off by default
        use_stdout_window = 0
        if kwargs.has_key('use_stdout_window'):
            use_stdout_window = kwargs['use_stdout_window']
            del kwargs['use_stdout_window']
        wx.App.__init__(self, use_stdout_window)

    def OnInit(self):
        if isinstance(WaxConfig.default_font, tuple):
            WaxConfig.default_font = font.Font(*WaxConfig.default_font)
        else:
            print >> sys.stderr, "Warning: This construct will not work in future wxPython versions"
        self.mainframe = self.frameklass(*self.args, **self.kwargs)
        if hasattr(self.mainframe.__class__, "__ExceptHook__"):
            sys.excepthook = self.mainframe.__ExceptHook__
        self.mainframe.Show(True)
        self.SetTopWindow(self.mainframe)
        return True

    def Run(self):
        self.MainLoop()
        
    #
    # pseudo-properties

    def __getattr__(self, name):
        if hasattr(self.__class__, "Get" + name):
            # use self.__class__ rather than self to avoid recursion
            f = getattr(self, "Get" + name)
            return f()
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        if hasattr(self, "Set" + name):
            f = getattr(self, "Set" + name)
            return f(value)
        else:
            self.__dict__[name] = value


# TODO:
# it should be easy to set font, icon, etc...
