from cmu_graphics import *

def calculateWindowBounds(app):
    window_width = int(app.width * 0.7)
    window_height = int(app.height * 0.7)
    window_x = (app.width - window_width) // 2
    window_y = (app.height - window_height) // 2
    return window_x, window_y, window_width, window_height
