#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2013                                                    *  
#*   Daniel Falck <ddfalck@gmail.com>                                      *
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

'''functions for drawing a spring for a web page '''
import sys
#sys.path.append(FREECADPATH) #set your (FREECADPATH) in your system
# something like "FREECADPATH='/usr/lib/freecad/lib/' " might work in linux ymmv
# you can also hard code the path, in place of FREECADPATH
sys.path.append('/usr/local/lib/')
import FreeCAD, Part 
import exportWebGL

def drawsolid(d,l,p,wd):
    pitch = p; height= l; radius = d/2.0;barradius = wd/2
    myhelix=Part.makeHelix(pitch,height,radius)
    g=myhelix.Edges[0].Curve
    c=Part.Circle()
    c.Center=g.value(0) # start point of the helix
    c.Axis=(0,1,0)
    c.Radius=barradius
    p=c.toShape()
    section = Part.Wire([p])
    makeSolid=True
    isFrenet=True
    myspring=Part.Wire(myhelix).makePipeShell([section],makeSolid,True)
    
    solidlist= [myspring]
    result = ''
    result+= exportWebGL.getHTML(solidlist)
    return result
