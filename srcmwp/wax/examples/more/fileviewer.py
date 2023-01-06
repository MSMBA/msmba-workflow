# fileviewer.py
# Skeleton for a simple file viewer.

from wax import *
from wax.tools.dirview import DirView

def isimage(path):
    EXTENSIONS = [".jpg", ".png", ".gif", ".ico", ".bmp"]
    path = path.lower()
    for ext in EXTENSIONS:
        if path.endswith(ext):
            return True
    return False

class MainFrame(Frame):

    def Body(self):
        self.splitter = Splitter(self)
        self.dirview = DirView(self.splitter)
        self.dirview.OnSelectionChanged = self.OnDirViewSelectionChanged
        self.panel = self.MakeOverlayPanel(self.splitter)
        self.panel.Select(0)
        self.splitter.Split(self.dirview, self.panel, direction='v', 
         sashposition=200)
        self.AddComponent(self.splitter, expand='both')
        self.Pack()
        self.Size = 600, 400
        
    def MakeOverlayPanel(self, parent):
        op = OverlayPanel(parent)
        
        # window 1: a textbox
        self.textbox = TextBox(op, multiline=1, wrap=0, readonly=1)
        self.textbox.Font = Font("Courier New", 10)
        op.AddComponent(self.textbox, expand='both')
        
        # image 2: a panel
        self.imagepanel = Panel(op)
        op.AddComponent(self.imagepanel, expand='both')
        # create Bitmap control w/ dummy image
        dummy = ArtProvider((16,16)).GetBitmap('error', 'other')
        self.bitmap = Bitmap(self.imagepanel, dummy)
        self.imagepanel.AddComponent(self.bitmap, expand='both')
        self.imagepanel.Pack()
        
        op.Pack()
        return op
        
    def OnDirViewSelectionChanged(self, event):
        path = self.dirview.GetPath()
        if isimage(path):
            self.panel.Select(1)
            try:
                bitmap = Image(path).ConvertToBitmap()
            except:
                self.ShowText("Image could not be loaded")
            else:
                self.bitmap.SetBitmap(bitmap)
                self.imagepanel.Repack()
        else:
            self.ShowText(path)
            
    def ShowText(self, text):
        self.panel.Select(0)
        self.textbox.Value = text
            
        
app = Application(MainFrame, title='fileviewer')
app.Run()
