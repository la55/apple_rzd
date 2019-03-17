class Thing():
    
    def __init__(self, name, img):
        self.name = name
        self.img = img

    def __repr__(self):
        return '{} {}'.format(self.name, self.image)

    def create(self, cursor, dbconn):
        cursor.execute('''INSERT OR IGNORE INTO things (name, img) values ('{0}', '{1}')'''.format(self.name, self.img))
        dbconn.commit()
        

class Stock():
    def __init__(self, x_max, y_max, names):
        self.x_max = x_max 
        self.y_max = y_max
        self.names = names
        self.items = [Item(x + 1, y + 1, name, 0) 
                        for x in range(x_max) for y in range(y_max) for name in names]
        self.cells = [{ 'pk': '{}{}'.format(x + 1, y + 1), 
                        'items': [{ 'name': name, 'count': 0 } for name in names] }
                        for x in range(x_max) for y in range(y_max)]
        self.fruits = [{ 'pk': '00', 'items': [{ 'name': name, 'count': 1 } for name in names] }]

    def __getitem__(self, index):
        return self.items[index]

    def __str__(self):
        return str(self.items)
    

class Item():

    def __init__(self, x, y, name, count):
        self.x = x 
        self.y = y
        self.name = name
        self.count = count

    @classmethod
    def from_db(cls, cursor, dbconn, x, y, name):
        sql = """SELECT x, y, name, count FROM items 
             WHERE x={0} AND y={1} AND name='{2}'
        """.format(x, y, name)
        cursor.execute(sql)
        one = cursor.fetchone()
        if one[0] != None:
            return cls(*one)
        return None

    def __str__(self):
        return '{} {} {} {}'.format(self.x, self.y, self.name, self.count)

    def create(self, cursor, dbconn):
        sql = """INSERT OR IGNORE INTO items
        (x, y, name, count) values ({}, {}, '{}', {})     
        """.format(self.x, self.y, self.name, self.count)
        res = cursor.execute(sql)
        dbconn.commit()
        print('created:', self)
        
    def update(self, cursor, dbconn):
        sql = """UPDATE items SET count={0}
             WHERE x={1} AND y={2} AND name='{3}'
        """.format(self.count, self.x, self.y, self.name)
        res = cursor.execute(sql)
        dbconn.commit()
        print('updated:', self)
