from cmu_graphics import *
import math

def onAppStart(app):
    resetApp(app)

# Classes --------------
def resetApp(app):
    app.width, app.height = 1366, 768

    app.blocks = createBlocks() # list of blocks (should not be empty)
    app.buttons = createButtons(app)
    # test1 = Icon(33,160,180,40,'test')
    app.icons = [] # starts empty

    app.draggedIcon = None
    app.selectedIcon = None
    app.previewIcon = None
    app.counter = 0
    app.threshold = 15

def createBlocks():
    return [ 
        Block(33,90,180,40,text='Input',type='input'),
        Block(33,150,180,40,text='Output',type='output'),
        Block(33,210,180,40,text='MLP'),
        Block(33,270,180,40,text='CNN'),
        Block(33,330,180,40,text='RNN'),
        Block(33,390,180,40,text='GNN'),
        Block(33,450,180,40,text='Transformer')
    ]

def createButtons(app):
    return [
        circleButton(1320, 30, 20, func=resetApp, param=app, text='Reset', url='static/reset.png')
    ]

class circleButton:
    def __init__(self, x, y, radius, func=None, param=None, text=None, url=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.text = text
        self.url = url
        self.func = func
        self.param=param
    
    def draw(self):
        drawCircle(self.x, self.y, self.radius, fill='yellow', border='black')
        if self.url is None:
            drawLabel(self.text, self.x, self.y, align='center', bold=True, size=20)
        else:
            drawImage(self.url, self.x, self.y, width=self.radius*2-5, height=self.radius*2-5, align='center')
        
        drawLabel(self.text, self.x, self.y+self.radius+7, align='center', bold=True)

    def contains(self, x, y):
        return distance(x,y,self.x,self.y) <= self.radius
    
    def pressed(self):
        if self.func is not None:
            if self.param is not None:
                self.func(self.param)
            else:
                self.func()
    
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
    
class Icon(Block):
    def __init__(self, x, y, width, height, text, type):
        super().__init__(x, y, width, height, text, type=type)
        self.dragOffsetX = 0 
        self.dragOffsetY = 0 

        self.parameters = {}

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
        print('icons', self.icons)
        self.updatePosition()
        # self.updateIcons()

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

    def updatePosition(self):
        self.x = self.icons[0].x
        self.y = self.icons[0].y
        self.width = self.icons[0].width
        self.height = len(self.icons)*40
        print(self.x, self.y, self.width, self.height)

    def adjustPosition(self, x, y):
        xOffset = x - self.icons[0].x
        yOffset = y - self.icons[0].y

        for icon in self.icons:
            icon.x += xOffset
            icon.y += yOffset

def createIcon(block):
    return Icon(block.x, block.y, block.width, block.height, block.text, block.type)

def distance(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

# ----------------------
def onMousePress(app, mouseX, mouseY):
    for button in app.buttons:
        if button.contains(mouseX, mouseY):
            print('yes')
            button.pressed()

    # Check if the mouse is over an existing icon
    for icon in app.icons:
        if icon.contains(mouseX, mouseY):
            app.draggedIcon = icon
            app.draggedIcon.startDrag(mouseX, mouseY)

            app.selectedIcon = icon
            return

    # Check if the mouse is over a block to create a new icon
    for block in app.blocks:
        if block.contains(mouseX, mouseY):
            newIcon = createIcon(block)
            app.icons.append(newIcon)
            app.draggedIcon = newIcon
            app.draggedIcon.startDrag(mouseX, mouseY)

            app.selectedIcon = newIcon
            return

def onMouseDrag(app, mouseX, mouseY):
    if app.draggedIcon:
        app.draggedIcon.drag(mouseX, mouseY)

        # Check for potential snapping position
        for icon in app.icons:
            if icon is not app.draggedIcon:
                snapPosition = snapToTop(app, app.draggedIcon, icon)
                if snapPosition:
                    if isinstance(app.draggedIcon, CompositeIcon):
                        # Show silhouette for CompositeIcon
                        app.previewIcon = CompositeIcon(app.draggedIcon.icons.copy())
                        app.previewIcon.x, app.previewIcon.y = snapPosition
                    else:
                        # Show silhouette for single Icon
                        app.previewIcon = Icon(*snapPosition, app.draggedIcon.width, app.draggedIcon.height, app.draggedIcon.text, app.draggedIcon.type)
                    return

                snapPosition = snapToBottom(app, app.draggedIcon, icon)
                if snapPosition:
                    if isinstance(app.draggedIcon, CompositeIcon):
                        # Show silhouette for CompositeIcon
                        app.previewIcon = CompositeIcon(app.draggedIcon.icons.copy())
                        app.previewIcon.x, app.previewIcon.y = snapPosition
                    else:
                        # Show silhouette for single Icon
                        app.previewIcon = Icon(*snapPosition, app.draggedIcon.width, app.draggedIcon.height, app.draggedIcon.text, app.draggedIcon.type)
                    return

        # If no snap position, remove the preview
        app.previewIcon = None


def onMouseMove(app, mouseX, mouseY):
    pass

def onMouseRelease(app, mouseX, mouseY):
    if app.draggedIcon:
        for icon in app.icons:
            if icon is not app.draggedIcon:
                # Check for snapping to the top
                snapPosition = snapToTop(app, app.draggedIcon, icon)
                if snapPosition:
                    app.draggedIcon.x, app.draggedIcon.y = snapPosition
                    if isinstance(app.draggedIcon, CompositeIcon):
                        if isinstance(icon, CompositeIcon):
                            app.draggedIcon.adjustPosition(icon.x, icon.y-app.draggedIcon.height)
                            composite = CompositeIcon(app.draggedIcon.icons + icon.icons)
                            app.icons.remove(icon)
                            app.icons.append(composite)
                        else:
                            app.draggedIcon.adjustPosition(icon.x, icon.y-app.draggedIcon.height)
                            composite = CompositeIcon(app.draggedIcon.icons + [icon])
                            app.icons.remove(icon)
                            app.icons.append(composite)
                    elif isinstance(icon, CompositeIcon):
                        icon.addIcon(app.draggedIcon, 'top')
                    else:
                        composite = CompositeIcon([app.draggedIcon, icon])
                        app.icons.remove(icon)
                        app.icons.append(composite)
                    app.icons.remove(app.draggedIcon)
                    break

                # Check for snapping to the bottom
                snapPosition = snapToBottom(app, app.draggedIcon, icon)
                if snapPosition:
                    app.draggedIcon.x, app.draggedIcon.y = snapPosition
                    if isinstance(app.draggedIcon, CompositeIcon):
                        if isinstance(icon, CompositeIcon):
                            app.draggedIcon.adjustPosition(icon.x, icon.y+icon.height)
                            composite = CompositeIcon(icon.icons + app.draggedIcon.icons)
                            app.icons.remove(icon)
                            app.icons.append(composite)
                        else:
                            app.draggedIcon.adjustPosition(icon.x, icon.y+icon.height)
                            composite = CompositeIcon([icon] + app.draggedIcon.icons)
                            app.icons.remove(icon)
                            app.icons.append(composite)
                    elif isinstance(icon, CompositeIcon):
                        icon.addIcon(app.draggedIcon, 'bottom')
                    else:
                        composite = CompositeIcon([icon, app.draggedIcon])
                        app.icons.remove(icon)
                        app.icons.append(composite)
                    app.icons.remove(app.draggedIcon)
                    break
    app.draggedIcon = None
    app.previewIcon = None  # Clear the silhouette

def snapToBottom(app, draggedIcon, target):
    if isinstance(target, CompositeIcon):
        bottommost = target.icons[-1]
        if distance(draggedIcon.x, draggedIcon.y, bottommost.x, bottommost.y + bottommost.height) <= app.threshold:
            return bottommost.x, bottommost.y + bottommost.height
    else:
        if distance(draggedIcon.x, draggedIcon.y, target.x, target.y + target.height) <= app.threshold:
            return target.x, target.y + target.height
    return None


def snapToTop(app, draggedIcon, target):
    if isinstance(target, CompositeIcon):
        topmost = target.icons[0]
        if distance(draggedIcon.x, draggedIcon.y + draggedIcon.height, topmost.x, topmost.y) <= app.threshold:
            print(topmost.x, topmost.y - draggedIcon.height)
            print(draggedIcon.x, draggedIcon.y + draggedIcon.height)
            return topmost.x, topmost.y - draggedIcon.height
    else:
        if distance(draggedIcon.x, draggedIcon.y + draggedIcon.height, target.x, target.y) <= app.threshold:
            return target.x, target.y - draggedIcon.height
    return None


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
    if app.previewIcon:
        drawPreview(app.previewIcon)
    drawBlocks(app)
    drawButtons(app)
    drawIcons(app)


## Additional functions
def drawPreview(icon):
    dims = [
        icon.x, icon.y,
        icon.x + 10, icon.y,
        icon.x + 17, icon.y + 8,
        icon.x + 43, icon.y + 8,
        icon.x + 50, icon.y,
        icon.x + icon.width, icon.y,
        icon.x + icon.width, icon.y + icon.height,
        icon.x + 50, icon.y + icon.height, 
        icon.x + 43, icon.y + 8 + icon.height, 
        icon.x + 17, icon.y + 8 + icon.height,
        icon.x + 10, icon.y + icon.height,
        icon.x, icon.y + icon.height
    ]
    drawPolygon(*dims, fill=rgb(200, 200, 200), border='black')  # Semi-transparent fill

def drawHeader(app):
    drawLabel(
        'Neural Net UI',20,25,bold=True,font='helvetica',size=25,align='top-left'
    ) # Insert logo instead

def drawBackground(app):
    drawRect(0,0,app.width,70,fill=rgb(136,92,212)) # header background
    drawRect(0,70,250,app.height-70,fill=rgb(232,244,252)) # block background
    drawRect(app.width-400,70,400,app.height-70,fill=rgb(217,227,242)) # parameter background

def drawBlocks(app):
    for block in app.blocks:
        block.draw()
    
def drawIcons(app):
    for icon in app.icons:
        if isinstance(icon, CompositeIcon):
            for subIcon in icon.icons:
                subIcon.draw()
        else:
            icon.draw()

def drawButtons(app):
    for button in app.buttons:
        button.draw()

def drawParameter(app):
    if app.selectedIcon:
        parameters = app.selectedIcon.parameters

def main():
    runApp()

if __name__ == '__main__':
    main()