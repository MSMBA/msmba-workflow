# dirview.py
#
# Notes:
# 1. Setting <filter> to a valid filter value is enough to activate filtering.
#    Setting a flag in addition to this (wx.DIRCTRL_SHOW_FILTERS) is not
#    necessary.
#    (Also see: examples/dirview-1.py)
# 2. GetTreeCtrl() returns a wx.TreeCtrl rather than a Wax TreeView.  Maybe
#    we should write this in Wax instead?

import wx
from wax import waxobject, styles, treeview

class DirView(wx.GenericDirCtrl, waxobject.WaxObject):

    __events__ = treeview.TreeView.__events__
    
    def __init__(self, parent, filter="", **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)
        
        if filter:
            style |= wx.DIRCTRL_SHOW_FILTERS
    
        wx.GenericDirCtrl.__init__(self, parent, filter=filter, style=style)
        self.SetDefaultFont()
        self.BindEvents()
        styles.properties(self, kwargs)
        
    __styles__ = {
        'dirs_only': (wx.DIRCTRL_DIR_ONLY, styles.NORMAL),
        'borders_3d': (wx.DIRCTRL_3D_INTERNAL, styles.NORMAL),
        'select_first': (wx.DIRCTRL_SELECT_FIRST, styles.NORMAL),
        'edit_labels': (wx.DIRCTRL_EDIT_LABELS, styles.NORMAL),
    }
    