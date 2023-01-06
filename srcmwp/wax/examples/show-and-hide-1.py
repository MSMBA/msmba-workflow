# show-and-hide-1.py

from wax import *

class MainFrame(Frame):

    def Body(self):
        b = Button(self, "Minimize me", event=self.IconizeMe)
        self.AddComponent(b, border=30)
        self.Pack()
        self.tbicon = None

    def IconizeMe(self, event):
        self.tbicon = TaskBarIcon()
        self.tbicon.OnLeftDoubleClick = self.ShowMeAgain
        self.tbicon.SetIcon('icon1.ico', 'Icon 1')
        self.Iconize(1) # creates an icon in the task bar
        self.Show(0)    # hides the window

    def ShowMeAgain(self, event):
        self.Iconize(0)
        self.Show(1)
        self.Raise()
        if self.tbicon:
            self.tbicon.Destroy()
            self.tbicon = None # important, or we'll get a segfault
            core.GetApp().ProcessIdle()

    def OnClose(self, event):
        if self.tbicon:
            self.tbicon.Destroy()
        event.Skip()

app = Application(MainFrame, title='show-and-hide-1')
app.Run()

