from cmu_graphics import *
from components.icon import CompositeIcon

def snapToBottom(app, draggedIcon, target):
    if isinstance(target, CompositeIcon):
        bottommost = target.icons[-1]
        if distance(draggedIcon.x, draggedIcon.y, bottommost.x, bottommost.y + bottommost.height) <= app.threshold:
            return bottommost.x, bottommost.y + bottommost.height
    else:
        if distance(draggedIcon.x, draggedIcon.y, target.x, target.y + target.height) <= app.threshold:
            return target.x, target.y + target.height
    return None


def snapToTop(app, draggedIcon, target):
    if isinstance(target, CompositeIcon):
        topmost = target.icons[0]
        if distance(draggedIcon.x, draggedIcon.y + draggedIcon.height, topmost.x, topmost.y) <= app.threshold:
            return topmost.x, topmost.y - draggedIcon.height
    else:
        if distance(draggedIcon.x, draggedIcon.y + draggedIcon.height, target.x, target.y) <= app.threshold:
            return target.x, target.y - draggedIcon.height
    return None