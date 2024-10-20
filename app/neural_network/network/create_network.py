import torch.nn as nn
import copy

from network.MLPnet import MLPNet
# import created submodules
from util.parameters import convert, parse, assertions

def create_network_list(neural_dict): # Return list of networks, repeated net_num number of times
    num_net = neural_dict.get('num_net')
    assert isinstance(num_net, int), f"expected num_net to be int, but got ({num_net})"

    network_list = []

    for i in range(num_net):
        # assert num_net matches number of networks given (try/except)
        net_name = f"net{i+1}"
        network_dict = neural_dict.get(net_name)
        assert network_dict is not None, f"expected ({num_net}) number of networks, but net{i+1} was not passed through"

        network = create_network(network_dict)
        network_list.append(network)

    return network_list

def create_network(network_dict):
    type = network_dict.get('type')
    dims = network_dict.get('dims')
    activations = network_dict.get('activations')

    assert type in ['mlp'], f"({type}) is not a valid network type"
    assertions.not_none(type, dims, activations)
    assertions.dims(dims, activations)
    
    activations = convert.activation(activations)

    if type == 'mlp':
        network = MLPNet(dims, activations)
    
    return network

def get_train_dict(neural_dict):
    trainer_dict = neural_dict.get('trainer')
    assertions.not_none(trainer_dict)

    loss = trainer_dict.get('loss')
    optim = trainer_dict.get('optim') # dictionary
    num_epochs = trainer_dict.get('num_epochs')
    assertions.not_none(loss, optim, num_epochs)

    data = neural_dict.get('data')
    assertions.not_none(data)

    input_data = data.get('input')
    label = data.get('label')
    assertions.not_none(input_data, label)

    # Convert loss and optimizer
    converted_loss = convert.loss(loss)
    
    optimizer = optim.get('type')
    assertions.not_none(optimizer)
    converted_optim = convert.optimizer(optimizer)
    optim = copy.deepcopy(optim)
    optim['type'] = converted_optim # Dictionary

    trainer_param = {
        'loss': converted_loss,
        'optim': optim,
        'num_epochs': num_epochs,
        'input': input_data,
        'label': label
    }

    print(trainer_param)

    return trainer_param

def get_eval_dict(neural_dict):
    data = neural_dict.get('data')
    assertions.not_none(data)

    input_data = data['input']
    label = data['label']
    assertions.not_none(input_data, label)

    state = neural_dict.get('state')
    assertions.not_none(state)

    eval_param = {
        'input': input_data,
        'label': label,
        'state': state
    }

    return eval_param

def assert_not_none(*type_dicts):
    for type_dict in type_dicts:
        assert type_dict is not None, f'{type_dict} did not parse properly'

if __name__ == '__main__':
    neural_dict = 42
    print(create_network(neural_dict))