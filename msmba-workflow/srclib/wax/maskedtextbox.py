# maskedtextbox.py

import wx
import wx.lib.masked.textctrl as med
import waxobject

class MaskedTextBox(med.TextCtrl, waxobject.WaxObject):

    def __init__(self, parent, text="", *args, **kwargs):
        med.TextCtrl.__init__(self, parent, wx.NewId(), text,
         *args, **kwargs)
