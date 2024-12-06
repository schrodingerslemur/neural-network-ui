from cmu_graphics import *
import json
import base64
import logging
import io
import tkinter as tk
from tkinter import filedialog

from component_logic.create_logic import createBlocks, createButtons, createIcon
from component_logic.draw_logic import drawPreview, drawHeader, drawBackground, drawBlocks, drawIcons, drawButtons, drawDropdown, drawSelectedIcon, drawNetFigures, drawTrainWindow, drawEvalWindow
from component_logic.snap_logic import snapToBottom, snapToTop
from component_logic.app_logic import resetApp
from component_logic.submit_logic import submitTrain, submitEval

from components.block import Block
from components.button import circleButton, dropdownButton
from components.icon import Icon, CompositeIcon
from components.circle import Circle # Figures for MLP visualization
from components.figures import Counter, mlpFigures, updateActivations, updateLayer, updateType

from util.math_utils import inTriangle
from util.bounds_utils import calculateWindowBounds
from util.fix_utils import fixActivations

from log.log import setup_logging # print out loss and activation etc. can use regex

from app.neural_network.net_main import neural_main

def onAppStart(app):
    resetApp(app)
    app.previousWidth = app.width  # Store the initial width
    app.previousHeight = app.height  # Store the initial height
    app.previousSelectedIcon = None

    app.minWidth = 900
    app.minHeight = 600
    app.maxWidth = 1300
    app.maxHeight = 800


def onMousePress(app, mouseX, mouseY):
    if app.trainWindowVisible:
        # window interactions
        if app.trainWindowCloseButton.contains(mouseX, mouseY):
            app.trainWindowCloseButton.pressed()
            return
        elif app.inputUploadButton.contains(mouseX, mouseY):
            app.inputUploadButton.pressed()
            return
        elif app.labelUploadButton.contains(mouseX, mouseY):
            app.labelUploadButton.pressed()
            return
        elif app.trainSubmitButton.contains(mouseX, mouseY):
            app.trainSubmitButton.pressed()
            return
        
        # Check if num_epochs field is clicked
        window_x, window_y, _, _ = calculateWindowBounds(app)
        num_epochs_x = window_x + 650
        num_epochs_y = window_y + 350
        if num_epochs_x <= mouseX <= num_epochs_x + 150 and num_epochs_y <= mouseY <= num_epochs_y + 30:
            app.numEpochsSelected = True  
        else:
            app.numEpochsSelected = False  

        # Handle dropdowns
        selected_optimizer = app.optimizerDropdown.optionContains(mouseX, mouseY)
        if selected_optimizer:
            app.optimizerDropdown.selectOption(selected_optimizer)
            app.train_dict["trainer"]["optim"]["type"] = selected_optimizer
            return
        elif app.optimizerDropdown.contains(mouseX, mouseY):
            app.lossFunctionDropdown.close()
            app.optimizerDropdown.toggle()
            return

        selected_loss = app.lossFunctionDropdown.optionContains(mouseX, mouseY)
        if selected_loss:
            app.lossFunctionDropdown.selectOption(selected_loss)
            app.train_dict["trainer"]["loss"] = selected_loss
            return
        elif app.lossFunctionDropdown.contains(mouseX, mouseY):
            app.optimizerDropdown.close()
            app.lossFunctionDropdown.toggle()
            return

    elif app.evalWindowVisible:
        # Eval window interactions
        if app.evalWindowCloseButton.contains(mouseX, mouseY):
            app.evalWindowCloseButton.pressed()
            return
        elif app.evalInputUploadButton.contains(mouseX, mouseY):
            app.evalInputUploadButton.pressed()
            return
        elif app.modelUploadButton.contains(mouseX, mouseY):
            app.modelUploadButton.pressed()
            return
        elif app.evalSubmitButton.contains(mouseX, mouseY):
            submitEval(app)  # Handle eval submission
            return
    
    for button in app.buttons:
        if button.contains(mouseX, mouseY):
            button.pressed()
            return

    # Check if  mouse is over existing icon
    for icon in app.icons:
        if isinstance(icon, CompositeIcon):
            if icon.contains(mouseX, mouseY):
                # Top block is being dragged, drag the entire composite
                app.draggedIcon = icon
                app.draggedIcon.startDrag(mouseX, mouseY)
                app.selectedIcon = icon.icons[0]
                return
            else:
                # check if non-top block is dragged
                index = icon.otherContains(mouseX, mouseY)
                if index is not None:
                    # Detach all blocks from this index and below
                    detachedIcons = icon.icons[index:]
                    remainingIcons = icon.icons[:index]

                    # Update original composite
                    icon.icons = remainingIcons
                    icon.updatePosition()

                    # new composite for detached blocks
                    newComposite = CompositeIcon(detachedIcons)
                    app.icons.append(newComposite)
                    app.draggedIcon = newComposite
                    app.draggedIcon.startDrag(mouseX, mouseY)

                    app.selectedIcon = newComposite.icons[0]
                    return
        elif icon.contains(mouseX, mouseY):
            # Single icon drag
            app.draggedIcon = icon
            app.draggedIcon.startDrag(mouseX, mouseY)
            app.selectedIcon = icon
            return

    # Check if mouse is over block to create new icon
    for block in app.blocks:
        if block.contains(mouseX, mouseY):
            newIcon = createIcon(block)
            app.icons.append(newIcon)
            app.draggedIcon = newIcon
            app.draggedIcon.startDrag(mouseX, mouseY)
            app.selectedIcon = newIcon
            return
        
    # button logic
    for button in app.netButtons:
        if isinstance(button, (Counter, CNNCounter)):
            # Handle Counter buttons
            if button.leftContains(mouseX, mouseY):
                button.decrease()
                return
            elif button.rightContains(mouseX, mouseY):
                button.increase()
                return
        elif isinstance(button, circleButton):
            # Handle circleButton
            if button.contains(mouseX, mouseY):
                button.pressed()
                return
            
    for dropdown in app.dropdowns:
        selected_option = dropdown.optionContains(mouseX, mouseY)
        if selected_option:
            app.mode = selected_option
            print(app.mode)
            dropdown.selectOption(selected_option)
            return  
    for dropdown in app.dropdowns:
        if dropdown.contains(mouseX, mouseY):
            dropdown.toggle()
            return

    for dropdown in app.netDropdowns:
        selected_option = dropdown.optionContains(mouseX, mouseY)
        if selected_option:
            dropdown.selectOption(selected_option)
            if app.selectedIcon.net_type == 'mlp':
                updateActivations(app)
            elif app.selectedIcon.net_type == 'cnn':
                if dropdown.options == ['conv', 'pool']:
                    updateLayer(app)
                    app.netFigures, app.netButtons, app.netDropdowns = cnnFigures(app)
                elif dropdown.options == [None]+ app.activations:
                    print('here')
                    updateActivations(app)
                else:
                    updateType(app)
            return

    # toggle dropdowns
    for dropdown in app.netDropdowns:
        if dropdown.contains(mouseX, mouseY):
            # Close all other dropdowns first
            for other in app.netDropdowns:
                if other is not dropdown:
                    other.close()
            dropdown.toggle()
            return

    # clicked elsewhere, close all dropdowns
    for dropdown in app.netDropdowns:
        dropdown.close()

