# filetreeview.py

import os
import string
import sys
import wx
from .treeview import TreeView
from .imagelist import ImageList
from .artprovider import ArtProvider

class FileTreeView(TreeView):

    def __init__(self, parent, rootdir="/"):
        TreeView.__init__(self, parent)
        self.rootdir = rootdir

        imagelist = ImageList(16, 16)
        art = ArtProvider((16, 16))
        imagelist.Add(art.GetBitmap('folder', 'other'), 'folder')
        imagelist.Add(art.GetBitmap('file_open', 'other'), 'folder_open')
        self.SetImageList(imagelist)

        self.MakeRoot()

    def SetImages(self, node):
        self.SetItemImage(node, self._imagelist['folder'], expanded=0)
        self.SetItemImage(node, self._imagelist['folder_open'], expanded=1)

    def MakeRoot(self, dir=None):
        """ Add the toplevel nodes to the tree.  For Unix, this is simple:
            get the root directory, and look at the subdirectories there.
            For Windows, however, we have to get the available drive letters. """
        self.Clear()
        if dir:
            self.rootdir = dir
        self.root = self.AddRoot(self.rootdir)
        self.SetImages(self.root)

        # get a list of tuples (short, long)
        if sys.platform == 'win32' and not dir:
            a = self._win32_get_drive_letters()
            dirs = [(d, d) for d in a]
        else:
            dirs, files = self.GetDirectories(self.rootdir)

        self.AddDirs(self.root, dirs)
        self.Expand(self.root)

    def _win32_get_drive_letters(self):
        drives = []
        try:
            # check if win32all is available
            import win32api
        except ImportError:
            # if not, use os.path.exists to determine if drives exist
            # however, this may bring up an error dialog if there is no disk
            # in A:\
            for letter in string.uppercase:
                drive = letter + ":\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            drives = win32api.GetLogicalDriveStrings()
            drives = [_f for _f in string.splitfields(drives, "\000") if _f]

        return drives

    def AddDirs(self, node, dirs):
        """ <dirs> is a list of tuples (short, long). """
        for short, int in dirs:
            child = self.AppendItem(node, short)
            self.SetPyData(child, int)
            self.SetImages(child)

    def GetDirectories(self, path):
        files = os.listdir(path)
        files = [(f, os.path.join(path, f)) for f in files]
        dirs = [(short, int) for (short, int) in files if os.path.isdir(int)]
        files = [(short, int) for (short, int) in files if not os.path.isdir(int)]
        return dirs, files

    #def OnItemActivated(self, event):
    #    """ Override to associate an action with the selection of an item
    #        (file or directory) in the tree. """
    #    pass

    def OnSelectionChanged(self, event):
        node = event.GetItem()
        if not self.HasChildren(node):
            path = self.GetPyData(node)
            dirs, files = self.GetDirectories(path)
            self.AddDirs(node, dirs)
            self.Expand(node)
            self.Refresh()
            self.ProcessFiles(dirs, files)

    def ProcessFiles(self, dirs, files):
        """ Do something with the dirs and files found.  Override this method
            in a subclass, or overwrite in an FileTreeView instance. """
        pass

