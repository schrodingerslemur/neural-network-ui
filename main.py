from cmu_graphics import *
import json
import tkinter as tk
from tkinter import filedialog

from component_logic.create_logic import createBlocks, createButtons, createIcon
from component_logic.draw_logic import drawPreview, drawHeader, drawBackground, drawBlocks, drawIcons, drawButtons, drawParameter, drawDropdown
from component_logic.snap_logic import snapToBottom, snapToTop
from component_logic.app_logic import resetApp

from components.block import Block
from components.button import circleButton, dropdownButton
from components.icon import Icon, CompositeIcon
from components.circle import Circle # Figures for MLP visualization
from components.counter import Counter, mlpFigures, updateActivations

from data.upload import uploadInput, uploadLabel
from util.math_utils import distance, inTriangle

from app.neural_network.util.parameters import convert
from app.neural_network.net_main import neural_main

def onAppStart(app):
    resetApp(app)
    app.inputDF = None
    app.labelDF = None
    app.result = {"trainer": {"num_epochs": 10, "optim": {"type": None}, "loss": None}}
    app.windowCloseButton = circleButton(0, 0, 20, text="X", func=closeWindow, param=app, label=False)

    # upload buttons
    app.inputUploadButton = circleButton(0, 0, 40, text="Upload input data", url='static/upload.webp', func=uploadInput, param=app, label=False)
    app.labelUploadButton = circleButton(0, 0, 40, text="Upload label data", url='static/upload.webp', func=uploadLabel, param=app, label=False)

    # submit button
    app.submitButton = circleButton(0, 0, 40, text="Submit", url='static/submit.png', func=submitTrain, param=app, label=False)
    app.optimizerDropdown = dropdownButton(0, 0, 150, 30, options=app.optimizers, default_option=app.optimizers[0])
    app.lossFunctionDropdown = dropdownButton(0, 0, 150, 30, options=app.losses, default_option=app.losses[0])

    # Num epochs input field
    app.numEpochsInput = "10"
    app.numEpochsSelected = False
    app.numEpochsCursorVisible = False  # To toggle the cursor

    # counter for cursor blinking
    app.counter = 0

    # window visibility
    app.windowVisible = False




def onMousePress(app, mouseX, mouseY):
    if app.windowVisible:
        # window interactions
        if app.windowCloseButton.contains(mouseX, mouseY):
            app.windowCloseButton.pressed()
            return
        elif app.inputUploadButton.contains(mouseX, mouseY):
            app.inputUploadButton.pressed()
            return
        elif app.labelUploadButton.contains(mouseX, mouseY):
            app.labelUploadButton.pressed()
            return
        elif app.submitButton.contains(mouseX, mouseY):
            app.submitButton.pressed()
            return

        # Check if num_epochs field is clicked
        window_x, window_y, _, _ = calculateWindowBounds(app)
        num_epochs_x = window_x + 650
        num_epochs_y = window_y + 350
        if num_epochs_x <= mouseX <= num_epochs_x + 150 and num_epochs_y <= mouseY <= num_epochs_y + 30:
            app.numEpochsSelected = True  # Field is selected
        else:
            app.numEpochsSelected = False  # Deselect field if clicked elsewhere

        # Handle dropdowns
        selected_optimizer = app.optimizerDropdown.optionContains(mouseX, mouseY)
        if selected_optimizer:
            app.optimizerDropdown.selectOption(selected_optimizer)
            app.result["trainer"]["optim"]["type"] = selected_optimizer
            return
        elif app.optimizerDropdown.contains(mouseX, mouseY):
            app.lossFunctionDropdown.close()
            app.optimizerDropdown.toggle()
            return

        selected_loss = app.lossFunctionDropdown.optionContains(mouseX, mouseY)
        if selected_loss:
            app.lossFunctionDropdown.selectOption(selected_loss)
            app.result["trainer"]["loss"] = selected_loss
            return
        elif app.lossFunctionDropdown.contains(mouseX, mouseY):
            app.optimizerDropdown.close()
            app.lossFunctionDropdown.toggle()
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
                selectIcon(app,icon.icons[0])
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

                    selectIcon(app,newComposite.icons[0])
                    return
        elif icon.contains(mouseX, mouseY):
            # Single icon drag
            app.draggedIcon = icon
            app.draggedIcon.startDrag(mouseX, mouseY)
            selectIcon(app,icon)
            return

    # Check if mouse is over block to create new icon
    for block in app.blocks:
        if block.contains(mouseX, mouseY):
            newIcon = createIcon(block)
            app.icons.append(newIcon)
            app.draggedIcon = newIcon
            app.draggedIcon.startDrag(mouseX, mouseY)
            selectIcon(app,newIcon)
            return
        
    # button logic
    for button in app.netButtons:
        if isinstance(button, Counter):
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
            
    # header dropdown
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
            updateActivations(app)
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
        
        # Update the result
        app.result["trainer"]["num_epochs"] = int(app.numEpochsInput) if app.numEpochsInput.isdigit() else 0
        print(f"Num Epochs Updated: {app.result['trainer']['num_epochs']}")


def onKeyRelease(app, key):
    pass

def onKeyHold(app, key):
    pass

def onStep(app):
    app.counter += 1

    if app.counter % 100 == 0:
        print(app.icons)
        print(app.result)

    # Tcursor 
    if app.counter % 15 == 0:
        app.numEpochsCursorVisible = not app.numEpochsCursorVisible

def redrawAll(app):
    drawBackground(app)
    drawHeader(app)
    if app.previewIcon:
        drawPreview(app.previewIcon)
    drawBlocks(app)
    drawButtons(app)
    drawIcons(app)
   

    drawRect(app.width-200, 100, 180, 40, align='center', fill=rgb(72,132,212), border='black')
    drawLabel(app.selectedIcon, app.width - 200, 100, align='center', bold=True, size=25)
    
    drawNetFigures(app)
    drawDropdown(app)

    if app.windowVisible:
        drawWindow(app)


