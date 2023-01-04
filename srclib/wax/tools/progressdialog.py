# progressdialog.py
# Original by Greg Givler.
# Updates by Hans Nowak.

import wx
from wax import waxobject, core, styles

class ProgressDialog(wx.ProgressDialog, waxobject.WaxObject):

    def __init__(self, parent, title="Progress", message="Message", maximum=100,
                 **kwargs):
        
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)
        
        wx.ProgressDialog.__init__(self, title, message, maximum, parent, style)
        self.SetDefaultFont()
        self.BindEvents()
        
        styles.properties(self, kwargs)
        
    def Update(self, value, newmsg=""):
        return wx.ProgressDialog.Update(self, value, newmsg)
    
    def Resume(self):
        wx.ProgressDialog.Resume(self)
        
    def Show(self):
        return wx.ProgressDialog.Show(self)
    
    __styles__ = {
        'autohide': (wx.PD_AUTO_HIDE, styles.NORMAL), 
        'modal': (wx.PD_APP_MODAL, styles.NORMAL),
        'abort': (wx.PD_CAN_ABORT, styles.NORMAL),
        'show_elapsed_time': (wx.PD_ELAPSED_TIME, styles.NORMAL),
        'show_estimated_time': (wx.PD_ESTIMATED_TIME, styles.NORMAL),
        'show_remaining_time': (wx.PD_REMAINING_TIME, styles.NORMAL),
    }