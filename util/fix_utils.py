from cmu_graphics import *

def fixActivations(app):
    if app.mode == 'train':
        num_net = app.train_dict["num_net"]
        for i in range(num_net):
            if app.train_dict[f"net{i+1}"]["type"] == 'mlp':
                app.train_dict[f"net{i+1}"]["activations"].pop()
    else:
        num_net = app.eval_dict["num_net"]
        for i in range(num_net):
            if app.eval_dict[f"net{i+1}"]["type"] == 'mlp':
                app.eval_dict[f"net{i+1}"]["activations"].pop()