def drawNetFigures(app):
    if app.selectedIcon:
        parameters = app.selectedIcon.parameters
        drawLabel(parameters, app.width-200, app.height-50, align='center')

        for figure in app.netFigures:
            figure.draw()
        for button in app.netButtons:
            button.draw()
        for dropdown in app.netDropdowns:
            if not dropdown.is_open:  # draw only closed dropdowns
                dropdown.draw()

        for dropdown in app.netDropdowns: # draw last
            if dropdown.is_open:  # draw open dropdowns on top of everything else
                dropdown.draw()

def selectIcon(app, icon):
    app.selectedIcon = icon
    if app.selectedIcon.net_type == 'mlp':
        app.netFigures, app.netButtons, app.netDropdowns = mlpFigures(app, icon.parameters) # returnn figures(circles) and buttons
    else:
        app.netFigures, app.netButtons, app.netDropdowns = [], [], []


def submitTrain(app):
    print("Submit button pressed.")
    print(app.result)
    # sPAGGEHEti code:
    app.result["net1"]["activations"].pop()
    json_string = json.dumps(app.result)
    pickle_data = neural_main(json_string)
    # tkinter root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide root window

    # save location in file
    save_path = filedialog.asksaveasfilename(
        title="Save Pickle File",
        defaultextension=".pkl",
        filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
    )

    if save_path:
        # save pickl to chosen file
        with open(save_path, "wb") as f:
            f.write(pickle_data)
        print(f"Pickle file saved to {save_path}")
    else:
        print("Save operation canceled.")

def closeWindow(app):
    app.windowVisible = False

def drawWindow(app):
    window_x, window_y, window_width, window_height = calculateWindowBounds(app)

    # Draw window background
    drawRect(window_x, window_y, window_width, window_height, fill='lightgrey', border='black')

    # Draw window close button
    app.windowCloseButton.x = window_x + window_width - 30
    app.windowCloseButton.y = window_y + 30
    app.windowCloseButton.draw()

    # Upload buttons
    app.inputUploadButton.x = window_x + 200
    app.inputUploadButton.y = window_y + 150
    app.inputUploadButton.draw()

    drawLabel("Upload input data", app.inputUploadButton.x + 90, app.inputUploadButton.y, align='left', size=30, bold=True)

    app.labelUploadButton.x = window_x + 200
    app.labelUploadButton.y = window_y + 250
    app.labelUploadButton.draw()

    drawLabel("Upload label data", app.labelUploadButton.x + 90, app.labelUploadButton.y, align='left', size=30, bold=True)

    # Submit button
    app.submitButton.x = window_x + 200
    app.submitButton.y = window_y + 350
    app.submitButton.draw()

    drawLabel("Submit", app.submitButton.x + 90, app.submitButton.y, align='left', size=30, bold=True)

    # Draw dropdowns (non-open dropdown first)
    app.optimizerDropdown.x = app.inputUploadButton.x + 450
    app.optimizerDropdown.y = app.inputUploadButton.y + 10
    app.lossFunctionDropdown.x = app.labelUploadButton.x + 450
    app.lossFunctionDropdown.y = app.labelUploadButton.y + 10

    # Num epochs input field
    num_epochs_x = window_x + 650
    num_epochs_y = window_y + 350
    drawRect(num_epochs_x, num_epochs_y, 150, 30, fill="white", border="black")
    drawLabel(app.numEpochsInput, num_epochs_x + 10, num_epochs_y + 15, align="left", size=20)

    # Blinking cursor
    if app.numEpochsSelected and app.numEpochsCursorVisible:
        cursor_x = num_epochs_x + 10 + len(app.numEpochsInput) * 10
        drawLine(cursor_x, num_epochs_y + 5, cursor_x, num_epochs_y + 25, fill="black")
    drawLabel("Num Epochs", num_epochs_x, num_epochs_y - 30, align="left", size=30, bold=True)

    if app.optimizerDropdown.is_open:
        app.lossFunctionDropdown.draw()
        drawLabel("Loss Function", app.lossFunctionDropdown.x, app.lossFunctionDropdown.y - 30, align='left', size=30, bold=True)
        drawLabel("Optimizer", app.optimizerDropdown.x, app.optimizerDropdown.y - 30, align='left', size=30, bold=True)
        app.optimizerDropdown.draw()
    elif app.lossFunctionDropdown.is_open:
        app.optimizerDropdown.draw()
        drawLabel("Optimizer", app.optimizerDropdown.x, app.optimizerDropdown.y - 30, align='left', size=30, bold=True)
        drawLabel("Loss Function", app.lossFunctionDropdown.x, app.lossFunctionDropdown.y - 30, align='left', size=30, bold=True)
        app.lossFunctionDropdown.draw()
    else:
        app.optimizerDropdown.draw()
        app.lossFunctionDropdown.draw()
        drawLabel("Optimizer", app.optimizerDropdown.x, app.optimizerDropdown.y - 30, align='left', size=30, bold=True)
        drawLabel("Loss Function", app.lossFunctionDropdown.x, app.lossFunctionDropdown.y - 30, align='left', size=30, bold=True)



def calculateWindowBounds(app):
    window_width = int(app.width * 0.7)
    window_height = int(app.height * 0.7)
    window_x = (app.width - window_width) // 2
    window_y = (app.height - window_height) // 2
    return window_x, window_y, window_width, window_height

    
def main():
    runApp()

if __name__ == '__main__':
    main()