#!/usr/bin/python3
import os
import json
import sqlite3
import time
import tornado.web
import tornado.httpserver
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.options import options, define

from models import Thing, Stock, Item

define("host", default="localhost", help="app host", type=str)
define("port", default=8080, help="app port", type=int)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

connections = set() 
  
#Ininial data
dbconn = sqlite3.connect('db.sqlite3')
cursor = dbconn.cursor()
cursor.execute('''CREATE TABLE if not exists things (pk INTEGER PRIMARY KEY, 
                name TEXT UNIQUE, img TEXT)''')
cursor.execute('''CREATE TABLE if not exists items 
                (pk INTEGER PRIMARY KEY, x INTEGER, y INTEGER, name TEXT, count INTEGER, UNIQUE (x, y, name))''')
cursor.execute('''DELETE FROM things''')
cursor.execute('''DELETE FROM items''')
dbconn.commit()
apple = Thing('apple', '/media/img/apple.png')
banana = Thing('banana', '/media/img/banana.png')
apple.create(cursor, dbconn)
banana.create(cursor, dbconn)
stock = Stock(3, 3, ['banana', 'apple'])
images = {}
[ images.setdefault(i.name, i.img) for i in [apple, banana] ]
[i.create(cursor, dbconn) for i in stock]

class WebSocketHandler(WebSocketHandler):

    # accept all cross-origin traffic
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in connections:
            connections.add(self)
        msg = json.dumps({ 'action' : 'init', 'xy' : stock.cells, 'fruits': stock.fruits, 'images': images })
        [con.write_message(msg) for con in connections]

    def on_message(self, message):
        data = json.loads(message)
        if data['action'] == 'put':
            to = data['pk']
            name = data['name']
            x, y = map(int, list(to))
            #Get obj
            item = Item.from_db(cursor, dbconn, x, y, name)
            #Put 1 thing
            item.count = item.count + 1
            #Update
            item.update(cursor, dbconn)
            #Check db again!
            item = Item.from_db(cursor, dbconn, x, y, name)
            msg = json.dumps({ 'action' : 'put', 'to': to, 'name': name, 'count': item.count})
            print(msg)
            [con.write_message(msg) for con in connections]
        if data['action'] == 'move':
            from_pk = data['from']
            to = data['to']
            name = data['name']
            x_to, y_to = map(int, list(to))
            x_from, y_from = map(int, list(from_pk))
            #Get obj
            item_to = Item.from_db(cursor, dbconn, x_to, y_to, name)
            item_from = Item.from_db(cursor, dbconn, x_from, y_from, name)
            #Move from to
            item_to.count = item_to.count + item_from.count
            item_from.count = 0
            #Update
            item_to.update(cursor, dbconn)
            item_from.update(cursor, dbconn)
            #Check db again 
            item_to = Item.from_db(cursor, dbconn, x_to, y_to, name)
            item_from = Item.from_db(cursor, dbconn, x_from, y_from, name)
            msg = json.dumps({ 'action' : 'move', 'to': to, 'from': from_pk,
                               'to_count': item_to.count, 'from_count': item_from.count,  'name': name})
            print(msg)
            [con.write_message(msg) for con in connections]
        if data['action'] == 'delete':
            to = data['pk']
            name = data['name']
            x, y = map(int, list(to))
            #Get obj
            item = Item.from_db(cursor, dbconn, x, y, name)
            #Delete one
            if item.count > 0:
                item.count = item.count - 1
            #Update
            item.update(cursor, dbconn)
            #Check db again!
            item = Item.from_db(cursor, dbconn, x, y, name)
            msg = json.dumps({ 'action' : 'put', 'to': to, 'name': name, 'count': item.count})
            print(msg)
            [con.write_message(msg) for con in connections]

            [con.write_message(msg) for con in connections]

    def on_close(self):
        connections.remove(self)
 

class IndexPageHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html",
            x_max=stock.x_max,
            server_url=options.host,
            server_port=options.port
        )
       
class Application(tornado.web.Application):

    def __init__(self):
        settings = {
            'template_path': 'templates',
            "static_path": os.path.join(BASE_DIR, 'static'),
            "media_path": os.path.join(BASE_DIR, 'media'),
        }

        handlers = [
            (r'/', IndexPageHandler),
            (r'/socket', WebSocketHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
            (r'/media/(.*)', tornado.web.StaticFileHandler, {'path': settings['media_path']}),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
 
 
if __name__ == '__main__':
    options.parse_command_line()
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(options.port)
    IOLoop.instance().start()
