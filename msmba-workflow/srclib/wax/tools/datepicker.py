# datepicker.py
# Original contributed by Nicolas Pinault.
# Changes and additional methods by Hans Nowak.

from wax import containers, waxobject, styles
import wx
import wx.adv
import datetime


class DatePicker(wx.adv.DatePickerCtrl, waxobject.WaxObject):

    __events__ = {
        'Change' : wx.adv.wxEVT_DATE_CHANGED,
    }

    def __init__(self, parent, text="", event=None, size=None, **kwargs):
        style = 0
        style |= self._params(kwargs)
        style |= styles.window(kwargs)
            
        wx.adv.DatePickerCtrl.__init__(self, parent, wx.NewId(), size=size or (-1,-1),
         style=style)
        
        self.SetDefaultFont()
        self.BindEvents()
        if event:
            self.OnChange = event
            
        styles.properties(self, kwargs)
        
    #
    # style parameters
    
    __styles__ = {
        'style': ({
            'dropdown' : wx.adv.DP_DROPDOWN,
            'spin'     : wx.adv.DP_SPIN,
            'default'  : wx.adv.DP_DEFAULT,
        }, styles.DICTSTART),
        'allow_none': (wx.adv.DP_ALLOWNONE, styles.NORMAL),
        'show_century': (wx.adv.DP_SHOWCENTURY, styles.NORMAL),
    }
    
    #
    # date conversion methods.
    # NOTE: might be moved to a separate module.  use with caution.
    
    def _wx_to_date(self, wxdate):
        return datetime.date(wxdate.GetYear(), wxdate.GetMonth() + 1,
                             wxdate.GetDay())
        
    def _date_to_wx(self, adate):
        wxdate = wx.DateTime()
        if isinstance(adate, tuple) and len(adate) == 3:
            wxdate.Set(adate[2], adate[1]-1, adate[0])
        elif isinstance(adate, datetime.date):
            wxdate.Set(adate.day, adate.month-1, adate.year)
        else:
            raise ValueError("date must be datetime.date, or 3-tuple (year, month, day). """)
        return wxdate
        
    def GetValue(self):
        """ Return the selected date as a datetime.date (Python stdlib). """
        wxdate = wx.adv.DatePickerCtrl.GetValue(self)
        return self._wx_to_date(wxdate)
        
    def SetValue(self, adate):
        wxdate = self._date_to_wx(adate)
        wx.adv.DatePickerCtrl.SetValue(self, wxdate)
        
    def SetRange(self, range1, range2):
        r1 = self._date_to_wx(range1)
        r2 = self._date_to_wx(range2)
        wx.adv.DatePickerCtrl.SetRange(self, r1, r2)
        
    # According to the wxWidgets 2.6.0 reference manual, wxDatePickerCtrl
    # does have GetRange()... but the wxPython object does not seem to have
    # this method!  What gives?
        
    #def GetRange(self):
    #    r1, r2 = wx.adv.DatePickerCtrl.GetRange(self)
    #    range1 = self._wx_to_date(r1)
    #    range2 = self._wx_to_date(r2)
    #    return range1, range2
    
    def Inc(self, days=1):
        d = self.GetValue()
        e = d + datetime.timedelta(days=days)
        self.SetValue(e)
        
    def Dec(self, days=1):
        self.Inc(-days)
        