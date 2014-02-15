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
import tornado
import tornado.ioloop
import tornado.web
import os
import StringIO
import drawit

class Userform(tornado.web.RequestHandler):
    def get(self):
        self.render("fileuploadform.html")

class Upload(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        if extn in ('.fcstd','FCStd'):
            fh = StringIO.StringIO()
            fh.write(fileinfo['body'])
            self.finish(drawit.makedrawing(fh))
            fh.close()
        else:
            self.finish("please upload a FreeCAD *.fcstd file!")

application = tornado.web.Application([
        (r"/", Userform),
        (r"/upload", Upload),
        ], debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
