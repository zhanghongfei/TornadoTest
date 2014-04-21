#coding: utf-8
'''
    异步非阻塞式回应
    当请求 /sleep 之后马上请求 /justnow 时
    不需要等待/sleep 返回结果后 /justnow 才相应
'''

import time

from tornado.web import RequestHandler, \
                        Application, \
                        asynchronous
from tornado.gen import coroutine, \
                        Task

from tornado.concurrent import run_on_executor
import tornado.ioloop

from tornado.options import define, options

from concurrent.futures import ThreadPoolExecutor

define("port", default=8000, help="run on the given port", type=int)

class SleepTwoHandler(RequestHandler):

    executor = ThreadPoolExecutor(1)

    @run_on_executor
    def _sleep(self, second):
        time.sleep(second)
        return second

    @asynchronous
    @coroutine
    def get(self):
        res = yield self._sleep(6)
        self.write("When i sleep %s s" % res)


class SleepHandler(RequestHandler):

    @asynchronous
    @coroutine
    def get(self):
        # Task(function, args)
        yield Task(tornado.ioloop.IOLoop.instance().add_timeout ,time.time()+5)
        self.write("when i sleep 5s")

    # coroutine 是3.0 之后增加的装饰器在 3.0 之前需要这样...
    #@asynchronous
    #def get(self):
    #    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 5, callback=self.on_response)
    #def on_response(self):
    #    self.write("when i sleep 5s")
    #    self.finish()

class JustNowHandler(RequestHandler):
    def get(self):
        self.write("i hope just now see you")


class TestApp(Application):

    def __init__(self):

        handlers=[
            (r"/sleep", SleepHandler),
            (r"/sleeptwo", SleepTwoHandler),
            (r"/justnow", JustNowHandler),
        ]
        print 'Support url:'
        print '\n'.join([i[0] for i in handlers])

        Application.__init__(self, handlers)

if __name__ == "__main__":

    print 'Starting Tornado web server on http://localhost:%s' % options.port
    app = TestApp()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
