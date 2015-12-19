# spinbox.py
# Contributed by Daniel James Baker.
#
# Note: Now that SpinBox exists, a wrapper around SpinButton will *not*
# be necessary.

from wax import waxobject, styles
import wx
import wx.lib.agw.floatspin

class SpinBoxDouble(wx.lib.agw.floatspin.FloatSpin, waxobject.WaxObject):

    # NOTE: If both OnSpin and OnSpinBox are defined, OnSpin will be called,
    #       but OnSpinBox will not be called unless OnSpin calls event.Skip().
    #       They both handle the same GUI actions.
    __events__ = {
        'SpinBox': wx.EVT_SPINCTRL,
        'Text': wx.EVT_TEXT,
        'Spin': wx.EVT_SPIN,
        'SpinUp': wx.EVT_SPIN_UP,
        'SpinDown': wx.EVT_SPIN_DOWN,
    }

    def __init__(self, parent, value=0, size=None, min=-1e12, max=1e12, increment=1.0, digits=-1, **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)
        
        wx.lib.agw.floatspin.FloatSpin.__init__(self, parent, wx.NewId(), size=size or (95, -1),
            style=style, value=value, min_val=min, max_val=max, increment=increment, digits=digits)
        self.SetDefaultFont()

        self.BindEvents()
        styles.properties(self, kwargs)

    def SetMin(self, val):
        "Set the minimum allowed value while retaining the current maximum."
        self.SetRange(val, self.GetMax())

    def SetMax(self, val):
        "Set the maximum allowed value while retaining the current minimum."
        self.SetRange(self.GetMin(), val)

    def GetRange(self):
        "Return a tuple of the current (min, max) allowed values."
        return (self.GetMin(), self.GetMax())
        
    __styles__ = {
        'arrowkeys': (wx.SP_ARROW_KEYS, styles.NORMAL),
        'wrap': (wx.SP_WRAP, styles.NORMAL),
    }

