# listview-sort-1.py

from wax import *

COLUMNS = ("Name", "Language")

DATA = [
    ("Guido", "Python"),
    ("Larry", "Perl"),
    ("Rasmus", "PHP"),
    ("Matz", "Ruby"),
    ("Bill", "Java"),
    ("John", "Lisp"),
]

class MainFrame(Frame):
    def Body(self):
        listview = ListView(self, columns=COLUMNS, rules='both')
        self.AddComponent(listview, expand='b')
        self.Pack()
        self.Size = (300, 300)
        
        for data in DATA:
            listview.AppendRow(*data)
            
        def f(item1, item2):
            # item1/2 are indices of rows being compared
            x1 = listview.GetStringItem(item1, 0)
            x2 = listview.GetStringItem(item2, 0)
            return cmp(x1, x2)
        listview.SortItems(f)
    
app = Application(MainFrame, title='listview-sort')
app.Run()
