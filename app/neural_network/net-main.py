import torch
import torch.nn as nn
import pickle
import json

# import sys

# if len(sys.argv) < 1:
#     print("Usage: python net-main.py <json_string>")
#     sys.exit(1)

from trainer.trainer import trainer
from eval.eval import eval
from network.MLPnet import MLPNet

from util.param_parse import convert
from util.json_parse import parse_neural_dict, json_neural_dict
from util.assertions import assertions

def main(json_string):
    neural_dict = json.loads(json_string)
    mode = neural_dict['mode']
    assert mode in ['train', 'eval'], f"invalid mode: expected 'train' or 'eval, but got ({mode})"

    if mode == 'train':
        output = main_trainer(neural_dict) # return json string of ['dims', 'activations', 'loss', 'optim_dict', 'num_epochs', 'input_data', 'label', 'output', 'pickled_data']
    else:
        output = main_eval(neural_dict) # returns tensor output
    return output

def main_trainer(neural_dict):
    print('\n\n\nStarting main_trainer -----------------------------------------')
    # Parameter parse (and assertions)
    parameters = parse_neural_dict(neural_dict)
    dims = parameters['dims']
    activations = parameters['activations']
    loss = parameters['loss']
    optim_dict = parameters['optim_dict']
    num_epochs = parameters['num_epochs']
    input_data = parameters['input_data']
    label = parameters['label']

    ### Conversions (and assertions) ----------------
    # Conversions
    activations = convert.activation(activations)
    loss = convert.loss(loss)
    optim, optim_param = convert.optimizer(optim_dict)
    
    # Convert and check input and label to tensor!!!!!!!!!!!!!!!!!!
    # Temporary fix --------
    # input_data = torch.tensor(input_data, dtype=torch.float64)
    # label = torch.tensor(label, dtype=torch.float64)
    input_data = torch.randn(100,10).double()
    label = torch.randn(100,10).double()

    # Assertions
    assertions.double(input_data, label)
    assertions.dims(dims, activations) # Check dim and activation list length
    assertions.data(input_data, label, dims) # Check dimension sizes for inputs and labels

    print('dims', dims)
    print('activations', activations)
    print('loss', loss)
    print('optim', optim)
    print('num', num_epochs)

    ### Network and training initialization -------
    neural_net = MLPNet(dims, activations)
    print('network created')
    
    neural_trainer = trainer(neural_net, loss, optim, optim_param)
    print('trainer created')
    
    cache_path = neural_trainer.train(input_data, label, num_epochs=num_epochs)
    print('trained successfully')
    
    output = eval(neural_net, cache_path, input_data)

    # Save model and output into JSON string
    state_dict = neural_net.state_dict()
    pickled_data = pickle.dumps(state_dict)
    
    json_output = json_neural_dict(output, pickled_data, parameters)
    return json_output # should return json instead


def main_eval(neural_dict):
    print('\n\n\nStarting main_eval------------------------------------')
    # Parameter parse (and assertions)
    parameters = parse_neural_dict(neural_dict, mode='eval')
    dims = parameters['dims']
    activations = parameters['activations']
    input_data = parameters['input_data']
    label = parameters['label']
    state = parameters['state']

    ### Conversions (and assertions) ----------------
    # Conversions
    activations = convert.activation(activations)
    
    # Convert and check input and label to tensor
    # Temporary fix --------
    # input_data = torch.tensor(input_data, dtype=torch.float64)
    # label = torch.tensor(label, dtype=torch.float64)
    input_data = torch.randn(100,10).double()
    label = torch.randn(100,10).double()

    # Assertions
    assertions.double(input_data, label)
    assertions.dims(dims, activations) # Check dim and activation list length
    assertions.data(input_data, label, dims) # Check dimension sizes for inputs and labels

    print('dims', dims)
    print('activations', activations)

    ### Network and training initialization -------
    neural_net = MLPNet(dims, activations)
    print('network created')
    
    output = eval(neural_net, state, input_data, mode='pickle') # state is pickle file
    output = output.tolist()

    dict_return = {'output': output, 'state': state}
    json_return = json.dumps(dict_return)

    return json_return

if __name__ == "__main__":
    # train test
    neural_dict = {
                    'mode': 'train',
                    'network': {
                        'type': 'mlp',
                        'dims': [10, 256, 256, 256, 10],
                        'activations': ['relu', 'relu', 'relu', 'relu']
                    },
                    'trainer': {
                        'parameters': {
                            'loss': 'mse',
                            'optim': {
                                'type': 'adam',
                                'lr': 0.01},
                            'num_epochs': 100
                        },
                        'data': {
                            'input': [1,2,3,4,5,6,7,8,9,10],
                            'label': [2,4,6,8,10,12,14,16,18,20]
                        }
                    }
                }
    
    json_string = json.dumps(neural_dict)

    output = main(json_string)

    # eval test
    # ['dims', 'activations', 'loss', 'optim_dict', 'num_epochs', 'input_data', 'label', 'output', 'pickled_data']
    output = json.loads(output)
    state = output['pickled_data']
    neural_dict_eval = {
                'mode': 'eval',
                'network': {
                    'type': 'mlp',
                    'dims': [10, 256, 256, 256, 10],
                    'activations': ['relu', 'relu', 'relu', 'relu'],
                    'state': state
                },
                'trainer': {
                    'parameters': {
                        'loss': 'mse',
                        'optim': {
                            'type': 'adam',
                            'lr': 0.01},
                        'num_epochs': 100
                    },
                    'data': {
                        'input': [1,2,3,4,5,6,7,8,9,10],
                        'label': [2,4,6,8,10,12,14,16,18,20]
                    }
                }
            }
    json_string = json.dumps(neural_dict_eval)
    output = main(json_string)
    # in future: number of networks should be key, then network --> network1, network2 , etc.
