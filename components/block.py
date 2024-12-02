from cmu_graphics import *

class Block:
    def __init__(self, x, y, width, height, text=None, type=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type
        self.text = text if text is not None else ''

    def draw(self):
        if self.type not in ['input', 'output']:
            dims = [
                self.x, self.y,
                self.x + 10, self.y,
                self.x + 17, self.y + 8,
                self.x + 43, self.y + 8,
                self.x + 50, self.y,
                self.x + self.width, self.y,
                self.x + self.width, self.y + self.height,
                self.x + 50, self.y + self.height, 
                self.x + 43, self.y + 8 + self.height, 
                self.x + 17, self.y + 8 + self.height,
                self.x + 10, self.y + self.height,
                self.x, self.y + self.height
            ]

        elif self.type == 'input':
            dims = [
                self.x, self.y,
                self.x + self.width, self.y,
                self.x + self.width, self.y + self.height,
                self.x + 50, self.y + self.height, 
                self.x + 43, self.y + 8 + self.height, 
                self.x + 17, self.y + 8 + self.height,
                self.x + 10, self.y + self.height,
                self.x, self.y + self.height
            ]            
        
        else:
            dims = [
                self.x, self.y,
                self.x + 10, self.y,
                self.x + 17, self.y + 8,
                self.x + 43, self.y + 8,
                self.x + 50, self.y,
                self.x + self.width, self.y,
                self.x + self.width, self.y + self.height,
                self.x, self.y + self.height
            ]

        drawPolygon(*dims, fill=rgb(80,148,252), border='black')        
        drawLabel(self.text, self.x+self.width//2, self.y+self.height//2, align='center', font='times', size=16)

    def contains(self, x, y):
        # Take smaller inner rectangle
        return (self.x <= x <= self.x+self.width) and (self.y+8 <= y <= self.y+self.height)