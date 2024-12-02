import math

def distance(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def inTriangle(mouseX, mouseY, x1, y1, x2, y2, x3, y3):
    area_full = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))

    area1 = abs((x1 - mouseX) * (y2 - mouseY) - (x2 - mouseX) * (y1 - mouseY))
    area2 = abs((x2 - mouseX) * (y3 - mouseY) - (x3 - mouseX) * (y2 - mouseY))
    area3 = abs((x3 - mouseX) * (y1 - mouseY) - (x1 - mouseX) * (y3 - mouseY))

    return almostEqual(area1 + area2 + area3, area_full)

def almostEqual(x, y):
    return abs(x-y) <= 0.001