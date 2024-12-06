from cmu_graphics import *

from components.circle import Circle
from components.button import dropdownButton, circleButton

from util.math_utils import inTriangle

class Counter:
    def __init__(self, x, y, parameters, index, app):
        self.x = x
        self.y = y
        self.parameters = parameters
        self.index = index
        self.app = app


    def draw(self):
        current_count = self.parameters["dims"][self.index]
        drawCircle(self.x, self.y, 15, fill='grey', border='black')
        drawLabel(str(current_count), self.x, self.y)
        
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
        self.parameters["dims"][self.index] += 1

    def decrease(self):
        if self.parameters["dims"][self.index] > 0:
            self.parameters["dims"][self.index] -= 1
        if self.parameters["dims"][self.index] == 0:
            del self.parameters["dims"][self.index]
            del self.parameters["activations"][self.index]

def mlpFigures(app):
    parameters = app.selectedIcon.parameters
    # Dynamically scale values based on app dimensions
    scale_x = app.width / 1366  # Scale factor for width
    scale_y = app.height / 768  # Scale factor for height

    center_x = app.width-200 - scale_x*60  # Center x
    start_y = int(150 * scale_y) + 30  # Start y
    row_width = int(200 * scale_x)  # Total row width
    max_circles = 20  # Maximum number of circles in a row
    r = int(10 * scale_y)  # Scaled radius
    figures = []  # List to store circles
    buttons = []
    dropdowns = []

    for i in range(len(parameters["dims"])):  # Iterate over the rows defined by dims
        dim = parameters["dims"][i]
        # Cap the number of circles
        effective_dim = min(dim, max_circles)

        if effective_dim > 0:  # Avoid division by zero
            space = row_width // (effective_dim + 1)  # Dynamic spacing for circles
        else:
            # For dim = 0, no circles
            continue

        x = center_x - row_width // 2 + space  # Start drawing from the left of the center row
        for _ in range(effective_dim):  # Create the number of circles in the row
            figure = Circle(x, start_y, r)  # Create a circle with the fixed radius
            figures.append(figure)  # Add circle to the list
            x += space  # Move x for the next circle

        button_x = center_x + row_width // 2 + int(100 * scale_x)
        button = Counter(button_x, start_y, parameters, i, app)
        buttons.append(button)

        dropdown_x = center_x + int(90 * scale_x)
        dropdown_y = start_y + int(2 * r)
        dropdown = dropdownButton(dropdown_x, dropdown_y, int(70 * scale_x), int(22 * scale_y), options=[None] + app.activations)
        dropdown.selected_option = parameters["activations"][i]  # Sync with existing parameter
        dropdowns.append(dropdown)

        start_y += int(2 * r + 50 * scale_y)  # Move to the next row

    add_row_button_x = center_x + row_width // 2 + int(100 * scale_x)
    add_row_button_y = start_y + int(20 * scale_y)
    add_row_button = circleButton(add_row_button_x, add_row_button_y, int(30 * scale_x), text="Add layer", url='static/add.png', func=addRow, param=app)
    buttons.append(add_row_button)

    return figures, buttons, dropdowns


def addRow(app):
    if app.selectedIcon and "dims" in app.selectedIcon.parameters:
        # Add a default value (e.g., 1) to dims and a default activation
        app.selectedIcon.parameters["dims"].append(1)
        app.selectedIcon.parameters["activations"].append(None)
        app.netFigures, app.netButtons, app.netDropdowns = mlpFigures(app)

def updateActivations(app):
    if app.selectedIcon.net_type == 'mlp':
        for i, dropdown in enumerate(app.netDropdowns):
            if app.selectedIcon and "activations" in app.selectedIcon.parameters:
                app.selectedIcon.parameters["activations"][i] = dropdown.selected_option
    else:
        for i, dropdown in enumerate(app.netDropdowns):
            if dropdown.selected_option in [None] + app.activations:
                print('yes')
                print('pre', i)
                i = fixActivationIndex(app, i)
                print('post', i)
                app.selectedIcon.parameters["activations"][i] = dropdown.selected_option
                print(app.selectedIcon.parameters)

def updateType(app):
    for i, dropdown in enumerate(app.netDropdowns):
        if dropdown.selected_option in ["max", "avg"]:
            i = fixTypeIndex(app, i)
            app.selectedIcon.parameters["dims"][i]["type"] = dropdown.selected_option

def updateLayer(app):
    """
    Updates the layer type and resets parameters, then refreshes the UI.
    """
    for i, dropdown in enumerate(app.netDropdowns):
        if dropdown.selected_option in ["conv", "pool"]:
            print(app.selectedIcon.parameters["dims"])
            print('og', i)
            i = fixLayerIndex(app, i)  # Adjust index to handle layer type dropdowns
            print('fixed', i)
            
            # Update the layer type in parameters
            app.selectedIcon.parameters["dims"][i]["layer"] = dropdown.selected_option
            
            # Reset parameters based on the selected layer type
            if dropdown.selected_option == 'conv':
                app.selectedIcon.parameters["dims"][i] = {
                    "layer": "conv",
                    "in_channels": 3,
                    "out_channels": 16,
                    "kernel_size": 3,
                    "stride": 1,
                    "padding": 0
                }
            elif dropdown.selected_option == 'pool':
                app.selectedIcon.parameters["dims"][i] = {
                    "layer": "pool",
                    "type": "max",
                    "kernel_size": 2,
                    "stride": 2
                }
            
            # Refresh UI elements to reflect the updated parameters


def fixLayerIndex(app,i):
    count = 0
    for index, dropdown in enumerate(app.netDropdowns):
        if index == i:
            break
        else:
            if dropdown.options != ["conv", "pool"]:
                count += 1
    return i - count

def fixTypeIndex(app, i): # for "max", "avg"
    count = 0
    for index, dropdown in enumerate(app.netDropdowns):
        if index == i:
            break
        else:
            if dropdown.options != ["max", "avg"]:
                count += 1
    return i - count

def fixActivationIndex(app, i):
    count = 0
    for index, dropdown in enumerate(app.netDropdowns):
        if index == i:
            break
        else:
            if dropdown.options != [None] + app.activations:
                count += 1
    return i - count