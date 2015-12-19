# colordb.py
# Allows access to Tk's color names, plus adds some other functions.
# You can now do obj.SetForeground(colordb['papayawhip'])! ;-)

import math
import operator
import string

_colordata = open("colordb.txt", "r").read()

d = {}
for s in _colordata.split("\n"):
    name, rest = s[:27], s[27:]
    r, g, b = map(int, string.split(rest))
    d[name.strip().lower()] = (r, g, b)

items = d.items()
items.sort()
f = open("colordb.py.out", "w")
print >> f, "data = {"
for key, value in items:
    print >> f, " %r: %r," % (key, value)
print >> f, "}"
f.close()
