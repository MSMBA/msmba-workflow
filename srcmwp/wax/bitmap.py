# bitmap.py

import wx
from . import waxobject
from . import image
import io

# XXX not sure what to do with this
class Bitmap(wx.StaticBitmap, waxobject.WaxObject):

    def __init__(self, parent, bitmap):
        if isinstance(bitmap, str) or isinstance(bitmap, str):
            bitmap = BitmapFromFile(bitmap)
        wx.StaticBitmap.__init__(self, parent, wx.NewId(), bitmap)
        # XXX supposedly you can load this from file too?

#
# use these functions for convenience...
# unfortunately, they return wxBitmaps, not Bitmaps

def BitmapFromData(data):
    stream = io.StringIO(data)
    z = wx.ImageFromStream(stream)
    return wx.BitmapFromImage(z)

def BitmapFromFile(filename):
    data = open(filename, 'rb').read()
    return BitmapFromData(data)