def onMouseDrag(app, mouseX, mouseY):
    if app.draggedIcon:
        app.draggedIcon.drag(mouseX, mouseY)

        # Check for potential snapping position
        for icon in app.icons:
            if icon is not app.draggedIcon:
                snapPosition = snapToTop(app, app.draggedIcon, icon)
                if snapPosition:
                    if isinstance(app.draggedIcon, CompositeIcon):
                        # silhouette for CompositeIcon
                        app.previewIcon = CompositeIcon(app.draggedIcon.icons.copy())
                        app.previewIcon.x, app.previewIcon.y = snapPosition
                    else:
                        # silhouette for single Icon
                        app.previewIcon = Icon(*snapPosition, app.draggedIcon.width, app.draggedIcon.height, app.draggedIcon.text, app.draggedIcon.type)
                    return

                snapPosition = snapToBottom(app, app.draggedIcon, icon)
                if snapPosition:
                    if isinstance(app.draggedIcon, CompositeIcon):
                        # silhouette for CompositeIcon
                        app.previewIcon = CompositeIcon(app.draggedIcon.icons.copy())
                        app.previewIcon.x, app.previewIcon.y = snapPosition
                    else:
                        # silhouette for single Icon
                        app.previewIcon = Icon(*snapPosition, app.draggedIcon.width, app.draggedIcon.height, app.draggedIcon.text, app.draggedIcon.type)
                    return

        # remove preview if no snap 
        app.previewIcon = None


