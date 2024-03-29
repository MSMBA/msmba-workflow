# flexgridpanel.py

# todo: styles

import wx
from . import containers
from . import panel

class FlexGridPanel(wx.Panel, containers.FlexGridContainer):
    """ Sub-level containers inside a frame, used for layout. """
    def __init__(self, parent=None, rows=3, cols=3, hgap=1, vgap=1,
     growable_cols=(), growable_rows=()):
        wx.Panel.__init__(self, parent or NULL, wx.NewId())

        self._create_sizer(rows, cols, hgap, vgap)
        self.SetDefaultFont()
        self.Body()

        for col in growable_cols:
            self.AddGrowableCol(col)
        for row in growable_rows:
            self.AddGrowableRow(row)
