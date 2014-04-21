#coding: utf-8
'''
    Blog: http://lbolla.info/blog/2013/01/22/blocking-tornado
    tornado 中的阻塞请求的解决方案:
      1. 优化请求， 比如数据库的慢查询
      2. 在一个单独的线程或者进程中执行慢的任务
         这意味着将任务卸载到一个不同的线程(或过程)的运行IOLoop
        然后空闲接受其他请求
      3. 用  asynchronous driver/library 去执行任务 例如 gevent, motor
    本文针对第二个

    用到的包 python 并发:
        https://docs.python.org/3/library/concurrent.futures.html#module-concurrent.futures
'''

import time

from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps

import tornado.ioloop
from tornado.web import RequestHandler, \
                        Application, \
                        asynchronous

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)


EXECUTOR = ThreadPoolExecutor(max_workers=4)

def unblock(func):
 
    @tornado.web.asynchronous
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
 
        def callback(future):
            self.write(future.result())
            self.finish()
 
        EXECUTOR.submit(
            partial(func, *args, **kwargs)
        ).add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                partial(callback, future)))
 
    return wrapper


class SleepHandler(RequestHandler):

    @unblock
    def get(self):
        time.sleep(5)
        return 'when i sleep 5s!!'

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

    print 'Starting Tornado web server on http://localhost:%s' % options.port
    app = TestApp()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
