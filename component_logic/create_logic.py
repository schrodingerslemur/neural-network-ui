from cmu_graphics import *

from components.block import Block
from components.button import circleButton, dropdownButton
from components.icon import Icon


def createBlocks():
    return [ 
        Block(33,90,180,40,text='Input',type='input'),
        Block(33,150,180,40,text='Output',type='output'),
        Block(33,210,180,40,text='MLP'),
        Block(33,270,180,40,text='CNN'),
        Block(33,330,180,40,text='RNN'),
        Block(33,390,180,40,text='GNN'),
        Block(33,450,180,40,text='Transformer')
    ]

def createButtons(app, reset_func):
    return [
        circleButton(app.width-44, 30, 20, func=reset_func, param=app, text='Reset', url='static/reset.png'),
        circleButton(app.width-94, 30, 20, func=app.submit, param=app, text='Submit', url='static/submit.png')        
    ]

def createDropdown(app):
    return [
        dropdownButton(app.width-234, 30, 80, 20, options=["train", "eval"])
    ]

def createIcon(block):
    return Icon(block.x, block.y, block.width, block.height, str(block.text), block.type)