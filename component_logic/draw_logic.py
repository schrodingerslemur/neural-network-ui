from cmu_graphics import *

from components.icon import CompositeIcon

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
    pass
