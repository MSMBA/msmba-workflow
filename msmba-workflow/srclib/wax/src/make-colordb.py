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
    r, g, b = list(map(int, string.split(rest)))
    d[name.strip().lower()] = (r, g, b)

items = list(d.items())
items.sort()
f = open("colordb.py.out", "w")
print("data = {", file=f)
for key, value in items:
    print(" %r: %r," % (key, value), file=f)
print("}", file=f)
f.close()