def onMouseMove(app, mouseX, mouseY):
    pass

def onMouseRelease(app, mouseX, mouseY):
    if app.draggedIcon:
        for icon in app.icons:
            if icon is not app.draggedIcon:
                # Check for snapping to top
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

                # Check for snapping to  bottom
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
    app.previewIcon = None  

def onKeyPress(app, key):
    if app.numEpochsSelected:
        if key.isdigit(): 
            app.numEpochsInput += key
        elif key == "backspace" and len(app.numEpochsInput) > 0:
            app.numEpochsInput = app.numEpochsInput[:-1] 
        
        # Update the train_dict
        app.train_dict["trainer"]["num_epochs"] = int(app.numEpochsInput) if app.numEpochsInput.isdigit() else 0
        print(f"Num Epochs Updated: {app.train_dict['trainer']['num_epochs']}")


def onKeyRelease(app, key):
    pass

def onKeyHold(app, key):
    pass

def onStep(app):
    app.counter += 1
    if app.counter % 100 == 0:
        if app.selectedIcon is not None:
            print(app.selectedIcon.parameters)
        if app.mode == 'train':
            print(app.train_dict)
        else:
            print(app.eval_dict)

    if app.width < app.minWidth:
        app.width = app.minWidth
    elif app.width > app.maxWidth:
        app.width = app.maxWidth

    if app.height < app.minHeight:
        app.height = app.minHeight
    elif app.height > app.maxWidth:
        app.width = app.maxWidth

    windowResized = (app.width != app.previousWidth or app.height != app.previousHeight)
    # Detect selected icon change
    selectedIconChanged = (app.selectedIcon != app.previousSelectedIcon)

    # Only update if window is resized or selected icon changes
    if windowResized or selectedIconChanged:
        print("Update triggered due to resize or selected icon change.")
        
        # Perform update logic here
        if app.selectedIcon is None:
            app.netFigures, app.netButtons, app.netDropdowns = [], [], []
        elif app.selectedIcon.net_type == 'mlp':
            app.netFigures, app.netButtons, app.netDropdowns = mlpFigures(app)
        elif app.selectedIcon.net_type == 'cnn':
            app.netFigures, app.netButtons, app.netDropdowns = cnnFigures(app)

        # Update tracking variables
        app.previousWidth = app.width
        app.previousHeight = app.height
        app.previousSelectedIcon = app.selectedIcon
        if app.selectedIcon is not None:
            app.previousParameters = app.selectedIcon.parameters.copy()


    # blinking cursor 
    if app.counter % 15 == 0:
        app.numEpochsCursorVisible = not app.numEpochsCursorVisible

def redrawAll(app):
    drawBackground(app)
    drawHeader(app)

    # Drawing-board of screen
    if app.previewIcon:
        drawPreview(app.previewIcon)
    drawBlocks(app)
    drawButtons(app)
    drawIcons(app)

    # Right-side of screen
    drawSelectedIcon(app)
    
    drawDropdown(app)
    if app.selectedIcon is not None and app.selectedIcon.net_type in ['mlp', 'cnn']:
        drawNetFigures(app)
    # Screen window (when submit is pressed)
    if app.trainWindowVisible:
        drawTrainWindow(app)
    
    if app.evalWindowVisible:
        drawEvalWindow(app)

class CNNCounter:
    def __init__(self, x, y, parameters, index, key, app):
        """
        Counter for managing specific parameters of CNN layers.
        :param x: X-coordinate of the counter
        :param y: Y-coordinate of the counter
        :param parameters: CNN layer parameters
        :param index: Index of the layer in the dims list
        :param key: The parameter key to modify (e.g., "in_channels", "kernel_size")
        :param app: The app object for context
        """
        self.x = x
        self.y = y
        self.parameters = parameters
        self.index = index
        self.key = key
        self.app = app

    def draw(self):
        current_value = self.parameters["dims"][self.index].get(self.key, 0)
        drawCircle(self.x, self.y, 15, fill='grey', border='black')
        drawLabel(str(current_value), self.x, self.y)
        drawLabel(self.key, self.x, self.y + 25, size=10)

        # Draw left and right adjustment buttons
        self.leftDims = [self.x - 40, self.y,
                         self.x - 20, self.y - 15,
                         self.x - 20, self.y + 15]
        
        self.rightDims = [self.x + 40, self.y,
                          self.x + 20, self.y - 15,
                          self.x + 20, self.y + 15]
        
        # Left clicker
        drawPolygon(
            *self.leftDims,
            fill='green'
        )

        # Right clicker
        drawPolygon(
            *self.rightDims,
            fill='green'
        )

    def leftContains(self, x, y):
        return inTriangle(x, y, *self.leftDims)
    
    def rightContains(self, x, y):
        return inTriangle(x, y, *self.rightDims)
    
    def increase(self):
        # Increase the specific parameter value
        self.parameters["dims"][self.index][self.key] += 1

    def decrease(self):
        # Decrease the specific parameter value
        if self.parameters["dims"][self.index][self.key] > 0:
            self.parameters["dims"][self.index][self.key] -= 1

