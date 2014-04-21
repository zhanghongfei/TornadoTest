#coding: utf-8

import time

from tornado.web import RequestHandler, Application
import tornado.httpserver
import tornado.ioloop
import tornado.httpclient

from tornado.options import define, options, parse_command_line

define("port", default=8000, help="run on the given port", type=int)

class SleepHandler(RequestHandler):
    def get(self):
        time.sleep(5)
        self.write("when i sleep 5s")

class JustNowHandler(RequestHandler):
    def get(self):
        self.write("i hope just now see you")


class TestApp(Application):

    def __init__(self):

        handlers=[
            (r"/sleep", SleepHandler),
            (r"/justnow", JustNowHandler),
        ]
        print 'Support url:'
        print '\n'.join([i[0] for i in handlers])

        Application.__init__(self, handlers)

if __name__ == "__main__":

    parse_command_line()
    print 'Starting Tornado web server on http://localhost:%s' % options.port
    app = TestApp()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
