# containers.py
# Containers are mixin classes that have a sizer and a number of methods to
# deal with that sizer (add components, etc).  Used to implement fairly
# "basic" controls like Panel and Frame.  When in doubt, derive from those
# two rather than making up your own container construct.

import utils
import waxconfig
import waxobject
import wx
import warnings

class Container(waxobject.WaxObject):

    def _create_sizer(self, direction):
        if direction.lower().startswith("h"):
            dir = wx.HORIZONTAL
        elif direction.lower().startswith("v"):
            dir = wx.VERTICAL
        else:
            raise ValueError, "Incorrect direction"
        self.sizer = wx.BoxSizer(dir)
        self._packed = 0

    def Body(self):
        """ Optionally override this to create components.  Add them with the
            AddComponent() method. """
            
    def _make_flags(self, expand, stretch, align, border):
        if stretch:
            warnings.warn("stretch is deprecated; use expand with strings instead")
    
        if isinstance(expand, str):
            expand = expand.lower()
            if expand.startswith("h"):
                if self.GetOrientation() == 'horizontal':
                    expand, stretch = 1, 0
                else:
                    expand, stretch = 0, 1
            elif expand.startswith("v"):
                if self.GetOrientation() == 'horizontal':
                    expand, stretch = 0, 1
                else:
                    expand, stretch = 1, 0
            elif expand.startswith("b"):
                expand = stretch = 1
            elif expand == '':
                expand = stretch = 0
            else:
                raise ValueError, "Invalid value for expand: %r" % (expand,)

        flags = 0
        if stretch:
            flags |= wx.EXPAND
        if align:
            flags |= {
                "t": wx.ALIGN_TOP,
                "c": wx.ALIGN_CENTER,
                "b": wx.ALIGN_BOTTOM,
                "r": wx.ALIGN_RIGHT,
                "l": wx.ALIGN_LEFT,
            }.get(align.lower()[:1], 0)
        if border:
            flags |= wx.ALL

        flags |= wx.FIXED_MINSIZE
        
        return expand, flags

    def AddComponent(self, comp, expand=0, stretch=0, align=None, border=0):
        # expand: expands a component in the direction of the panel/sizer
        # stretch: expands a component in the other direction
        # for example, if we have a horizontal panel, and resize the window
        # both horizontally and vertically, then a component with 'expand'
        # will expand horizontally, and one with 'stretch' will expand
        # vertically. (See simplebuttons.py)

        # make sure the parents are correct
        if waxconfig.WaxConfig.check_parent:
            if comp.GetParent() is not self:
                utils.parent_warning(comp, self)

        expand, flags = self._make_flags(expand, stretch, align, border)
        if 0 and hasattr(comp, 'sizer') and hasattr(comp, '_include_sizer'):
            # ugly hack to add nested sizer rather than its frame
            # only for certain quirky controls, like GroupBox!
            self.sizer.Add(comp.sizer, expand, flags)
        else:
            self.sizer.Add(comp, expand, flags, border)
            # comp can be a component or a tuple (width, height), but the
            # Add() method is called just the same, as of wxPython 2.5.1.5

    def AddSpace(self, width, height=None, *args, **kwargs):
        if height is None:
            height = width
        return self.AddComponent((width, height), *args, **kwargs)
    AddSeparator = AddSpace
    
    def InsertComponent(self, x, control, expand=0, align=None, border=0):
        """ Insert WaxObject <control> at position <x>.  <x> may be another
            control, in which case its position is taken, so <control> will
            be inserted before it. """
        if type(x) == type(42):
            idx = x
        else:
            idx = self.GetSizerObjectIndex(x)
            
        expand, flags = self._make_flags(expand, 0, align, border)
        self.sizer.Insert(idx, control, expand, flags, border)
    
    def ReplaceComponent(self, old, new, expand=0, align=None, border=0, 
     destroy=1, repack=1):
        """ Replace control <old> with <new>.  The usual options (expand, align,
            border) apply to the new control.  
            If <destroy> is set, then the old control will be automatically 
            destroyed.  If <repack> is set, the container will be repacked. 
        """
        self.InsertComponent(old, new, expand=expand, align=align, border=border)
        self.sizer.Detach(old)
        if destroy:
            old.Destroy()
        if repack:
            self.Layout()
            self.Repack()

    def Pack(self):
        if not self._packed:
            self.SetSizerAndFit(self.sizer)
            self._packed = 1

    def Repack(self):
        self.sizer.RecalcSizes()

    def GetOrientation(self):
        """ Return 'horizontal' or 'vertical'. """
        orientation = self.sizer.GetOrientation()
        if orientation == wx.HORIZONTAL:
            return 'horizontal'
        elif orientation == wx.VERTICAL:
            return 'vertical'
        else:
            raise ValueError, "Unknown direction for sizer"
            
    def GetSizerItems(self):
        """ Return a list of the object handled by the container's sizer, in 
            the order used by the sizer (which is not necessarily the same
            as the order returned by GetChildren()). """
        objects = []
        idx = 0
        while True:
            try:
                sizeritem = self.sizer.GetItem(idx)
            except:
                break
            if sizeritem is None:
                break 
                # on some systems (e.g. Ubuntu) this returns None rather than
                # raising an exception
            objects.append(sizeritem.GetWindow())
            idx = idx + 1
        return objects
        
    def GetSizerItem(self, idx):
        """ Get the <idx>-th object in the list returned by GetSizerItems. """
        objects = self.GetSizerItems()
        try:
            return objects[idx]
        except IndexError:
            raise IndexError, "Sizer has no object at index #%s" % (idx,)
    
    def GetSizerObjectIndex(self, obj):
        """ Get the index of <obj> in the list returned by GetSizerItems. """
        objects = self.GetSizerItems()
        try:
            idx = objects.index(obj)
        except IndexError:
            idx = -1
        return idx


