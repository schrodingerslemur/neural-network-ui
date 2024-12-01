from cmu_graphics import *
import math

def onAppStart(app):
    app.width, app.height = 1366, 768

    app.buttons = createButtons() # list of buttons (should not be empty)
    
    # test1 = Icon(33,160,180,40,'test')
    app.icons = [] # starts empty

    app.draggedIcon = None
    app.selectedIcon = None
    app.counter = 0
    app.threshold = 15

# Classes --------------
def createButtons():
    return [ 
        Button(33,90,180,40,'Input',type='input'),
        Button(33,150,180,40,'Output',type='output'),
        Button(33,210,180,40,'MLP'),
        Button(33,270,180,40,'CNN'),
        Button(33,330,180,40,'RNN'),
        Button(33,390,180,40,'GNN'),
        Button(33,450,180,40,'Transformer')
    ]

class Button:
    def __init__(self, x, y, width, height, text, type=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.type = type

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

        drawPolygon(*dims, fill=rgb(80,148,252))        
        drawLabel(self.text, self.x+self.width//2, self.y+self.height//2, align='center', font='times', size=16)

    def contains(self, x, y):
        # Take smaller inner rectangle
        return (self.x <= x <= self.x+self.width) and (self.y+8 <= y <= self.y+self.height)
    
class Icon(Button):
    def __init__(self, x, y, width, height, text, type):
        super().__init__(x, y, width, height, text, type=type)
        self.dragOffsetX = 0 
        self.dragOffsetY = 0 

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

    def isNearTop(self, other, app):
        # Other is on top
        if distance(self.x, self.y, other.x, other.y+other.height) <= app.threshold:
            if other.type != 'output':
                return True
    
    def isNearBottom(self, other, app):
        # Other is on bottom
        if distance(self.x, self.y+self.height, other.x, other.y) <= app.threshold:
            if other.type != 'input':
                return True     

class CompositeIcon():
    def __init__(self, icons):
        self.icons = icons
        self.dragOffsetX = 0
        self.dragOffsetY = 0
    
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
        
    def addIcon(self, icon, position):
        if position == 'top':
            icon.x = self.icons[0].x
            icon.y = self.icons[0].y - icon.height
            self.icons.insert(0,icon)
        elif position == 'bottom':
            icon.x = self.icons[-1].x
            icon.y = self.icons[-1].y + self.icons[-1].height
            self.icons.append(icon)

    def contains(self, mouseX, mouseY):
        return self.icons[0].contains(mouseX, mouseY)

def createIcon(button):
    return Icon(button.x, button.y, button.width, button.height, button.text, button.type)

def distance(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

# ----------------------
def onMousePress(app, mouseX, mouseY):
    # Check if the mouse is over an existing icon
    for icon in app.icons:
        if icon.contains(mouseX, mouseY):
            app.draggedIcon = icon
            app.draggedIcon.startDrag(mouseX, mouseY)
            return

    # Check if the mouse is over a button to create a new icon
    for button in app.buttons:
        if button.contains(mouseX, mouseY):
            newIcon = createIcon(button)
            app.icons.append(newIcon)
            app.draggedIcon = newIcon
            app.draggedIcon.startDrag(mouseX, mouseY)
            return

def onMouseDrag(app, mouseX, mouseY):
    # If icon is already being dragged
    if app.draggedIcon:
        app.draggedIcon.drag(mouseX, mouseY)
        return

def onMouseMove(app, mouseX, mouseY):
    pass

def onMouseRelease(app, mouseX, mouseY):
    if app.draggedIcon:
        for icon in app.icons:
            if icon is not app.draggedIcon:
                if app.draggedIcon.isNearTop(icon, app):
                    print('true')
                    if isinstance(icon, CompositeIcon):
                        icon.addIcon(app.draggedIcon, 'top')
                    else:
                        # create new composite
                        composite = CompositeIcon([app.draggedIcon, icon])
                        app.icons.remove(icon)
                        app.icons.append(composite)
                    break
                elif app.draggedIcon.isNearBottom(icon, app):
                    print('yes')
                    if isinstance(icon, CompositeIcon):
                        icon.addIcon(app.draggedIcon, 'bottom')
                    else:
                        # create new composite
                        composite = CompositeIcon([icon, app.draggedIcon])
                        app.icons.remove(icon)
                        app.icons.append(composite)
                    break
            break
    app.draggedIcon = None

def onKeyPress(app, key):
    pass

def onKeyRelease(app, key):
    pass

def onKeyHold(app, key):
    pass

def onStep(app):
    app.counter += 1

    if app.counter % 100 == 0:
        print(app.icons)

def redrawAll(app):
    drawBackground(app)
    drawHeader(app)
    drawButtons(app)
    drawIcons(app)

## Additional functions
def drawHeader(app):
    drawLabel(
        'Neural Net UI',20,25,bold=True,font='helvetica',size=25,align='top-left'
    ) # Insert logo instead

def drawBackground(app):
    drawRect(0,0,app.width,70,fill=rgb(136,92,212)) # header background
    drawRect(0,70,250,app.height-70,fill=rgb(232,244,252)) # block background
    drawRect(app.width-400,70,400,app.height-70,fill=rgb(217,227,242)) # parameter background

def drawButtons(app):
    for button in app.buttons:
        button.draw()
    
def drawIcons(app):
    for icon in app.icons:
        if isinstance(icon, CompositeIcon):
            for subIcon in icon.icons:
                subIcon.draw()
        else:
            icon.draw()

def main():
    runApp()

if __name__ == '__main__':
    main()