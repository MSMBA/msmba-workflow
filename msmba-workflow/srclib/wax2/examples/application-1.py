# application-1.py

from wax import *

class MainFrame(Frame):
    def Body(self):
        p = Panel(self)
        self.AddComponent(p, expand='both')
        self.Pack()
        self.panel = p

app = Application(MainFrame, title='application-1')

# at this point, the main window has been created
# let's inspect it
print dir(app)
win = app.TopWindow # pseudo-properties work here too!
print win
win.Size = (200, 200)
win.panel.BackgroundColor = 'blue'
win.Refresh()

app.Run()