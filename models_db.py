import sqlite3

dbconn = sqlite3.connect('db.sqlite3')
cursor = dbconn.cursor()
cursor.execute('''DROP TABLE things''')
cursor.execute('''DROP TABLE stock''')
cursor.execute('''CREATE TABLE if not exists things (pk INTEGER PRIMARY KEY, name TEXT UNIQUE, img TEXT)''')
cursor.execute('''CREATE TABLE if not exists stock (pk INTEGER PRIMARY KEY, xy TEXT, name TEXT, count INTEGER, UNIQUE (xy, name))''')
dbconn.commit()

class Thing():
    
    def __init__(self, name, img):
        self.name = name
        self.img = img

    def __repr__(self):
        return self.name

    def save(self):
        cursor.execute('''INSERT OR IGNORE INTO things (name, img) values ('{0}', '{1}')'''.format(self.name, self.img))
        dbconn.commit()
        


class Stock():

    def __init__(self, x, y):
        self.x = 0
        self.y = 0
        self.things = [[ [] for i in range(x)] for g in range(y)]

    def __str__(self):
        cursor.execute("""SELECT * FROM stock""")
        rows = cursor.fetchall()
        if rows:
            return '\n'.join('{} {} {} {}'.format(*row) for row in rows)
        else:
            return 'Empty'

    def __repr__(self):
        return self.things
    
    def count_thing(self, thing, x, y):
        cursor.execute("""SELECT count(pk) FROM stock WHERE  xy='{0}{1}' AND name='{2}'""".format(x, y, thing.name))
        count = cursor.fetchone()[0]
        print('Count: {}'.format(count))
        return count

    def put_one(self, thing, x, y):
        #DB
        count = self.count_thing(thing, x, y)
        if count == 0:
            cursor.execute('''INSERT INTO stock (xy, name, count) values ('{0}{1}', '{2}', {3})'''.format(x, y, thing.name, 1))
            dbconn.commit()
        else:
            cursor.execute("""UPDATE stock SET count={0} WHERE xy='{1}{2}' AND name='{3}'""".format(count + 1, x, y, thing.name))
            dbconn.commit()

    def delete_one(self, thing, x, y):
        #DB
        count = self.count_thing(thing, x, y)
        if count < 2:
            cursor.execute("""DELETE FROM stock WHERE xy='{0}{1}' AND name='{2}'""".format(x, y, thing.name))
            dbconn.commit()
        else:
            cursor.execute("""UPDATE stock SET count={0} WHERE xy='{1}{2}' AND name='{3}'""".format(count - 1, x, y, thing.name))
            dbconn.commit()

    def put_many(self, things, x, y): 
        for thing in things:
            self.put_one(thing, x, y)

    def delete_many(self, things, x, y): 
        for thing in things:
            self.delete_one(thing, x, y)
        
    def move(self, x_from, y_from, x_to, y_to):
        cursor.execute("""UPDATE stock SET xy={0}{1} WHERE xy='{1}{2}'""".format(x_to, y_to, x_from, y_from))
        dbconn.commit()
    

if __name__ == '__main__':

    apple = Thing('apple', 'apple.jpg')
    apple.save()
    banana = Thing('banana', 'banana.jpg')
    banana.save()
    stock = Stock(3, 3)
    print('First apple')
    stock.put_one(apple, 0, 2)
    print('Second apple')
    stock.put_one(apple, 0, 2)
    print('First banana')
    stock.put_one(banana, 0, 2)
    print('Delete banana')
    stock.delete_one(banana, 0, 2)
    print('Delete apple')
    stock.delete_one(apple, 0, 2)
    print('Put many: banana, apple, banana')
    stock.put_many([banana, apple, banana], 0, 2)
    #print('Delete many: banana, apple, banana')
    #stock.delete_many([apple, apple, banana], 0, 2)
    print('Move: banana, apple, banana')
    stock.move(0, 2, 1, 2)
    print(stock)
