# filetreeview-1.py

from wax import *

class MainFrame(Frame):

    def Body(self):
        splitter = Splitter(self)
        self.treeview = FileTreeView(splitter)
        self.filewindow = self.MakeFileWindow(splitter)
        splitter.Split(self.treeview, self.filewindow, direction='v', 
         sashposition=150, minsize=100)
         
        self.treeview.ProcessFiles = self.ProcessFiles
        
        self.AddComponent(splitter, expand='both')
        self.Pack()
        self.Size = 500, 400
         
    def MakeFileWindow(self, parent):
        p = Panel(parent, direction='v')
        listview = ListView(p, columns=['Filename', 'foo', 'bar', 'baz'])
        p.AddComponent(listview, expand='both')
        infopanel = Panel(p, direction='v')
        infopanel.SetSize((-1, 100))
        p.AddComponent(infopanel, expand='h')
        p.Pack()
        
        self.art = ArtProvider((16, 16))
        
        imagelist = ImageList(16, 16)
        imagelist.Add(self.art.GetBitmap('folder', 'other'), name='folder')
        imagelist.Add(self.art.GetBitmap('normal_file', 'other'), name='file')
        listview.SetImageList(imagelist)
        listview.SetColumnWidth(0, 300)

        # keep references around for later use
        p.listview = listview
        p.infopanel = infopanel
        
        return p
        
    def ProcessFiles(self, dirs, files):
        listview = self.filewindow.listview
        listview.DeleteAllItems()
        for short, long in dirs:
            listview.AppendRow(short + "/")
        for short, long in files:
            index = listview.AppendRow(short)
            image_index = listview._imagelist['file']
            listview.SetItemImage(index, image_index, image_index)

 
app = Application(MainFrame, title='filetreeview-1')
app.Run()
