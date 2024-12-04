from cmu_graphics import *

import tkinter as tk
from component_logic.create_logic import createBlocks, createButtons, createDropdown
from components.icon import CompositeIcon
from app.neural_network.util.parameters import convert
# from data.upload import create_ui
def get_screen_dimensions():
    root = tk.Tk()
    root.withdraw()
    return root.winfo_screenwidth(), root.winfo_screenheight()

def resetApp(app):
    screen_width, screen_height = get_screen_dimensions()
    app.width = int(screen_width*0.8)
    app.height = int(screen_height*0.8)
    # app.width, app.height = 1366, 768

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

def submit_func(app): # First submit button (not window submit button)
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
    
    if app.mode == 'train':
        num_net = len(nets)-2
        nets = nets[1:-1]
        print(num_net, nets)

        # Default selections:
        train_dict = {
            "mode": app.mode,
            "num_net": num_net,
            "data": {},
            "trainer": {
                "optim": {
                    "type": "sgd"
                },
                "num_epochs": 10,
                "loss": "cel"
            }
        }

        for i, net in enumerate(nets):
            train_dict[f"net{i+1}"] = net.parameters

        print(train_dict)

        app.trainWindowVisible = True
        
        app.train_dict = train_dict
    
    elif app.mode == 'eval':
        num_net = len(nets)-2
        nets = nets[1:-1]
        print(num_net, nets)

        eval_dict = {
            "mode": app.mode,
            "num_net": num_net,
            "data": {
                "label": [[1]]
            },
        }

        # update eval_dict with app.model!!!!
        for i, net in enumerate(nets):
            eval_dict[f"net{i+1}"] = net.parameters

        print(eval_dict)
        app.evalWindowVisible = True
        app.eval_dict = eval_dict