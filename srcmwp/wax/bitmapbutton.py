# bitmapbutton.py

from . import button
from . import containers
from . import waxobject
import wx
import os
from . import styles

def opj(path):
    """Convert paths to the platform-specific separator"""
    return os.path.join(*tuple(path.split('/')))

def loadbitmap(filename):
    """Load a bitmap from an image file"""
    return wx.Image(opj(filename), wx.BITMAP_TYPE_ANY).ConvertToBitmap()

class BitmapButton(wx.BitmapButton, waxobject.WaxObject):

    __events__ = {
        'Click': wx.EVT_BUTTON,
    }

    def __init__(self, parent, bmp, event=None, default_style=1, size=None, **kwargs):
        if isinstance(bmp, str) or isinstance(bmp, str):
            bmp = loadbitmap(bmp)
        style = default_style and 4 or 0
        style |= self._params(kwargs)
        style |= self._params(kwargs, button.Button.__styles__)
        style |= styles.window(kwargs)

        wx.BitmapButton.__init__(self, parent, wx.NewId(), bmp, 
         size=size or (-1,-1), style=style)

        self.SetDefaultFont()
        self.BindEvents()
        if event:
            self.OnClick = event
        styles.properties(self, kwargs)

    __styles__ = {
        'align': ({
            'left': wx.BU_LEFT,
            'top': wx.BU_TOP,
            'right': wx.BU_RIGHT,
            'bottom': wx.BU_BOTTOM,
        }, styles.DICTSTART),
        'autodraw': (wx.BU_AUTODRAW, styles.NORMAL),
    }
    