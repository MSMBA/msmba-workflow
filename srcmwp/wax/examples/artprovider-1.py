# artprovider-1.py
# Based on wxPython demo.

from wax import *
import wx
import io

class MainFrame(VerticalFrame):
    def Body(self):
        self.art = ArtProvider((16,16))
        for image in self.art.images:
            stream = io.StringIO(smile48_png)
            self.art.RegisterFromData(stream, image, 'toolbar', (48,48))
        label = Label(self, "ArtProvider", align='c')
        label.Font = Font("Arial", 18, bold=1)
        # note: set font *before* adding, to make label the right size
        self.AddComponent(label, expand='h', border=5)

        line = Line(self, size=(20,-1), direction='h')
        self.AddComponent(line, expand='h', border=5)

        fgp = self.MakeFlexGridPanel(self)
        self.AddComponent(fgp, expand='b', border=5)

        self.Pack()
        #self.Size = 400, 400
        self.BackgroundColor = label.BackgroundColor = 'white'
        self.GetArt()

    def MakeFlexGridPanel(self, parent):
        fgp = FlexGridPanel(parent, 3, 3, 10, 10)

        self.combo1 = ComboBox(fgp, self.art.clients, readonly=1)
        self.combo1.OnSelect = self.OnSelectClient
        self.combo1.Select(0)
        fgp.AddComponent(0, 0, self.combo1)

        self.combo2 = ComboBox(fgp, self.art.images, readonly=1)
        self.combo2.OnSelect = self.OnSelectImage
        self.combo2.Select(0)
        fgp.AddComponent(1, 0, self.combo2)

        checkbox = CheckBox(fgp, "Custom toolbar provider")
        checkbox.OnCheck = self.OnCheck
        fgp.AddComponent(2, 0, checkbox)

        box1 = self.MakeBox(fgp, 'bmp16', (16,16))
        fgp.AddComponent(0, 2, box1, expand=1, align='c')

        box2 = self.MakeBox(fgp, 'bmp32', (32,32))
        fgp.AddComponent(1, 2, box2, expand=1, align='c')

        box3 = self.MakeBox(fgp, 'bmp48', (48,48))
        fgp.AddComponent(2, 2, box3, expand=1, align='c')

        fgp.Pack()
        return fgp

    def MakeBox(self, parent, name, size=(16,16)):
        box1 = VerticalPanel(parent)
        bmp = wx.EmptyBitmap(*size) # FIXME
        z = Bitmap(box1, bmp)
        setattr(self, name, z)
        box1.AddComponent(z, border=5, align='c')
        sizestring = "%dx%d" % (size[0], size[1])
        text = Label(box1, sizestring, align='c')
        box1.AddComponent(text, border=5, align='c')
        box1.Pack()
        return box1

    def GetArt(self):
        client = self.combo1.Value
        image = self.combo2.Value
        print(client, image)
        self.SetBitmap('bmp16', client, image, (16,16))
        self.SetBitmap('bmp32', client, image, (32,32))
        self.SetBitmap('bmp48', client, image, (48,48))

    def OnSelectClient(self, event):
        self.GetArt()

    def OnSelectImage(self, event):
        self.GetArt()

    def OnCheck(self, evt):
        self.art.UseCustom = evt.IsChecked()
        self.GetArt()

    def SetBitmap(self, name, client, image, size):
        bmp = self.art.GetBitmap(image or 'error', client or 'other', size)
        print(bmp)
        if not bmp.Ok():
            bmp = wx.EmptyBitmap(*size)
        obj = getattr(self, name)
        obj.SetBitmap(bmp)

#----------------------------------------------------------------------
# Image data

