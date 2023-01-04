# waxrf-3.py
# Based on example code by Andreas Kaiser.
# New in Wax 0.3.33.

from wax import *
import wax.tools.waxrf as waxrf

resource = """\
<?xml version="1.0" ?>
<resource>
    <Splitter name="mysplitter" direction="v" sashposition="150">
        <VerticalPanel name="leftpanel">
            <Button name="btnPrj" text="Projekte" _expand="h" _border="5" />
            <Button name="btnDiv" text="Bereiche" _expand="h" _border="5" />
            <Button name="btnMumo" text="Aufnahmen" _expand="h" _border="5" />
            <Button name="btnBasics" text="Stammdaten" _expand="h" _border="5" />
        </VerticalPanel>
        <NoteBook name="nbPrj">
            <Page text="Liste">
                <Panel BackgroundColor="yellow" />
            </Page>
            <Page text="Details">
                <Panel BackgroundColor="red" />
            </Page>
        </NoteBook>
    </Splitter>
    <MenuBar name="mb">
        <Menu text="Datei">
            <MenuItem text="Oeffnen"/>
            <MenuItem name="menuFileExit" text="Beenden"/>
        </Menu>
        <Menu text="Hilfe">
            <MenuItem text="Info"/>
        </Menu>
    </MenuBar>
</resource>
"""

res = waxrf.XMLResource()
res.LoadFromString(resource)

# stick a custom event in Button
def MyOnClick(self, event):
    print 'U clicked the button with label', `self.GetLabel()`
    print self.GetId(), self.GetName()

Button.OnClick = MyOnClick

class MainFrame(VerticalFrame):
    def Body(self):
        menubar = res.LoadMenuBar(self, 'mb')
        sp1 = res.LoadObject(self, 'mysplitter')
        self.AddComponent(sp1, expand='both')
        self.Pack()
        self.Size = 800, 600
        
        # we can refer to the controls like this:
        print sp1.leftpanel
        print sp1.leftpanel.btnPrj
        print self.mysplitter
        # (assuming they have a 'name' attribute!)

    def Menu_Datei_Beenden(self, event):
        print "Beenden"
        self.Close()

app = Application(MainFrame, title='Test')
app.Run() 