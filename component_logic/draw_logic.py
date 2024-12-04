from cmu_graphics import *

from components.icon import CompositeIcon
from util.bounds_utils import calculateWindowBounds

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

def drawDropdown(app):
    for dropdown in app.dropdowns:
        dropdown.draw()

def drawSelectedIcon(app):
    drawRect(app.width-200, 100, 90, 40, align='center', fill=rgb(72,132,212), border='black')
    drawLabel(app.selectedIcon, app.width - 200, 100, align='center', bold=True, size=25)
    
def drawTrainWindow(app):
    window_x, window_y, window_width, window_height = calculateWindowBounds(app)

    scale_x = app.width / 1366  # Scale factor for width
    scale_y = app.height / 768  # Scale factor for height

    # Draw window background
    drawRect(window_x, window_y, window_width, window_height, fill='lightgrey', border='black')

    # Draw window close button
    app.trainWindowCloseButton.x = window_x + window_width - int(30 * scale_x)
    app.trainWindowCloseButton.y = window_y + int(30 * scale_y)
    app.trainWindowCloseButton.draw()

    # Upload buttons
    app.inputUploadButton.x = window_x + int(200 * scale_x)
    app.inputUploadButton.y = window_y + int(150 * scale_y)
    app.inputUploadButton.draw()

    drawLabel(
        "Upload input data",
        app.inputUploadButton.x + int(90 * scale_x),
        app.inputUploadButton.y,
        align='left',
        size=int(30 * scale_y),
        bold=True
    )

    if app.inputUploaded:
        drawImage(
            'static/submit.png',
            app.inputUploadButton.x - int(100 * scale_x),
            app.inputUploadButton.y,
            width=int(60 * scale_x),
            height=int(60 * scale_y),
            align='center'
        )

    app.labelUploadButton.x = window_x + int(200 * scale_x)
    app.labelUploadButton.y = window_y + int(250 * scale_y)
    app.labelUploadButton.draw()

    drawLabel(
        "Upload label data",
        app.labelUploadButton.x + int(90 * scale_x),
        app.labelUploadButton.y,
        align='left',
        size=int(30 * scale_y),
        bold=True
    )

    if app.labelUploaded:
        drawImage(
            'static/submit.png',
            app.labelUploadButton.x - int(100 * scale_x),
            app.labelUploadButton.y,
            width=int(60 * scale_x),
            height=int(60 * scale_y),
            align='center'
        )

    # Submit button
    app.trainSubmitButton.x = window_x + int(200 * scale_x)
    app.trainSubmitButton.y = window_y + int(350 * scale_y)
    app.trainSubmitButton.draw()

    drawLabel(
        "Submit",
        app.trainSubmitButton.x + int(90 * scale_x),
        app.trainSubmitButton.y,
        align='left',
        size=int(30 * scale_y),
        bold=True
    )

    # Draw dropdowns
    app.optimizerDropdown.x = app.inputUploadButton.x + int(450 * scale_x)
    app.optimizerDropdown.y = app.inputUploadButton.y + int(10 * scale_y)
    app.lossFunctionDropdown.x = app.labelUploadButton.x + int(450 * scale_x)
    app.lossFunctionDropdown.y = app.labelUploadButton.y + int(10 * scale_y)

    # Num epochs input field
    num_epochs_x = window_x + int(650 * scale_x)
    num_epochs_y = window_y + int(350 * scale_y)
    drawRect(num_epochs_x, num_epochs_y, int(150 * scale_x), int(30 * scale_y), fill="white", border="black")
    drawLabel(
        app.numEpochsInput,
        num_epochs_x + int(10 * scale_x),
        num_epochs_y + int(15 * scale_y),
        align="left",
        size=int(20 * scale_y)
    )

    # Blinking cursor
    if app.numEpochsSelected and app.numEpochsCursorVisible:
        cursor_x = num_epochs_x + int(10 * scale_x) + len(app.numEpochsInput) * int(10 * scale_x)
        drawLine(
            cursor_x, 
            num_epochs_y + int(5 * scale_y), 
            cursor_x, 
            num_epochs_y + int(25 * scale_y), 
            fill="black"
        )
    drawLabel(
        "Num Epochs", 
        num_epochs_x, 
        num_epochs_y - int(30 * scale_y), 
        align="left", 
        size=int(30 * scale_y), 
        bold=True
    )

    if app.optimizerDropdown.is_open:
        app.lossFunctionDropdown.draw()
        drawLabel(
            "Loss Function",
            app.lossFunctionDropdown.x,
            app.lossFunctionDropdown.y - int(30 * scale_y),
            align='left',
            size=int(30 * scale_y),
            bold=True
        )
        drawLabel(
            "Optimizer",
            app.optimizerDropdown.x,
            app.optimizerDropdown.y - int(30 * scale_y),
            align='left',
            size=int(30 * scale_y),
            bold=True
        )
        app.optimizerDropdown.draw()
    elif app.lossFunctionDropdown.is_open:
        app.optimizerDropdown.draw()
        drawLabel(
            "Optimizer",
            app.optimizerDropdown.x,
            app.optimizerDropdown.y - int(30 * scale_y),
            align='left',
            size=int(30 * scale_y),
            bold=True
        )
        drawLabel(
            "Loss Function",
            app.lossFunctionDropdown.x,
            app.lossFunctionDropdown.y - int(30 * scale_y),
            align='left',
            size=int(30 * scale_y),
            bold=True
        )
        app.lossFunctionDropdown.draw()
    else:
        app.optimizerDropdown.draw()
        app.lossFunctionDropdown.draw()
        drawLabel(
            "Optimizer",
            app.optimizerDropdown.x,
            app.optimizerDropdown.y - int(30 * scale_y),
            align='left',
            size=int(30 * scale_y),
            bold=True
        )
        drawLabel(
            "Loss Function",
            app.lossFunctionDropdown.x,
            app.lossFunctionDropdown.y - int(30 * scale_y),
            align='left',
            size=int(30 * scale_y),
            bold=True
        )

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