from cmu_graphics import *

from component_logic.create_logic import createBlocks, createButtons, createIcon
from component_logic.draw_logic import drawPreview, drawHeader, drawBackground, drawBlocks, drawIcons, drawButtons, drawParameter
from component_logic.snap_logic import snapToBottom, snapToTop
from component_logic.app_logic import resetApp

from components.block import Block
from components.button import circleButton, dropdownButton
from components.icon import Icon, CompositeIcon
from components.circle import Circle # Figures for MLP visualization
from components.counter import Counter, mlpFigures, updateActivations

from util.math_utils import distance, inTriangle

from app.neural_network.util.parameters import convert

def onAppStart(app):
    resetApp(app)

def onMousePress(app, mouseX, mouseY):
    for button in app.buttons:
        if button.contains(mouseX, mouseY):
            button.pressed()
            return

    # Check if the mouse is over an existing icon
    for icon in app.icons:
        if isinstance(icon, CompositeIcon):
            if icon.contains(mouseX, mouseY):
                # Top block is being dragged, drag the entire composite
                app.draggedIcon = icon
                app.draggedIcon.startDrag(mouseX, mouseY)
                selectIcon(app,icon.icons[0])
                return
            else:
                # Check if a non-top block is being dragged
                index = icon.otherContains(mouseX, mouseY)
                if index is not None:
                    # Detach all blocks from this index and below
                    detachedIcons = icon.icons[index:]
                    remainingIcons = icon.icons[:index]

                    # Update the original composite
                    icon.icons = remainingIcons
                    icon.updatePosition()

                    # Create a new composite for the detached blocks
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

    # Check if the mouse is over a block to create a new icon
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
            
    for dropdown in app.netDropdowns:
        selected_option = dropdown.optionContains(mouseX, mouseY)
        if selected_option:
            dropdown.selectOption(selected_option)
            updateActivations(app)
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

    # If clicked elsewhere, close all dropdowns
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
                        # Show silhouette for CompositeIcon
                        app.previewIcon = CompositeIcon(app.draggedIcon.icons.copy())
                        app.previewIcon.x, app.previewIcon.y = snapPosition
                    else:
                        # Show silhouette for single Icon
                        app.previewIcon = Icon(*snapPosition, app.draggedIcon.width, app.draggedIcon.height, app.draggedIcon.text, app.draggedIcon.type)
                    return

                snapPosition = snapToBottom(app, app.draggedIcon, icon)
                if snapPosition:
                    if isinstance(app.draggedIcon, CompositeIcon):
                        # Show silhouette for CompositeIcon
                        app.previewIcon = CompositeIcon(app.draggedIcon.icons.copy())
                        app.previewIcon.x, app.previewIcon.y = snapPosition
                    else:
                        # Show silhouette for single Icon
                        app.previewIcon = Icon(*snapPosition, app.draggedIcon.width, app.draggedIcon.height, app.draggedIcon.text, app.draggedIcon.type)
                    return

        # If no snap position, remove the preview
        app.previewIcon = None


def onMouseMove(app, mouseX, mouseY):
    pass

def onMouseRelease(app, mouseX, mouseY):
    if app.draggedIcon:
        for icon in app.icons:
            if icon is not app.draggedIcon:
                # Check for snapping to the top
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

                # Check for snapping to the bottom
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
    app.previewIcon = None  # Clear the silhouette

def onKeyPress(app, key):
    pass

def onKeyRelease(app, key):
    pass

def onKeyHold(app, key):
    pass

def onStep(app):
    app.counter += 1

    if app.counter % 100 == 0:
        print(app.icons)

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
    
    # Selected icon figures
    drawNetFigures(app)
    

def drawNetFigures(app):
    if app.selectedIcon:
        parameters = app.selectedIcon.parameters
        drawLabel(parameters, app.width-200, app.height-50, align='center')

        for figure in app.netFigures:
            figure.draw()
        for button in app.netButtons:
            button.draw()
        for dropdown in app.netDropdowns:
            if not dropdown.is_open:  # Draw only closed dropdowns here
                dropdown.draw()

        # Draw opened dropdowns last to ensure they appear on top
        for dropdown in app.netDropdowns:
            if dropdown.is_open:  # Draw open dropdowns on top of everything else
                dropdown.draw()

def selectIcon(app, icon):
    app.selectedIcon = icon
    if app.selectedIcon.net_type == 'mlp':
        app.netFigures, app.netButtons, app.netDropdowns = mlpFigures(app, icon.parameters) # returnn figures(circles) and buttons
    else:
        app.netFigures, app.netButtons, app.netDropdowns = [], [], []






def main():
    runApp()

if __name__ == '__main__':
    main()