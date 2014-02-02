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
# you can also hard insert the value here, in place of FREECADPATH
import time
import zipfile
from xml.dom import minidom
import FreeCAD as App
from FreeCAD import Base

import Part
import Drawing
import math

def getActiveObjs(docobj):
    '''Pass a FreeCAD.ActiveDocument object to this function and 
    receive back a list of the visible objects.'''
    filename = docobj.FileName
    print filename
    zfile = zipfile.ZipFile(filename)
    guidata = zfile.read('GuiDocument.xml')
    xmlgui =minidom.parseString(guidata)
    objlist = []
    itemlist = xmlgui.getElementsByTagName('ViewProvider') 
    for s in itemlist :
        for i in s.childNodes:
            for j in i.childNodes:
                if j.attributes:
                    if j.attributes['name'].value == 'Visibility':
                        for b in j.childNodes:
                            if b.nodeName == 'Bool':
                                if b.attributes['value'].value == 'true':
                                    objlist.append(s.attributes['name'].value)

    return objlist

def diagcenter(obj  ):
    '''return the diagonal distance between corners
       and center of a FreeCAD Compound object-ie something 
       that is made from several objects'''
    xmax = obj.OutList[0].Shape.BoundBox.XMax
    xmin = obj.OutList[0].Shape.BoundBox.XMin
    ymax = obj.OutList[0].Shape.BoundBox.YMax
    ymin = obj.OutList[0].Shape.BoundBox.YMin
    zmax = obj.OutList[0].Shape.BoundBox.ZMax
    zmin = obj.OutList[0].Shape.BoundBox.ZMin

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
    #print xmax,"  ",  ymax,"  ", zmax
    #print xmin,"  ",  ymin,"  ", zmin
    #print v0,"  ", v1
    #print vdiff
    #print "Diagonal of bounding box = ", bblength
    #print "Center of bounding box = ", vdiff.multiply(.5)

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

def makedrawing(cname):
    time.sleep(2.0)
    App.open(cname)
    doc = App.ActiveDocument
    #get all visible objects in document
    #hopefully they are solid shapes (shape checking to come)
    objs = getActiveObjs(doc)

    #convert unicode names into FreeCAD objects
    activelist = []
    for o in objs:
        activelist.append(doc.getObject(o))

    doc.addObject("Part::Compound","Compound")
    doc.Compound.Links = activelist
    obj = doc.getObject("Compound")

#set up the drawing page
    myPage=doc.addObject("Drawing::FeaturePage","Page")
    #myPage.Template = App.getResourceDir()+'Mod/Drawing/Templates/A3_Landscape.svg'
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
    myPage.EditableTexts = [unicode('D. FALCK', 'utf-8'),unicode('01/25/14', 'utf-8'),unicode('SLIPTONIC', 'utf-8'),unicode('01/25/14', 'utf-8'),unicode('1:2.5', 'utf-8'),unicode('3.75', 'utf-8'),unicode('F20140125-1', 'utf-8'),unicode('1', 'utf-8'),unicode('ROBOT COUPLER', 'utf-8'),unicode('A COOL PART', 'utf-8'),]

    doc.recompute()

#return the svg string
    PageFile = open(App.activeDocument().Page.PageResult,'r')
    App.closeDocument(doc.Name)
    return PageFile.read()


