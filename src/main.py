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
from components.circle import Circle 
from components.figures import Counter, CNNCounter, cnnFigures, mlpFigures, updateActivations, updateLayer, updateType

from util.math_utils import inTriangle
from util.bounds_utils import calculateWindowBounds
from util.fix_utils import fixActivations

from app.neural_network.net_main import neural_main

def onAppStart(app):
    resetApp(app)
    app.previousWidth = app.width  
    app.previousHeight = app.height  
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

    # Check if mouse is over existing icon
    for icon in app.icons:
        if isinstance(icon, CompositeIcon):
            if icon.contains(mouseX, mouseY):
                # Top block dragged: drag entire composite
                app.draggedIcon = icon
                app.draggedIcon.startDrag(mouseX, mouseY)
                app.selectedIcon = icon.icons[0]
                return
            else:
                # Check if non-top block is dragged
                index = icon.otherContains(mouseX, mouseY)
                if index is not None:
                    # Detach all blocks from index and below
                    detachedIcons = icon.icons[index:]
                    remainingIcons = icon.icons[:index]

                    # Update original composite
                    icon.icons = remainingIcons
                    icon.updatePosition()

                    # New composite for detached blocks
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

    # Check if mouse over block to create new icon
    for block in app.blocks:
        if block.contains(mouseX, mouseY):
            newIcon = createIcon(block)
            app.icons.append(newIcon)
            app.draggedIcon = newIcon
            app.draggedIcon.startDrag(mouseX, mouseY)
            app.selectedIcon = newIcon
            return
        
    # Button logic
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

    # Toggle dropdowns
    for dropdown in app.netDropdowns:
        if dropdown.contains(mouseX, mouseY):
            # Close all other dropdowns first
            for other in app.netDropdowns:
                if other is not dropdown:
                    other.close()
            dropdown.toggle()
            return

    # Clicked elsewhere, close all dropdowns
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
                        # Silhouette for CompositeIcon
                        app.previewIcon = CompositeIcon(app.draggedIcon.icons.copy())
                        app.previewIcon.x, app.previewIcon.y = snapPosition
                    else:
                        # Silhouette for single Icon
                        app.previewIcon = Icon(*snapPosition, app.draggedIcon.width, app.draggedIcon.height, app.draggedIcon.text, app.draggedIcon.type)
                    return

                snapPosition = snapToBottom(app, app.draggedIcon, icon)
                if snapPosition:
                    if isinstance(app.draggedIcon, CompositeIcon):
                        # Silhouette for CompositeIcon
                        app.previewIcon = CompositeIcon(app.draggedIcon.icons.copy())
                        app.previewIcon.x, app.previewIcon.y = snapPosition
                    else:
                        # Silhouette for single Icon
                        app.previewIcon = Icon(*snapPosition, app.draggedIcon.width, app.draggedIcon.height, app.draggedIcon.text, app.draggedIcon.type)
                    return

        # Remove preview if no snap 
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
    selectedIconChanged = (app.selectedIcon != app.previousSelectedIcon)

    # If window is resized or selected icon changed
    if windowResized or selectedIconChanged:
        print("Update triggered due to resize or selected icon change.")
        
        # Update logic
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

    # Blinking cursor 
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

def main():
    runApp()

if __name__ == '__main__':
    main()