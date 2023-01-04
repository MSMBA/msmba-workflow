# datepicker-1.py

from wax import *
from wax.tools.datepicker import DatePicker
import datetime
import time

class MainFrame(VerticalFrame):

    def Body(self):
        p1 = HorizontalPanel(self)
        dp1 = DatePicker(p1)
        p1.AddComponent(dp1)
        p1.AddSpace(10)
        
        b1 = Button(p1, "Add 1 day", event=self.AddOneDay)
        p1.AddComponent(b1)
        
        p1.Pack()
        self.AddComponent(p1, expand='h', border=4)
        
        p2 = HorizontalPanel(self)
        dp2 = DatePicker(p2, style='dropdown', show_century=1)
        p2.AddComponent(dp2)
        p2.AddSpace(10)
        
        b2 = Button(p2, "Yesterday", event=self.SetToYesterday)
        p2.AddComponent(b2)

        p2.Pack()
        self.AddComponent(p2, expand='h', border=4)
        
        self.Pack()
        self.BackgroundColor = p1.BackgroundColor
        self.dp1 = dp1
        self.dp2 = dp2
        
        # restrict dp2's range to current year
        thisyear = time.localtime(time.time())[0]
        dp2.SetRange((thisyear, 1, 1), (thisyear, 12, 31))
        
    def AddOneDay(self, event):
        self.dp1.Inc()
        print "Date set to:", self.dp1.Value
        
    def SetToYesterday(self, event):
        now = time.localtime(time.time())
        self.dp2.Value = now[:3] # tuple: (year, month, day)
        self.dp2.Dec()
        
app = Application(MainFrame, title='datepicker-1')
app.Run()
