# line.py

import wx
from . import waxobject

class Line(wx.StaticLine, waxobject.WaxObject):

    def __init__(self, parent, size=(20,-1), direction='horizontal'):
        style = 0
        if direction.lower().startswith('h'):
            style |= wx.LI_HORIZONTAL
        elif direction.lower().startswith('v'):
            style |= wx.LI_VERTICAL
        else:
            raise ValueError("direction should be horizontal or vertical")

        wx.StaticLine.__init__(self, parent, wx.NewId(), size=size, style=style)

