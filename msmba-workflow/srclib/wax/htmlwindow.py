# htmlwindow.py

# todo: styles

import wx.html
from . import waxobject

class HTMLWindow(wx.html.HtmlWindow, waxobject.WaxObject):

    def __init__(self, parent, fullrepaint=1, scroll=True, size=None):
        style = 0
        if not fullrepaint:
            style |= wx.NO_FULL_REPAINT_ON_RESIZE
        if not scroll:
            style |= wx.html.HW_SCROLLBAR_NEVER
        wx.html.HtmlWindow.__init__(self, parent, wx.NewId(), style=style)
        if size != None:
            self.SetSize(size);
        self.SetBorders(0);
