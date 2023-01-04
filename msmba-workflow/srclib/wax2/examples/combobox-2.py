# combobox-2.py
# Demonstrates "autolookup" feature in ComboBox.
# By Greg Givler.

from wax import *

CHOICES = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw",
           "Rivendale", "Huffnagle"]

class MainFrame(VerticalFrame):

    def Body(self):
        label = Label(self, "Choose your house:")
        self.AddComponent(label, border=3)
        cb1 = ComboBox(self, CHOICES, sort=1)
        cb1.OnChar = self.OnChar
        self.AddComponent(cb1, expand='h', border=3)
        button = Button(self, "OK", event=self.OnButtonClick)
        self.AddComponent(button, border=3)
        self.phrase = ''
        self.Pack()

        self.BackgroundColor = label.BackgroundColor = 'white'
        self.cb1 = cb1

    def OnButtonClick(self, event):
        print "You chose:", self.cb1.GetValue()

    def OnChar(self, event):
        obj = event.GetEventObject()
        keycode = event.GetKeyCode()
        print keycode
        if keycode == keys.backspace:
            self.phrase = self.phrase[:-1]
        elif keycode == keys.delete:
            self.phrase = ''
        elif keycode not in range(256):
            event.Skip()
            return 0
        else:
            self.phrase += chr(keycode).lower()
        if self.phrase == '':
            return 0
        for choice in CHOICES:
            choice = choice.lower()
            if choice.startswith(self.phrase):
                obj.SetStringSelection(choice)
                return 0
        return 0

app = Application(MainFrame, resize=0)
app.Run()
