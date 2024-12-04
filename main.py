from cmu_graphics import *
import json
import base64
import tkinter as tk
from tkinter import filedialog

from component_logic.create_logic import createBlocks, createButtons, createIcon
from component_logic.draw_logic import drawPreview, drawHeader, drawBackground, drawBlocks, drawIcons, drawButtons, drawDropdown, drawSelectedIcon, drawNetFigures, drawTrainWindow
from component_logic.snap_logic import snapToBottom, snapToTop
from component_logic.app_logic import resetApp

from components.block import Block
from components.button import circleButton, dropdownButton
from components.icon import Icon, CompositeIcon
from components.circle import Circle # Figures for MLP visualization
from components.counter import Counter, mlpFigures, updateActivations

from data.upload import uploadInput, uploadLabel, uploadModel, uploadEvalInput
from util.bounds_utils import calculateWindowBounds
from util.fix_utils import fixActivations

from app.neural_network.net_main import neural_main

def onAppStart(app):
    resetApp(app)

    scale_x = app.width / 1366  # Scale factor for width
    scale_y = app.height / 768  # Scale factor for height

    # Training dictionary
    app.train_dict = {"trainer": {"num_epochs": 10, "optim": {"type": None}, "loss": None}}

    # Train window close button
    app.trainWindowCloseButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(20 * scale_x), 
        text="X", func=closeTrainWindow, param=app, label=False
    )

    # Upload buttons
    app.inputUploadButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Upload input data", url='static/upload.webp', func=uploadInput, param=app, label=False
    )
    app.labelUploadButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Upload label data", url='static/upload.webp', func=uploadLabel, param=app, label=False
    )

    # Submit button
    app.trainSubmitButton = circleButton(
        int(0 * scale_x), int(0 * scale_y), int(40 * scale_x),
        text="Submit", url='static/submit.png', func=submitTrain, param=app, label=False
    )

    # Dropdowns
    app.optimizerDropdown = dropdownButton(
        int(0 * scale_x), int(0 * scale_y), int(150 * scale_x), int(30 * scale_y),
        options=app.optimizers, default_option=app.optimizers[0]
    )
    app.lossFunctionDropdown = dropdownButton(
        int(0 * scale_x), int(0 * scale_y), int(150 * scale_x), int(30 * scale_y),
        options=app.losses, default_option=app.losses[0]
    )

    # Num epochs input field
    app.numEpochsInput = "10"
    app.numEpochsSelected = False
    app.numEpochsCursorVisible = False  # To toggle the cursor

    # To check whether input/label is uploaded
    app.inputUploaded = False
    app.labelUploaded = False

    # counter for cursor blinking
    app.counter = 0

    # window visibility
    app.trainWindowVisible = False

    # Eval Window stuff:
    # Reuse inputUploadButton
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
            app.numEpochsSelected = True  # Field is selected
        else:
            app.numEpochsSelected = False  # Deselect field if clicked elsewhere

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
        print(app.icons)
        if app.mode == 'train':
            print(app.train_dict)
        else:
            print(app.eval_dict)

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
    drawNetFigures(app)
    drawDropdown(app)

    # Screen window (when submit is pressed)
    if app.trainWindowVisible:
        drawTrainWindow(app)
    
    if app.evalWindowVisible:
        drawEvalWindow(app)


def selectIcon(app, icon):
    app.selectedIcon = icon
    if app.selectedIcon.net_type == 'mlp':
        app.netFigures, app.netButtons, app.netDropdowns = mlpFigures(app, icon.parameters) # returnn figures(circles) and buttons
    else:
        app.netFigures, app.netButtons, app.netDropdowns = [], [], []

def drawEvalWindow(app):
    """Draw the evaluation window with dynamic scaling."""
    window_x, window_y, window_width, window_height = calculateWindowBounds(app)

    scale_x = app.width / 1366  # Scale factor for width
    scale_y = app.height / 768  # Scale factor for height

    # Draw window background
    drawRect(window_x, window_y, window_width, window_height, fill='lightgrey', border='black')

    # Draw window close button
    app.evalWindowCloseButton.x = window_x + window_width - int(30 * scale_x)
    app.evalWindowCloseButton.y = window_y + int(30 * scale_y)
    app.evalWindowCloseButton.draw()

    # Input upload button
    app.evalInputUploadButton.x = window_x + int(200 * scale_x)
    app.evalInputUploadButton.y = window_y + int(150 * scale_y)
    app.evalInputUploadButton.draw()
    drawLabel("Upload input data",
              app.evalInputUploadButton.x + int(90 * scale_x),
              app.evalInputUploadButton.y,
              align='left', size=int(30 * scale_y), bold=True)

    if app.evalInputUploaded:
        drawImage('static/submit.png',
                  app.evalInputUploadButton.x - int(100 * scale_x),
                  app.evalInputUploadButton.y,
                  width=int(30 * scale_x * 2) - 5,
                  height=int(30 * scale_y * 2) - 5,
                  align='center')

    # Model upload button
    app.modelUploadButton.x = window_x + int(200 * scale_x)
    app.modelUploadButton.y = window_y + int(250 * scale_y)
    app.modelUploadButton.draw()
    drawLabel("Upload model",
              app.modelUploadButton.x + int(90 * scale_x),
              app.modelUploadButton.y,
              align='left', size=int(30 * scale_y), bold=True)

    if app.modelUploaded:
        drawImage('static/submit.png',
                  app.modelUploadButton.x - int(100 * scale_x),
                  app.modelUploadButton.y,
                  width=int(30 * scale_x * 2) - 5,
                  height=int(30 * scale_y * 2) - 5,
                  align='center')

    # Eval submit button
    app.evalSubmitButton.x = window_x + int(200 * scale_x)
    app.evalSubmitButton.y = window_y + int(350 * scale_y)
    app.evalSubmitButton.draw()
    drawLabel("Submit",
              app.evalSubmitButton.x + int(90 * scale_x),
              app.evalSubmitButton.y,
              align='left', size=int(30 * scale_y), bold=True)


def submitTrain(app):
    print("Submit train button pressed.")

    # Train model
    try:
        fixActivations(app)
        json_string = json.dumps(app.train_dict)
        train_output = neural_main(json_string)
        train_output = json.loads(train_output)
        encoded_pickle_data = train_output['pickled_data']
        pickle_data = base64.b64decode(encoded_pickle_data)

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
            app.showMessage(f"Pickle file saved to {save_path}")
        else:
            print("Save operation canceled.")
            app.showMessage("Save operation canceled.")

    except Exception as e:
        app.showMessage(f"An error occured: ({e})")
        print(e)

def submitEval(app):
    print("Submit eval button pressed")


    fixActivations(app)
    print('eval_dict', app.eval_dict)
    json_string = json.dumps(app.eval_dict)
    eval_output = neural_main(json_string)
    print(eval_output)
    app.showMessage('evaluation success BORATTTTTTTTTTTTT')
    # except Exception as e:
    #     app.showMessage(f"An error occured: ({e})")
    #     print(e)
    
    
def closeTrainWindow(app):
    app.trainWindowVisible = False

def closeEvalWindow(app):
    app.evalWindowVisible = False

def main():
    runApp()

if __name__ == '__main__':
    main()