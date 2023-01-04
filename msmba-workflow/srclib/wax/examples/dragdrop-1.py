# dragdrop-1.py

from wax import *

phont = ("Courier New", 10)

class MainFrame(VerticalFrame):
    def Body(self):
        self.text1 = TextBox(self, text="Drop **files** here\n", size=(400, 150),
                     multiline=1)
        self.text1.Font = phont
        self.AddComponent(self.text1, expand="both", border=2)
        self.text2 = TextBox(self, text="Drop **text** here\n", multiline=1)
        self.text2.Font = phont
        self.AddComponent(self.text2, expand="both", border=2)

        filedrop = FileDropTarget(self.text1, event=self.OnDropFiles)
        textdrop = TextDropTarget(self.text2, event=self.OnDropText)

        self.Pack()

    def OnDropFiles(self, x, y, filenames):
        print("You dropped:", filenames)
        for filename in filenames:
            print(filename, file=self.text1)

    def OnDropText(self, x, y, text):
        print(text, file=self.text2)

app = Application(MainFrame, title="Drag & drop demo")
app.Run()
