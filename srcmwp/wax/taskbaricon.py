# taskbaricon.py

from . import waxobject
import wx.adv
import wx

class TaskBarIcon(wx.adv.TaskBarIcon, waxobject.WaxObject):

    __events__ = {
        'LeftDoubleClick': wx.adv.wxEVT_TASKBAR_LEFT_DCLICK,
        'RightUp': wx.adv.wxEVT_TASKBAR_RIGHT_UP,
        'LeftDown' : wx.adv.wxEVT_TASKBAR_LEFT_DOWN,
        'RightDoubleClick' : wx.adv.wxEVT_TASKBAR_RIGHT_DCLICK,
        'RightUp': wx.adv.wxEVT_TASKBAR_RIGHT_UP,
        'RightDown': wx.adv.wxEVT_TASKBAR_RIGHT_DOWN,
    }

    def __init__(self):
        wx.TaskBarIcon.__init__(self)
        self.BindEvents()

    def SetIcon(self, obj, tooltip=""):
        """ Like wx.Frame.SetIcon, but also accepts a path to an icon file. """
        if isinstance(obj, str) or isinstance(obj, str):
            obj = wx.Icon(obj, wx.BITMAP_TYPE_ICO)    # FIXME
        wx.TaskBarIcon.SetIcon(self, obj, tooltip)
        # XXX same as Frame.SetIcon... there must be a better way, since I
        # don't like wx.Icon in Wax. :-)

    # XXX more events are in order, of course...

