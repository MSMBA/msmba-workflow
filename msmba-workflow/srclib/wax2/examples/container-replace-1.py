# container-replace-1.py
# Create a number of buttons.  Clicking on them replaces them with a label.
# New in: 0.3.32

from wax import *

class MainFrame(VerticalFrame):
    def Body(self):
        for i in range(10):
            b = Button(self, "Button #" + str(i+1), event=self.ReplaceMe)
            self.AddComponent(b, border=1, expand='h')
        self.Pack()
    def ReplaceMe(self, event):
        button = event.GetEventObject()
        text = button.GetLabel()[7:]
        label = Label(self, "Label " + text)
        self.ReplaceComponent(button, label, border=5)
        
app = Application(MainFrame, title='container-replace-1')
app.Run()
