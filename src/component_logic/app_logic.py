from cmu_graphics import *

import tkinter as tk

from components.icon import CompositeIcon
from components.button import circleButton, dropdownButton
from component_logic.create_logic import createBlocks, createButtons, createDropdown
from component_logic.close_logic import closeEvalWindow, closeTrainWindow
from component_logic.submit_logic import submitEval, submitTrain

from data.upload import uploadInput, uploadLabel, uploadModel, uploadEvalInput
from app.neural_network.util.parameters import convert


def get_screen_dimensions():
    root = tk.Tk()
    root.withdraw()
    return root.winfo_screenwidth(), root.winfo_screenheight()

def resetApp(app):
    screen_width, screen_height = get_screen_dimensions()
    app.width = int(screen_width*0.8)
    app.height = int(screen_height*0.8)

    app.blocks = createBlocks() 
    app.submit = submit_func
    app.buttons = createButtons(app, resetApp)
    app.dropdowns = createDropdown(app)
    app.mode = "train"
    app.icons = [] 

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

    scale_x = app.width / 1366  
    scale_y = app.height / 768  

    # Training dictionary
    app.train_dict = {"trainer": {"num_epochs": 10, "optim": {"type": None}, "loss": None}}

    # Train window close button
    app.trainWindowCloseButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(20 * scale_x), 
        text="X", func=closeTrainWindow, param=app, label=False
    )

    app.inputUploadButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Upload input data", url='static/upload.webp', func=uploadInput, param=app, label=False
    )
    app.labelUploadButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Upload label data", url='static/upload.webp', func=uploadLabel, param=app, label=False
    )

    app.trainSubmitButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Submit", url='static/submit.png', func=submitTrain, param=app, label=False
    )

    app.optimizerDropdown = dropdownButton(
        int(0 * scale_x), int(0 * scale_y), int(150 * scale_x), int(30 * scale_y),
        options=app.optimizers, default_option=app.optimizers[0]
    )
    app.lossFunctionDropdown = dropdownButton(
        int(0 * scale_x), int(0 * scale_y), int(150 * scale_x), int(30 * scale_y),
        options=app.losses, default_option=app.losses[0]
    )

    app.numEpochsInput = "10"
    app.numEpochsSelected = False
    app.numEpochsCursorVisible = False  # To toggle the cursor

    app.inputUploaded = False
    app.labelUploaded = False

    app.counter = 0
    app.trainWindowVisible = False

    app.model = None
    app.eval_dict = {}
    app.modelUploadButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Upload model", url='static/upload.webp', func=uploadModel, param=app, label=False
    )

    app.evalInputUploadButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Upload input data", url='static/upload.webp', func=uploadEvalInput, param=app, label=False
    )

    app.evalWindowCloseButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(20 * scale_x),
        text="X", func=closeEvalWindow, param=app, label=False
    )

    app.evalSubmitButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Evaluate", url='static/submit.png', func=submitEval, param=app, label=False
    )
    app.evalWindowVisible = False
    app.evalInputUploaded = False
    app.modelUploaded = False
    

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
            
        app.evalWindowVisible = True
        app.eval_dict = eval_dict