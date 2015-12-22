# scrollframe.py

import wx
import containers
import styles
from wx.lib.scrolledpanel import ScrolledPanel

class ScrollPanel(ScrolledPanel, containers.Container):

    __events__ = {
    }

    def __init__(self, parent, direction='v', **kwargs):
        style = 0
        style |= styles.window(kwargs)
        
        ScrolledPanel.__init__(self, parent, wx.NewId(), style=style)

        self.BindEvents()
        self._create_sizer(direction)
        styles.properties(self, kwargs)
        self.Body()
        self.SetSizerAndFit(self.sizer);
        self.SetAutoLayout(True);
        self.SetupScrolling();
        