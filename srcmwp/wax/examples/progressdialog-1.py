# progressdialog-1.py
# By Greg Givler.
# Updates by Hans Nowak.

from wax import *
from wax.tools.progressdialog import ProgressDialog
import time

class MainFrame(Frame):
    def Body(self):
        self.AddComponent(Button(self, "one", self.OnClick))
        self.AddComponent(Button(self, "two", self.OnClick2))
        self.AddComponent(Button(self, "three", self.OnClick3))
        self.Pack()
    
    def OnClick(self, event):
        # note: does not have a Cancel button, so it cannot be interrupted
        dlg = ProgressDialog(self, title="Progress Dialog Test", 
              message="Counting from 1 to 1000", maximum=1000, modal=0)
        dlg.Show()
        cancel = True
        for i in range(1000):
            if i % 100 == 0:
                cancel = dlg.Update(i, "Counting from " + str(i) + " to 1000")
            else:
                cancel = dlg.Update(i)
            time.sleep(.01)
            if not cancel:
                break
        dlg.Destroy()
        
    def OnClick2(self, event):
        dlg = ProgressDialog(self, title="Progress Dialog Test", 
              message="Counting from 1 to 1000", maximum=1000, abort=1)
        dlg.Show()
        cancel = True
        for i in range(1000):
            if i % 100 == 0:
                cancel = dlg.Update(i, "Counting from " + str(i) + " to 1000")
            else:
                cancel = dlg.Update(i)
            time.sleep(.01)
            if not cancel:
                break
        dlg.Destroy()

    def OnClick3(self, event):
        dlg = ProgressDialog(self, title="Progress Dialog Test", 
              message="Counting from 1 to 1000", maximum=1000, abort=1, 
              show_elapsed_time=1, show_estimated_time=1, show_remaining_time=1)
        dlg.Show()
        cancel = True
        for i in range(1000):
            if i % 100 == 0:
                cancel = dlg.Update(i, "Counting from " + str(i) + " to 1000")
            else:
                cancel = dlg.Update(i)
            time.sleep(.01)
            if not cancel:
                dlg2 = MessageDialog(self, title="Continue?", text="Do you want to abort?", yes_no=1)
                result = dlg2.ShowModal()
                if result == "yes":
                    dlg.Destroy()
                    break
                else:
                    dlg.Resume()
                dlg2.Destroy()
        if dlg:
            dlg.Destroy()

app = Application(MainFrame, title='progressdialog-1')
app.MainLoop()
        