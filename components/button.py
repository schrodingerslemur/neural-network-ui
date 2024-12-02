from cmu_graphics import *

class circleButton:
    def __init__(self, x, y, radius, func=None, param=None, text=None, url=None, label=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.text = text
        self.url = url
        self.func = func
        self.param = param
        self.label = label
    
    def draw(self):
        drawCircle(self.x, self.y, self.radius, fill='yellow', border='black')
        if self.url is None:
            drawLabel(self.text, self.x, self.y, align='center', bold=True, size=20)
        else:
            drawImage(self.url, self.x, self.y, width=self.radius*2-5, height=self.radius*2-5, align='center')
        if self.label:
            drawLabel(self.text, self.x, self.y+self.radius+7, align='center', bold=True)

    def contains(self, x, y):
        return distance(x,y,self.x,self.y) <= self.radius
    
    def pressed(self):
        if self.func is not None:
            if self.param is not None:
                self.func(self.param)
            else:
                self.func()

class dropdownButton:
    def __init__(self, x, y, width, height, options, default_option=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected_option = default_option if default_option else options[0]
        self.is_open = False
        self.option_height = height

    def draw(self):
        drawRect(self.x, self.y, self.width, self.height, fill='lightgrey', border='black')
        drawLabel(self.selected_option, self.x + self.width // 2, self.y + self.height // 2, align='center')
        triangle_x = self.x + self.width - 20
        triangle_y = self.y + self.height // 2
        drawPolygon(
            triangle_x, triangle_y - 5,
            triangle_x + 10, triangle_y,
            triangle_x, triangle_y + 5,
            fill='black'
        )
        if self.is_open:
            for i, option in enumerate(self.options):
                option_y = self.y + (i + 1) * self.height
                drawRect(self.x, option_y, self.width, self.option_height, fill='white', border='black')
                drawLabel(option, self.x + self.width // 2, option_y + self.option_height // 2, align='center')

    def contains(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def optionContains(self, x, y):
        if not self.is_open:
            return None
        for i, option in enumerate(self.options):
            option_y = self.y + (i + 1) * self.height
            if self.x <= x <= self.x + self.width and option_y <= y <= option_y + self.option_height:
                return option
        return None

    def toggle(self):
        self.is_open = not self.is_open

    def close(self):
        self.is_open = False

    def selectOption(self, option):
        self.selected_option = option
        self.close()