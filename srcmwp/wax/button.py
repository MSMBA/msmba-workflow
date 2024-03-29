# button.py

from . import containers
from . import waxobject
import wx
from . import styles


class Button(wx.Button, waxobject.WaxObject):

    __events__ = {
        'Click': wx.EVT_BUTTON,
    }

    def __init__(self, parent, text="", event=None, size=None, **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)

        wx.Button.__init__(self, parent, wx.NewId(), text, size=size or (-1,-1),
         style=style)

        self.SetDefaultFont()
        self.BindEvents()
        if event:
            self.OnClick = event

        styles.properties(self, kwargs)

    #
    # style parameters
    
    __styles__ = {
        'align': ({
            "left": wx.BU_LEFT,
            "right": wx.BU_RIGHT,
            "bottom": wx.BU_BOTTOM,
            "top": wx.BU_TOP,
            "exact": wx.BU_EXACTFIT,
        }, styles.DICTSTART),
        'flat': (wx.NO_BORDER, styles.NORMAL), 
          # seems to have no effect on Windows XP
        'exactfit': (wx.BU_EXACTFIT, styles.NORMAL),
    }

