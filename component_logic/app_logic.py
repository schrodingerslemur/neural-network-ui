from cmu_graphics import *

from component_logic.create_logic import createBlocks, createButtons, createDropdown
from components.icon import CompositeIcon
from app.neural_network.util.parameters import convert
# from data.upload import create_ui

def resetApp(app):
    app.width, app.height = 1366, 768

    app.blocks = createBlocks() 
    app.submit = submit_func
    app.buttons = createButtons(app, resetApp)
    app.dropdowns = createDropdown(app)
    app.mode = "train"
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

def submit_func(app):
    for icon in app.icons:
        print(icon)
    print(len(app.icons))

    if len(app.icons) != 1:
        app.showMessage('Make sure all components are dragged and snapped together!')
        return

    net = app.icons[0] # should be composite
    if not isinstance(net, CompositeIcon):
        app.showMessage('You cannot just have 1 icon!')
        return
    
    nets = net.icons # list
    first_net = nets[0]
    last_net = nets[-1]
    if first_net.type != 'input' or last_net.type != 'output':
        app.showMessage('First and last block must be "input" and "output" respectively!')
        return
    
    num_net = len(nets)-2
    nets = nets[1:-1]
    print(num_net, nets)

    result = {
        "mode": app.mode,
        "num_net": num_net,
        "data": {},
        "trainer": {
            "optim": {}
        }
    }

    for i, net in enumerate(nets):
        result[f"net{i+1}"] = net.parameters

    print(result)

    app.windowVisible = True
    
    app.result = result