def cnnFigures(app):
    """
    Create a visual representation of CNN dimensions with dropdowns and counters.
    """
    parameters = app.selectedIcon.parameters
    scale_x = app.width / 1366  # Scale factor for width
    scale_y = app.height / 768  # Scale factor for height

    center_x = app.width - 200  # Center x position
    start_y = int(150 * scale_y) + 30  # Start y position for the first layer

    figures = []
    buttons = []
    dropdowns = []

    # counter = CNNCounter(100,100,parameters, 0, "in_channels", app)
    for i, layer in enumerate(parameters["dims"]):
        x = center_x - int(50 * scale_x)  # Centered position for the layer
        layer_width = int(200 * scale_x)
        layer_height = int(50 * scale_y)

        type_dropdown = dropdownButton(
            x - int(170*scale_x),
            start_y-15,
            int(80*scale_x),
            30,
            ["conv", "pool"],
            default_option=layer["layer"]
        )
        dropdowns.append(type_dropdown)

        if layer["layer"] == "conv":
            # Conv layer counters
            in_channel_counter = CNNCounter(
                x - int(30 * scale_x), start_y, parameters, i, "in_channels", app)
            out_channel_counter = CNNCounter(
                x + int(80 * scale_x), start_y, parameters, i, "out_channels", app)
            kernel_size_counter = CNNCounter(
                x + int(190 * scale_x), start_y, parameters, i, "kernel_size", app)

            buttons.extend([in_channel_counter, out_channel_counter, kernel_size_counter])

        elif layer["layer"] == "pool":
            # Pooling layer type dropdown
            pool_type_dropdown = dropdownButton(
                x - int(80 * scale_x),
                start_y - 15,
                int(80 * scale_x),
                30,
                options=["max", "avg"],
                default_option=layer.get("type", "max")
            )
            dropdowns.append(pool_type_dropdown)

            # Pooling layer counters
            kernel_size_counter = CNNCounter(
                x + int(80 * scale_x), start_y, parameters, i, "kernel_size", app)
            stride_counter = CNNCounter(
                x + int(190 * scale_x), start_y, parameters, i, "stride", app)

            buttons.extend([kernel_size_counter, stride_counter])

        activation_dropdown = dropdownButton(
            x + int(100 * scale_x),
            start_y + int(45 * scale_y),
            int(90 * scale_x),
            20,
            options=[None] + app.activations,  # Example activations: ["ReLU", "Sigmoid", "Tanh"]
            default_option=parameters["activations"][i]  # Default activation from parameters
        )
        dropdowns.append(activation_dropdown)
        # Adjust start_y for the next layer
        start_y += int(layer_height + 45 * scale_y)

    # Add a button to append a new layer
    add_layer_button = circleButton(
        center_x + int(150 * scale_x), 
        start_y + int(40 * scale_y), 
        int(30 * scale_x), 
        text="Add Layer", 
        url='static/add.png', 
        func=addLayer, 
        param=app
    )
    buttons.append(add_layer_button)


    return figures, buttons, dropdowns

def addLayer(app):
    """
    Add a new layer to the CNN figure.
    """
    if app.selectedIcon and "dims" in app.selectedIcon.parameters:
        # Default to a convolutional layer
        app.selectedIcon.parameters["dims"].append({
            "layer": "conv",
            "in_channels": 3,
            "out_channels": 16,
            "kernel_size": 3,
            "stride": 1,
            "padding": 0
        })
        app.selectedIcon.parameters["activations"].append(None)
        # Refresh the figures
        app.netFigures, app.netButtons, app.netDropdowns = cnnFigures(app)




def main():
    runApp()

if __name__ == '__main__':
    main()