#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2013 Daniel Falck  <ddfalck@gmail.com>                  *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************
import sys
#sys.path.append(FREECADPATH) #set your (FREECADPATH) in your system
# something like "FREECADPATH='/usr/lib/freecad/lib/' " might work in linux ymmv
# you can also hard code the path, in place of FREECADPATH
sys.path.append('/usr/local/lib/')
import FreeCAD as App
from FreeCAD import Base
import Part
import Drawing
import zipfile
import xml.etree.ElementTree as ET

def getActiveObjs(filename):
    '''Pass a FreeCAD file to this function and 
    receive back a list of the visible objects.'''
    zfile = zipfile.ZipFile(filename)
    #find out which objects were left visible in the saved file
    gui=zfile.read('GuiDocument.xml')
    guitree = ET.fromstring(gui)
    objlist = []
    for viewp in guitree.getiterator(tag = 'ViewProvider'):
        for elem in viewp.getiterator(tag='Properties'):
            for prop in elem.getiterator(tag='Property'):
                if prop.attrib.get('name')=='Visibility':
                   for state in prop.getiterator(tag='Bool'):
                       if state.get('value')=='true':
                            objlist.append( viewp.get('name'))
    #return objlist
    #get the Brep geometry of visible objects.
    geom=zfile.read('Document.xml')
    geotree = ET.fromstring(geom)
    filelist = []
    for elem in geotree.getiterator(tag='ObjectData'):
        for label in elem.getiterator(tag='Object'):
            if label.attrib.get('name') in (tuple(objlist)):
                for prop in label.getiterator(tag='Property'):
                    if prop.attrib.get('name') == 'Shape':
                        for part in prop.getiterator(tag='Part'):
                            filelist.append(part.attrib.get('file'))
    return filelist

def diagcenter(obj  ):
    '''return the diagonal distance between corners
    and center of a FreeCAD Compound object-ie something 
    that is made from several objects'''
    xmax = obj.Shape.BoundBox.XMax
    xmin = obj.Shape.BoundBox.XMin
    ymax = obj.Shape.BoundBox.YMax
    ymin = obj.Shape.BoundBox.YMin
    zmax = obj.Shape.BoundBox.ZMax
    zmin = obj.Shape.BoundBox.ZMin

    for o in obj.OutList:
        if o.Shape.BoundBox.XMax >= xmax:
            xmax = o.Shape.BoundBox.XMax 
        if o.Shape.BoundBox.XMin <= xmin:
            xmin = o.Shape.BoundBox.XMin
        if o.Shape.BoundBox.YMax >= ymax:
            ymax = o.Shape.BoundBox.YMax 
        if o.Shape.BoundBox.YMin <= ymin:
            ymin = o.Shape.BoundBox.YMin
        if o.Shape.BoundBox.ZMax >= zmax:
            zmax = o.Shape.BoundBox.ZMax 
        if o.Shape.BoundBox.YMin <= zmin:
            zmin = o.Shape.BoundBox.ZMin
    v0 = Base.Vector(xmin,ymin,zmin)
    v1 = Base.Vector(xmax,ymax,zmax)
    vdiff = v1.sub(v0)
    bblength = vdiff.Length
    center = vdiff.multiply(.5)
    return (bblength, center)

def makeView(doc, obj, vname, viewdir, x, y, scale, lwmod, hwmod, rotation, page ,showhidden):
    '''create a drawing view on a given page  '''
    viewname = doc.addObject('Drawing::FeatureViewPart',vname)
    viewname.Source = obj
    viewname.Direction = viewdir
    viewname.Rotation = rotation
    viewname.X = x
    viewname.Y = y
    viewname.Scale = scale
    viewname.LineWidth = lwmod
    viewname.HiddenWidth = hwmod
    if showhidden :
        viewname.ShowHiddenLines = True
    page.addObject(viewname)

def getshape(filename):
    #get all visible objects in document
    #hopefully they are solid shapes (shape checking to come)
    activebreps = getActiveObjs(filename)
    zfile=zipfile.ZipFile(filename)
    partcomp = [] #list for Part.Compound
    #pull breps out of file and make make shapes from them
    for i in activebreps:
        data=zfile.read(i)
        exec("shape%d = Part.Shape()" % (activebreps.index(i)))
        exec("shape%d.importBrepFromString(%s)" %(activebreps.index(i),repr(data)))
        partcomp.append(eval("shape%d" % (activebreps.index(i))))
    if len(partcomp)>1:
        objs = Part.Compound(partcomp)
    else:
        objs = partcomp[0]
    return objs

def makedrawing(filename):
    App.newDocument()
    App.setActiveDocument("Unnamed")
    doc = App.ActiveDocument
    doc.addObject("Part::Compound","Compound")
    doc.Compound.Shape = getshape(filename)
    obj = doc.getObject("Compound")

    #set up the drawing page
    myPage=doc.addObject("Drawing::FeaturePage","Page")
    myPage.Template = "./templates/empty_rectangle.svg"
    nviews =1 #number of views- make this 1 for a single iso view
    lwmod = .35
    scale = 2.750
    vwidth,vheight = 400, 200.0
    centerofview = Base.Vector(vwidth,vheight,0).sub(Base.Vector(0,0,0)).multiply(.5)
    diagonalofview = Base.Vector(vwidth,vheight,0).sub(Base.Vector(0,0,0)).Length
    diagofobj = diagcenter(obj  )[0]
    scale = (diagonalofview / diagofobj)*.25
    viewdir = (0,0,1)
    x = centerofview.x
    y = centerofview.y
    rotation = 0.0
    hwmod = .25
    showhidden = False
    if nviews == 4:
        #4 projected views
        makeView(doc, obj, 'view1', viewdir, x*.5, y*.5, scale, lwmod, hwmod, rotation, myPage,showhidden)
        makeView(doc, obj, 'view2', (0,1,0), x*.5, y+vheight*.25, scale, lwmod, hwmod, 90, myPage,showhidden)
        makeView(doc, obj, 'view3', (1,0,0), x+vwidth*.05, y+vheight*.25, scale, lwmod, hwmod, 180, myPage,showhidden)
        makeView(doc, obj, 'view4', (.577,.577,.577), x+vwidth*.03, y*.5, scale, lwmod, hwmod, 120, myPage,False)
    else:
        # make a single Isometric view in the middle of the page
        makeView(doc, obj, 'view4', (1,1,1), x*.5, y*.5, scale, lwmod, hwmod, 120, myPage,False)
    doc.recompute()
    #return the svg string
    PageFile = open(App.activeDocument().Page.PageResult,'r')
    App.closeDocument(doc.Name)
    return PageFile.read()

