# sound.py

# Commented to avoid dependency on wx.adv library:

import wx.adv
from . import waxobject

class Sound(wx.adv.Sound, waxobject.WaxObject):

    def Play(self, sync=1):
        mode = wx.SOUND_SYNC
        if not sync:
            mode = wx.SOUND_ASYNC
        wx.Sound.Play(self, mode)