#
# GridContainer (used to implement GridPanel)

class GridContainer(Container):

    _sizerclass = wx.GridSizer

    alignment = {
        'b': wx.ALIGN_BOTTOM,
        'r': wx.ALIGN_RIGHT,
        'l': wx.ALIGN_LEFT,
        'c': wx.ALIGN_CENTER,
        't': wx.ALIGN_TOP,
        'h': wx.ALIGN_CENTER_HORIZONTAL,
        'v': wx.ALIGN_CENTER_VERTICAL,
    }

    def _create_sizer(self, rows, cols, hgap=1, vgap=1):
        self.sizer = self._sizerclass(rows, cols, vgap, hgap)
        self.controls = {}
        for row in range(rows):
            for col in range(cols):
                self.controls[col, row] = None
                # (col, row) allows for (x, y)-like calling
        self._packed = 0

    def AddComponent(self, col, row, obj, expand=1, align='', border=0, stretch=0, proportion=0):
        # make sure the parents are correct
        if waxconfig.WaxConfig.check_parent:
            if obj.GetParent() is not self:
                utils.parent_warning(obj, self)

        if stretch:
            warnings.warn("stretch is deprecated and has no effect here")

        if self.controls[col, row]:
            raise ValueError, "A control has already been set for position (%s, %s)" % (row, col)
        self.controls[col, row] = {'obj': obj, 'expand': expand, 'align': align,
                                   'border': border, 'proportion': proportion}

    def Pack(self):
        if not self._packed:
            controls = self._AllControls()
            self.sizer.AddMany(controls)
            self.SetSizerAndFit(self.sizer) # is this still necessary?
            self._packed = 1

    def __setitem__(self, index, value):
        col, row = index
        self.AddComponent(col, row, value)

    def __getitem__(self, index):
        col, row = index
        return self.controls[col, row]['obj']  # may raise KeyError

    def _AllControls(self):
        controls = []
        for row in range(self.sizer.GetRows()):
            for col in range(self.sizer.GetCols()):
                d = self.controls[col, row]
                if d is None:
                    from panel import Panel
                    p = Panel(self) # hack up a dummy panel
                    controls.append((p, 0, wx.EXPAND|wx.FIXED_MINSIZE))
                else:
                    obj = d['obj']

                    # set alignment
                    align = d['align'].lower()
                    alignment = 0
                    for key, value in self.__class__.alignment.items():
                        if key in align:
                            alignment |= value

                    z = d['expand'] and wx.EXPAND
                    z |= alignment
                    border = d['border']
                    #if border and not alignment:
                    if border:
                        z |= wx.ALL
                    z |= wx.FIXED_MINSIZE
                    proportion = d['proportion']
                    controls.append((obj, proportion, z, border))

        return controls

    # XXX maybe a Wax version of AddMany() would be useful?

#
# FlexGridContainer

class FlexGridContainer(GridContainer):
    _sizerclass = wx.FlexGridSizer

    def AddGrowableRow(self, row):
        self.sizer.AddGrowableRow(row)

    def AddGrowableCol(self, col):
        self.sizer.AddGrowableCol(col)

#
# OverlayContainer

class OverlaySizer(wx.PySizer):
    def __init__(self):
        wx.PySizer.__init__(self)

    def CalcMin(self):
        maxx, maxy = 0, 0
        for win in self.GetChildren():
            x, y = win.CalcMin()
            maxx = max(maxx, x)
            maxy = max(maxy, y)
        return wx.Size(maxx, maxy)

    def RecalcSizes(self):
        pos = self.GetPosition()
        size = self.GetSize()
        for win in self.GetChildren():
            win.SetDimension(pos, size)


class OverlayContainer(Container):
    """ Container that takes an arbitrary number of windows, and stacks them
        on top of each other.  Controls are hidden by default. """

    def _create_sizer(self):
        self.sizer = OverlaySizer()
        self.windows = []
        self._packed = 0

    def AddComponent(self, window, expand=0, stretch=0, align=None, border=0):
        Container.AddComponent(self, window, expand=expand, stretch=stretch, 
         align=align, border=border)
        self.windows.append(window)
        window.Hide()   # default is hiding

    

#
# GroupBoxContainer

class GroupBoxContainer(Container):

    def _create_sizer(self, groupbox, direction='h'):
        direction = direction.lower()
        if direction.startswith('v'):
            dir = wx.VERTICAL
        elif direction.startswith('h'):
            dir = wx.HORIZONTAL
        else:
            raise ValueError, "Unknown direction: %s" % (direction,)

        self.sizer = wx.StaticBoxSizer(groupbox, dir)
        self._packed = 0

#
# PlainContainer

class PlainContainer(Container):
    """ A container without a sizer.  Controls must be added at a given position.
        Size can be specified as well.
    """

    def _create_sizer(self):
        self.sizer = None
        self._packed = 0    # included for compatibility

    def AddComponent(self, x, y, comp):
        # make sure the parents are correct
        if waxconfig.WaxConfig.check_parent:
            if comp.GetParent() is not self:
                utils.parent_warning(comp, self)

        comp.SetPosition((x, y))

    def AddComponentAndSize(self, x, y, sx, sy, comp):
        # make sure the parents are correct
        if waxconfig.WaxConfig.check_parent:
            if comp.GetParent() is not self:
                utils.parent_warning(comp, self)

        comp.SetPosition((x, y))
        comp.SetSize((sx, sy))

    def Pack(self):
        self._packed = 1    # useless, but included for compatibility

        if len(self.Children) == 1:
            import panel
            dummy = panel.Panel(self, size=(0,0))
            dummy.Position = 0, 0
            self.__dummy = dummy

    def Repack():
        pass

