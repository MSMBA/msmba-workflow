# waxrf-2.py

from wax import *
import wax.tools.waxrf as waxrf

resource = """\
<?xml version="1.0" ?>
<resource>
  <Splitter name="mysplitter" direction="v" sashposition="200">
    <Panel name="leftpanel" />
    <NoteBook name="notebook">
      <Page text="Page 1">
        <Panel BackgroundColor="yellow" />
      </Page>
      <Page text="Page 2">
        <Panel BackgroundColor="red" />
      </Page>
    </NoteBook>
  </Splitter>
</resource>
"""

res = waxrf.XMLResource()
res.LoadFromString(resource)

class MainFrame(VerticalFrame):
    def Body(self):
        p1 = res.LoadObject(self, 'mysplitter')
        self.AddComponent(p1, expand='both')
        self.Pack()
        self.Size = 500, 400

app = Application(MainFrame, title='Wax XRC Example 2')
app.Run()
