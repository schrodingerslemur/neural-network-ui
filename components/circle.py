from cmu_graphics import *

class Circle:
    def __init__(self, x, y, r):
        self.x = x 
        self.y = y
        self.r = r

    def draw(self):
        drawCircle(self.x, self.y, self.r, fill='yellow', border='black')