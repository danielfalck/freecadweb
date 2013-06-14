#!/usr/bin/env python

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

import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import SpringMaker 

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class BoxPageHandler(tornado.web.RequestHandler):
    def post(self):
        d = self.get_argument('diameter')
        l = self.get_argument('length')
        p = self.get_argument('pitch')
        wd = self.get_argument('wire_dia')
        #self.render('box.html', wide=w,boxlen=l,tall=h)
        self.output = SpringMaker.drawsolid(float(d),float(l),float(p),float(wd))
        self.write(self.output)

if __name__ == "__main__":
    tornado.options.parse_command_line()

    app = tornado.web.Application(handlers=[(r"/", IndexHandler), (r'/spring', BoxPageHandler)],template_path=os.path.join(os.path.dirname(__file__), "templates"))

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
