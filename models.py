class Thing():
    
    def __init__(self, name, img):
        self.name = name
        self.img = img

    def __repr__(self):
        return self.name


class Stock():

    def __init__(self, x, y):
        self.x = 0
        self.y = 0
        self.things = [[ [] for i in range(x)] for g in range(y)]

    def __str__(self):
        pass

    def __repr__(self):
        return self.things
    
    def put_one(self, thing, x, y):
        cell = self.things[x][y]
        cell.append(thing)

    def delete_one(self, thing, x, y):
        cell = self.things[x][y]
        # If name match, remove thing
        for item in cell:
            if item.name == thing.name:
                cell.remove(item)

    def put_many(self, things, x, y): 
        for thing in things:
            self.put_one(thing, x, y)

    def delete_many(self, things, x, y): 
        for thing in things:
            self.delete_one(thing, x, y)
        
    def delete_all(self, x, y): 
        cell = self.things[x][y]
        cell = []

    def move(self, things, x_from, y_from, x_to, y_to):
        self.delete_many(things, x_from, y_from)
        self.put_many(things, x_to, y_to)
    

if __name__ == '__main__':

    apple = Thing('apple', 'apple.jpg')
    banana = Thing('banana', 'banana.jpg')
    stock = Stock(3, 4)
    stock.put_one(apple, 0, 2)
    stock.put_one(apple, 0, 2)
    stock.put_one(banana, 0, 2)
    stock.delete_one(banana, 0, 2)
    stock.delete_one(apple, 0, 2)
    stock.delete_many([apple, apple, banana], 0, 2)
    stock.put_many([banana, apple, banana], 0, 2)
    print(stock.things)
    stock.move([banana, apple, banana], 0, 2, 1, 2)
    print(stock.things)
    
