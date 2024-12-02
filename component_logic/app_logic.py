from cmu_graphics import *

from component_logic.create_logic import createBlocks, createButtons
from app.neural_network.util.parameters import convert

def resetApp(app):
    app.width, app.height = 1366, 768

    app.blocks = createBlocks() 
    app.buttons = createButtons(app, resetApp)
    app.icons = [] # starts empty

    app.draggedIcon = None
    app.selectedIcon = None
    app.previewIcon = None
    app.counter = 0
    app.threshold = 15

    app.netFigures = []
    app.netButtons = []
    app.netDropdowns = []
    
    app.activations = convert.lists('activation', 'list')
    app.optimizers = convert.lists('optimizer', 'list')
    app.losses = convert.lists('loss', 'list')