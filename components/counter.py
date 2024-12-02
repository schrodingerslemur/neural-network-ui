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
        current_count = self.parameters["dims"][self.index]  # Get count dynamically
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
        self.parameters["dims"][self.index] += 1  # Directly modify the value in parameters
        self.updateFigures()

    def decrease(self):
        if self.parameters["dims"][self.index] > 0:  # Ensure count doesn't go negative
            self.parameters["dims"][self.index] -= 1
            self.updateFigures()

    def updateFigures(self):
        self.app.netFigures, self.app.netButtons, self.app.netDropdowns = mlpFigures(self.app, self.parameters)

def mlpFigures(app, parameters):
    center_x, start_y, row_width = 1100, 150, 200  # Center x, start y, total row width
    max_circles = 20  # Maximum number of circles in a row
    r = 10  # Default radius
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

        button = Counter(center_x + row_width//2 + 100, start_y, parameters, i, app)
        buttons.append(button)

        mid_y = start_y + 2*r 
        dropdown = dropdownButton(center_x + 90 , mid_y, 70, 22, options=[None]+app.activations)
        dropdown.selected_option = parameters["activations"][i]  # Sync with existing parameter
        dropdowns.append(dropdown)

        start_y += 2 * r + 50  # Move to the next row

    add_row_button_y = start_y + 20
    add_row_button = circleButton(center_x + row_width//2 + 100, add_row_button_y, 30, text="Add layer",url='static/add.png', func=addRow, param=app)
    buttons.append(add_row_button)

    return figures, buttons, dropdowns

def addRow(app):
    """
    Add a new row to the MLP figure.
    """
    if app.selectedIcon and "dims" in app.selectedIcon.parameters:
        # Add a default value (e.g., 1) to dims and a default activation
        app.selectedIcon.parameters["dims"].append(1)
        app.selectedIcon.parameters["activations"].append(None)

        # Update the figures and controls
        app.netFigures, app.netButtons, app.netDropdowns = mlpFigures(app, app.selectedIcon.parameters)

def updateActivations(app):
    """
    Update the activations in parameters based on the dropdown selections.
    """
    if app.selectedIcon and "activations" in app.selectedIcon.parameters:
        for i, dropdown in enumerate(app.netDropdowns):
            app.selectedIcon.parameters["activations"][i] = dropdown.selected_option