smile48_png = \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x000\x00\x00\x000\x08\x06\x00\
\x00\x00W\x02\xf9\x87\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x0c4IDATx\x9c\xed\x99{\x8c]\xc5}\xc7?3\xe7}\xef=\xf7\xe1\xbb\xde\x97\xd7\
\xbb`{\xc1\x0b\xb10\xc6(\x01\xb2n\xa9 Ai"\x82[\x05E$\xfc\x83\x10Hi\xa5(j\xd4\
H\x95\x9a\xaa\xad\x10i\xffI\x9b\xaaJj(\x15(~cC\xc2#H\x01c\x8ay8\xc5\xbb\xe0\
\xf7zm\xaf\xd7\xbb\xeb}\xde\xdd\xfb\xbe\xf7\xbc\xa6\x7f\xec\x82\x85H\xbb\xbb\
\xbe+\xa1J\x1di\xa4\xa393\xe7\xf7\xfd\x9e\xdfc~3?\x91N\xa7\xf9\xbf\xdc\xe4\
\xe7\r\xa0\xd1\xf6\xff\x04>\xef\xa6\xaf\xf4\x07\xf7\xefyF\xd5\xf2g\xa9\x15\
\x06\x11\xc1,Am\x14+\xd1\x81\xe1\xac\xc1L\xde\x88\x11\xdf\xc07\xb7\x7fK\xac\
\x94<\xb1RN|\xe0\xf9\xdd*w\xf9u.\x9d\xd8CX\x1b\'a{\xd8\x16d\xdc\x85\tJ \x8d\
\x18V\xeafd\xf6~\xcc\xf4\xed+BdE\x08\x1cx~\xb7:q\xf8o\x99\xbc\xfc;\x1c\xd3\'\
\xe3\xce\x03O\xbb\xe0X`\x9bW\xe7\xd6<\xa8\xf96\xa1\xfb\x87\xc4\xaf\xffA\xc3$\
V\xc4\x84.\x1d\x7f\x8eK\x83G\x89Y\xc1\'\xe0\xdb\x9a\xe6\x81g\xdc\xcf\x12\x98\
-\xd6\xa8\xd5\xdf\xc0\x9f\xd9\xd4\xb0\xec\x86\x9dx\xc7?\x7f_\xf5\xbd\xf7\x02\
\x9a\x9c\x07o[\xf3\x7f\xde6\xa1-\x0b\xd9\x14\xc4\x9d\xab=\x9b\x9a\x1f\xb7\r\
\x0fr\x078\xb0\xe7\x17\xeas%p\xee\xc3\x17\xf1je,\xe3\xea\x1fw\x16l?\xee\xfc\
\xfe5qg\xfe\xbd\xee_ *\x1emH~C\x04\xf6\xef}VM\x8c_\xfe\xcc\xb8m~\xdal~_\xb3M\
p,EX9\xd7\x08\x84\xc6\x08\xa8(\xc4\xf3\xfc\x86\x00(\x7f\xb6\xa1\xf5\r\x11\
\x98\x9d:G>_n\x08@!7\xc4\xf3\xfb~y\xcd~\xd0P\x14:=0N\xad\x1ea\xe8P\xaeA\xbe\
\x0cRB\xa9\n\xd3ypcW\xe7\xda\xb6\x8dm\xdb\xe8\x9aF\x10\x86\x9c\x1f\xf18>Pa\
\xf0\xca4_i\x99\xbcf\x0c\xd7L\xe0\xc5\xfd\xff\xa1\x9e\xfe\xc5\xbfp\xe0p\x04\
\x80e\x82\xa1\xfd\xcf\xf3{z\xae\xa7\xb7\xb7\x97m\x7f\xb0\x8d\xb7\xdey\x8bCo\
\xbeM\xdf\x87\xa7\xd0\xb4:\xb7\xf6\x9e\xe4\xd7/\xeeR\xdf\xb8\xff\xdb\xcb\xde\
\x13\xae\xc9\x84\x9e\xfd\xa7\xef\xaa\x96\xdaO\xd9\xbc\xee\x12=\xeb\xe2$b:\
\x86\xa1\x834P\x18\x94\xaa|\xa6W\xea\x92\xd1\xf1<o\x1cz\x97\x89\xa9<\x9af\
\x90LX|q\xf3\x1a6\xb6\x0e\xb3V\x7f\x81}O\xff\xd9\xb2Mi\xd9\x1ax\xf6\xa9\x7fW\
\xa3\xa7\xf7\xf0\x9fo\x0c\xd2\xda$x\xf8\x8f\x93\x94k\x82\xe6&\x87d\xc2! \xc6\
\xe8T\x80mY\x98\x96\x85\x94&R\xea(i\x92J%X\xdf\xa1\x90!\xe4\xf3-\xcc\xe4\x12\
\xe8\x94\x19\x1e\xec\xe7\xc3~\x8d\xd6u\xbd\xcb\x85\xb3<\x02;\x9f{Ni~\xc8\x8d\
\x9b\xbfKP\xedd\xf0\xa3~\x08s\xe8\xa2\xce\xc8\xa8B7\x02\x1cw\x06KJt\xbd\x82\
\xd0\x04RJ4MC\x97\x82`f\x88\x81s\x1a\xb99\x9b \x84z\x18Q*8\xf85\x87P\x18l\
\xb8\xe5\x0e`\xef\xb2\x08,9\x17\xda\xb7w\xaf\xcaOL\xb2*\xbd\x8a\xd3\xc7\x8eq\
\xea\xdd\xf7@\x85\x84\xf5*A\xad\x8a\n|\xd2\xe9$J)\x04\x1aa\xf4\xf1J\tRC\n\
\x81\xd4@\x13\x12t\x89\x10\x82H\x80PP+\x97)\xe5\x8b(\xdbf\xfb\x0f\xbe\xcfw\
\x1eyd\xc9\xbe\xb0d\x1f\x98\x19\x1f\'\x1eO0|\xfe"}\xef\xbcK\x14}\x82\x10!%\
\xba\xae\xa3\xe9:\x86i"u\x1d\xa9ih\x0bc\x9a\xbe\xf0\xaci\xc8\x85\xae-\xbc\
\x97\x9aF\xdcu1-\x93\xcaL\x8eC{\xf7\xf1\xc2\xc1\x83K\xf6\x85%\x99\xd0\xb3\
\xcf<\xa3T\xbdN\xa5T\xe2\x9d\xd7\x0fQ\xcc\x17\x88[&R(\xa4RX\x96\x85!%BjD(4MC\
H1\xaf\r\xa1\x81\x94H!\xf1B\x0fG\xd7@\x93H!@\n\x84\x04\xa1\x14\xa9t\x860TL\
\x9f\xbf\xc8\xc0\xf1\xe3K\xc5\xbf4\r\x94f\xa6\x11\x08~\xfb\xf2\xcb\\\x1c8\
\x87R\n?\x0c\x18\x99\x9be \x97\xe3\\\xbe@\xce0xu`\x90\xdf\x9c9G$%\x8e\xe3\
\x10O$\xb0c\x0e\x96ms\xa5T\xe0W\'\x8eslr\x82\t\xcf\xa3\x7ft\x94\xf7/\\`\xa2P\
\x00)\x89\xbb\t\xda\xdbZ\x11Jq\xe4W\xbf^\xb2\x16\x16\xd5\xc0\xfe={Tqr\x82\
\xc2\xec\x0cC\xa7\xcf"\x80\x9a\xefs|r\x8c\xf3\xa3#x\x9e\x07\x80a\x18\xf8\xbe\
\xcf\x9d\xb7\xdf\x8eeZ\x08)A\xcc;q\xa4 \xb5*\xcb\xf8\x7f\x1d\xe5\xfc\xc8\x08\
\xba\xae\xe3\xfb>B\x08R\xae\xcb\xd6\xeen\xfeh\xe3M\x18\x9a\x8ea\x1a\xe4\xa6\
\xa68\xf2\xe6\x9bK\xc1\xbf\xb8\x06\xfcj\x05\x15\xf8L\x8e]\x01\xa50M\x93+\x95\
"g\x86.\x12\x04\x01\xb1X\x82\xf6\xf6N\x92\xc9\x0cn\xc2\xa5;\xe5\x12\x85\xc1<\
\xf8\x05[\x97R\x92\xd2u\xba;:\xb0m\x87\xa6l\x0bm\xad\x1d\x98\xa6\xc5\\\xa1\
\xc0\x91\x93\'\x99\xacV\x90RbY\x16A\xdd\xe7\xec\xb1\xbe%\x11XT\x03~\xa5\x8c\
\nCf\'\'H\xc4\xe3\x08\xa5\xd1\x1c\xe9\xdc\xb5\xf5\x0e\xe2\xc9\x0c1\xc3\xc4\
\xb4l\x94\n)\xcd\xcd\xe2\x196\xc5P\x91\xf9\xf8\x03B\x12\x112^\xf1\xf8\xd2\
\xedw\xd3{\xa7A(utM\x92\x9b\x9dfrf\n+\xac\xd1\x92J#\x95"\x16\x8b\xa3P\xcc\
\x8e\x8f\xb3c\xc7\x0e\xf5\xe8\xa3\x8f\xfe\xaf\x11iQ\x02\x91\xef\xa3K\x81\xa5\
i\xb8\x89\x04U?\xc2p\xb2\xac5tz\xd6v\xa1\x87ut)\x90*\xc2\xbc\xa1\x9b\x81\x91\
\x11N\x8f\\fu\xa9\xc2\xe0\xe8%R\xf1\x04\xa9\xd5\x1d\xac\xbd~#=\x9d\x9d8""\
\xf0\xabH)\t\xda\xb3\xcc\xd5\xd630:\xc6D\xbdF\x97\xa3\x93t\x13h\xa6I\x04\x0c\
\r\r-\xaa\x81\xc5\x9d8\x08\x88\x82\x00\xbfRf$_`Z\t\x0c)\xd9\xb4~#\xa1W\xa5^)\
P\xc9O\x13\xd6\xab\xe0\xd7\xd9r\xd3\x17\xb8\xed\xe6[\x98\xae\xd7\x19\x99\x99\
f\xacP\xa0s\xfdM\xdcy\xcbVb\xa6N\xe8W\x89\xc2:^%O\xe0UH\xdb\x06[\xbao`\xba\
\x1epdd\x9c\xa9j\x15\xcb4\x91J\xe1\xd5j\x8d\x13\x88\xc2\x90Z\xb5\xc2\xdc\\\
\x8e\xa0^\xe5\xe2\xa5A6\xae\xef\x99\x0f\x83JQ\xafU\xf1}\x8fz\xbdB\x18\x05DQ\
\x84\x1bO20t\x91G\xbe\xfe\x15\xdc\x98\xc5\xf1\x93\x1f0W\xcc\xcf\xef\x13\x86\
\x85&@j\x12\x15\x85h\x9a$\x93L\xd2\xde\xdcFan\x1a\xd7q\xf0\xc3\x10/\x08>\xb5\
\xd7\\3\x01?\x8c\xa8\xd7j8v\x8c\x94&\x88\xbc:\x02\x85\x14\xf3\xf1[\xd7-\x14\
\x02\xa5\xe9\xd4\xbd\x80\xc1\x8b\x83\xec\xd8\xf5o\xacJX|\xe7\xeb\xf7\xf2\xbd\
\x07\xefg\xf8\xf2\x00O\xef\xfcW\xaa\xb5\n\x9a\xa1a;1\x0c\xcb\xc4t\x1c\x84\
\x9cwt\x85\xa2\xbb\xbd\x8d\x98m3[.\x11\x08\xd0\xf4\xc5\xb7\xa9E\th\x96E\xe0\
\x05\xd8\x8eC\xd6qp\r\x8d\xbe\x8f\x8eb[6\xae\x9b\xc6\x89\'HfZ\x88\xb9\xab\
\x98\xadz\xec\xf9\xcd\x8b\xdc\xb7\xf9F^z\xf2\xafX\xd7\xd5\xc9\xb7\xff\xf4\
\x9b\x1c\xfc\xc7\xbf!\xa6G\xbcz\xe8%\x94n\x10\xe9\x06\xba\xe3b\xdb\t\x9c\xb8\
K\xc9\xf3\xe8;\xfe\x01m-\xcdxB\xa1t\r\xa5\xeb\xf3\xa1\xb8Q\x02F,\x06J\xcd\
\xc7v"\xbe\xd0\xd2\xcc\x85\x0b\x03|p\xb2\x0faX\xa4\xb2m\xb8\xd9V\x8cx\x86\
\xd7\xdf=DO{\x13\x7f\xff\xf0\x9f\xd0\x94r!\xf0Q\x85<\xdd\xed-\xfc\xc3c\x0fs\
\xf4\xc3~^{\xfb0N2K<\xb5\x9ax\xa6\x99\xc8\xb0x\xff\xa3>\xdaR\x0em-\xcd\xcc\
\x14\x0bxa\x880\x8cE\xc1\xc3\x12\xa2\x90\x93L\xe2y>RH\x0c\xc3 )%[\xdb[8}\xf2\
\x18\xfd\'\xfbi\xce\xaefMK\x1b\xa3\x93cL\xccL\xd2\xeev\xa0+\x05\xb5\n\x9f\
\xdaJ\xbd\x1aQ\x14\xf1\xde\x07\xefs\xfdu\x1b0\x0c\x83\xf1\x99\x19fg\'ivmn\
\xdd\xba\x05\x84`fnv>\x1d\x89\xc7\xd0\x97`B\x8b\xce0l\x07a\x9aD*$\x1eOP*\x14\
I\xd86w\\\xd7E\xd1\xf7\x89\x00Y\xce\xb1&n3\x9eH\xf0\xf6\xd9\x0b\xfc\xc5S\xbb\
\xf8\xde7\xeee\xdd\x9aV\xaa\x9eO\xdf\xf9K\xfc\xdd\xae\x17\x11(\xb6\xf6t#j\
\xd3\x10\xeat\xad\xb2\xb9\xa3g\x0b\x9a\xd4(\x97\xcb\xcc\xe4r\x8cNN\xa2[6\xd2\
\xb2\xe9\xec\xecl\x9c\xc0\x03\xdb\xb7\x8b\xa7~\xf635~\xfe<\x86\x13C+/\x1c\
\xe2\x85 \x1d\x8b\xa1\x1b\x06\xbaa\xa0\xe9:\xa5 `*_\xe0\x95c\'x\xa5\xef\x14m\
\x99$\xd5\xba\xc7\x95\xb9"\xa6\xaeQ\x0b\x15]\x9d\x9dt\xb4\xb6b\xda\x16\xb6ec\
\xd9\x16\xbe\x1f\xe0\xf9>G\xfb\xfa(U\xabd\xd7\xac\xa5\xb3\xb3\x93\xc7\x1e{l\
\xd1\xb4zI\xd9hv\xcd\x1a\xccl\x96\xd9\xa9I\x84n@\x14"\xa4\xbc\xda\x17r\x9e\
\xee\xd6V&K\xdd\xbc\x7f\xe2\x04\xba\x80\\\xa9\x8c@\xa0P(-\xc6\x83\xf7\xdd\
\xcb\xf5m\xad(\x14\x9eWG\xd3t,a#\xa4\xe0\xf4\xc0Y\x06\x87/\xe3\xc4\xe3\x98n\
\x82\xeb\xae\xbbn)\xd0\x96~\xa0yf\xc7\x0eux\xdf^\xaaS\xd3\x18BbY\xe6\xfcIkA\
\x03\x1fk\xc1\x0fC\x86\xa6\xa6\x98,\x95\x98+\x97I\xc4b\xb465\xd1\xd5\xdcD{\
\xf3jL\xd3@\x01a\x14\xe28q\xdc\x94\xcb\xc8\xe5\xcb\xec\x7f\xe9U\xca\xf5:M\
\x1dkY\xb7\xb1\x87\x9d;w.\xe9P\xb3\xac\xdb\xe9\x9f\xfe\xe4\'\xea\xd0\x9e\xdd\
\xa8r\x95t2\x89m\x99\xf3\xe0u\x1d\xdd41\x0c\x830\x8a\x08\x95B\xd3u,\xcb\xc24\
M\x0c\xcbBHP(L\xcb$\x8a"\xbc\xc0\xc7\xb2\x1dj\xb5*\x87\xdf?\xca\xe5+\xe3\xa4\
V\xb7`\xa53<\xf4\xd0C<\xfe\xf8\xe3K"\xb0\xac3q\xd7\r7p\xeb=\xf7p\xec\xb7\xaf\
3\x91\x9b!f\x98\xb8\xaeK<\x11Gj\x1a\xb50D3\x0c\xcc\x05\x8d\x08!\x88\x94\xc2\
\xab\xd7\x91\xba$\x0c|\x84\x8a0-\x13\x82\x90\xbe\xbe~>\x1c8\x8b\x1fF\xacji\
\xc5H\xa7\xe9\xed\xed]2x\xb8\x86\xfa\xc0\xc1\x03\x07\xd4\xe0\xa9S\xbc\xf9\
\xc2\x0b\x14FGqL\x93\xe6\xa6&\xd2\xe9\x0cB\x93W\xcdI\xd3\xd0\x16HH)\x91R\x00\
\x11(\xc5L.G\xff\x993\x8c\xcf\xcd\xa1\x9b&\xa9\xd66\x0c7\xc9]w}\x99\'\x9f|rY\
wC\xd7\\\xe0\xd8\xf1\xf3\x9f\xab\xc3\x07\x0f2|\xea\x14\xa6\xd4\x16\xec? \x99\
L\x92M\xa7q\x1c\x07\xc30PBP\xad\xd5\xa8T\xca\xe4\xf3s\\\xc9\xcdP*\x14\t4\r7\
\x9d\xc6iiEZ6\xbd\xbd\xbd<\xf1\xc4\x13\xcb\xbe\xd8j\xa8B\xf3\xfc\xfe\xfdjx\
\xe0\x1c\xaf\xec\xdc\x89\x0c|.\x0c\x0e2\xedy\xb4$\x93$]\x17MJ\xbc \xa0\xe6yx\
\xbe\x87\xeb8\x9c\x19\x1d\xe3\xb6u\xeb\x18\x1e\x1e&\xb3i\x137\xddr\x0b\xdb\
\xb6m[\x96\xd9\xac\x18\x81\x8f\xdb=\xb7\xdd\xa6:\xae\\\xe1G\x99\x0c\x87-\x8b\
]\xc5"\xd3\xc3\xc3T,\x8b \x08\xd04\x8dD\xb9\xcc\xb6\xaf}\x8d\xf5o\xbd\xc5\
\xed\xad\xad<44\xc4\xcdw\xdd\xc5\xab\x87\x0e5TbZ\x912\xab\x93JQT\x8a\xec\xd0\
\x10\xdf\x12\x82\xbfv]\xc6\xcbe\xb4L\x06\'\x95\xc27M\x92\x1b6\xf0h\xb1\xc8\
\xc3--\xac\x8a\xc7\t\x95b\xd3\x96-\r\xcb^\x91\x1a\xd9\x8d\x9b61\xecy\xd4\x86\
\x86\x90A@\xe2\xd2%\xc2Z\r16\xc6\xadMM\xbc^(\x90\xae\xd7\xf1\x84\xa0R.3U\xab\
\x91jo\xa7\xad\xa3\xa3a\xd9+\xa2\x81\xb6\xceN\xc6fg\x99\xeb\xea"\xd6\xd6F{S\
\x13\xc9\xd5\xab\x19*\x958\x92\xcb\xa1\x0c\x83T"\xc1\x86X\x8cX{;\x17\x85\xa0\
\\,\x92\xcdf\x1b\x96\xbdb\x85\xee\xcbccT\xebu\x82J\x85\x1f\x9d?\xcfd\x18\xf2\
\xe7?\xfc!\xed]]\xfc\xee\x8d78\xd6\xd7\xc7\x91\xe1a\xbe\xb4y3^\xb1H87\xb7\
\xa4ls\xb1\xb6"\x04b\xb1\x181\xc7\xe1e\xc3`(\x97\xe3\xadL\x86\x07\xbf\xfaU\
\xbe|\xf7\xdd<\xf0\xc0\x03b\xf7\xee\xdd\xaaX(\xf0\xf0\xe1\xc3<25\xc5P\x14\
\xd1\x12\x8baYV\xc3\xb2W$\n\x1d<xP\xbd\xf7\xdak\x9c9s\x06]\x08\xbex\xcf=l\
\xe8\xe9a\xfb\xf6\xed\x9fD\x98}\xfb\xf6\xa9\x93\xfd\xfd\xbc\xf9\xca+\xd8\xb6\
\xcd\xdd\xf7\xdd\xc7_\xfe\xf8\xc7\rW\xea\xff\x1b\xd5\xe8\x0b\x01\xe7z\x82m\
\x00\x00\x00\x00IEND\xaeB`\x82'

app = Application(MainFrame, title='artprovider-1.py', resize=0)
app.Run()
