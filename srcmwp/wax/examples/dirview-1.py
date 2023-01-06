# dirview-1.py

from wax import *
from wax.tools.dirview import DirView

FILTER = "All files (*.*)|*.*|Python files (*.py)|*.py"

class MainFrame(HorizontalFrame):

    def Body(self):
        self.dirview1 = DirView(self)
        self.AddComponent(self.dirview1, expand='both')
        self.dirview2 = DirView(self, dirs_only=1)
        self.AddComponent(self.dirview2, expand='both')
        self.dirview3 = DirView(self, filter=FILTER)
        self.AddComponent(self.dirview3, expand='both')
        self.Pack()
        self.Size = 500, 400
        
app = Application(MainFrame, title='dirview-1')
app.Run()
