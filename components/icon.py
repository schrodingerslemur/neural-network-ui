from cmu_graphics import *
from components.block import Block

class Icon(Block):
    def __init__(self, x, y, width, height, text, type):
        super().__init__(x, y, width, height, text, type=type)
        self.dragOffsetX = 0 
        self.dragOffsetY = 0 

        self.net_type = self.text.lower()
        self.parameters = {
            "type": self.net_type
        }

        if self.net_type == 'mlp':
            self.parameters["dims"] = [2, 64]
            self.parameters["activations"] = [None, None]
        elif self.net_type == 'cnn':
            self.parameters["dims"] = [{
                                    "layer": "conv",
                                    "in_channels": 3,
                                    "out_channels": 16,
                                    "kernel_size": 3,
                                    "stride": 1,
                                    "padding": 0
                                }]
            self.parameters["activations"] = [None]
        elif self.net_type == 'gnn':
            pass
        elif self.net_type == 'rnn':
            pass
        elif self.net_type == 'transformer':
            pass


    def __repr__(self):
        return self.text
    
    def startDrag(self, mouseX, mouseY):
        # offset between mouse and icon
        self.dragOffsetX = mouseX - self.x
        self.dragOffsetY = mouseY - self.y

    def drag(self, mouseX, mouseY):
        # change position based on offset
        self.x = mouseX - self.dragOffsetX
        self.y = mouseY - self.dragOffsetY

class CompositeIcon():
    def __init__(self, icons):
        self.icons = icons
        self.dragOffsetX = 0
        self.dragOffsetY = 0
        self.type = None
        self.text = None
        
        self.updatePosition()

    def __repr__(self):
        return f"Composite{[str(icon) for icon in self.icons]}"
    
    def startDrag(self, mouseX, mouseY):
        firstIcon = self.icons[0]
        self.dragOffsetX = mouseX - firstIcon.x
        self.dragOffsetY = mouseY - firstIcon.y

    def drag(self, mouseX, mouseY):
        firstIcon = self.icons[0]
        deltaX = mouseX - self.dragOffsetX - firstIcon.x
        deltaY = mouseY - self.dragOffsetY - firstIcon.y

        for icon in self.icons:
            icon.x += deltaX
            icon.y += deltaY
        
        self.updatePosition()
        
    def addIcon(self, icon, position):
        if position == 'top':
            icon.x = self.icons[0].x
            icon.y = self.icons[0].y - icon.height
            self.icons.insert(0,icon)
        elif position == 'bottom':
            icon.x = self.icons[-1].x
            icon.y = self.icons[-1].y + self.icons[-1].height
            self.icons.append(icon)

        self.updatePosition()

    def contains(self, mouseX, mouseY):
        return self.icons[0].contains(mouseX, mouseY)
    
    def otherContains(self, mouseX, mouseY):
        for i in range(1,len(self.icons)):
            if self.icons[i].contains(mouseX, mouseY):
                return i
        return
        
    def updatePosition(self):
        self.x = self.icons[0].x
        self.y = self.icons[0].y
        self.width = self.icons[0].width
        self.height = len(self.icons)*40

    def adjustPosition(self, x, y):
        xOffset = x - self.icons[0].x
        yOffset = y - self.icons[0].y

        for icon in self.icons:
            icon.x += xOffset
            icon.y += yOffset
