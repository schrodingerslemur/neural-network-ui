import torch
import torch.nn as nn
import pickle
import json

from trainer.trainer import trainer
from eval.eval import eval
from network.MLPnet import MLPNet
from network.COMPnet import COMPnet
from network.create_network import create_network_list, get_train_dict, get_eval_dict

from util.data import data_convert
from util.parameters import convert, assertions, parse

def main(json_string):
    neural_dict = json.loads(json_string)
    mode = neural_dict['mode']
    
    assert mode in ['train', 'eval'], f"invalid mode: expected 'train' or 'eval, but got ({mode})"

    output = main_train(neural_dict) if mode == 'train' else main_eval(neural_dict)
    return output

def main_train(neural_dict):
    print('\n\n\nStarting main_train -----------------------------------------')
    
    networks = create_network_list(neural_dict)
    print(networks)

    train_dict = get_train_dict(neural_dict)
    loss = train_dict['loss']
    optim = train_dict['optim']
    num_epochs = train_dict['num_epochs']
    input_data = train_dict['input']
    label = train_dict['label']

    # Conversions
    input_data, label = data_convert(input_data, label)

    # Assertions
    assertions.double(input_data, label) # Check for float64
    assertions.data(neural_dict, input_data, label)

    ### Network and training initialization -------
    neural_net = COMPnet(networks)
    print('network created')
    ######################################################################################################
    
    neural_trainer = trainer(neural_net, loss, optim)
    print('trainer created')
    
    cache_path = neural_trainer.train(input_data, label, num_epochs=num_epochs)
    print('trained successfully')
    
    output = eval(neural_net, cache_path, input_data)

    # Save model and output into JSON string
    state_dict = neural_net.state_dict()
    pickled_data = pickle.dumps(state_dict)
    json_output = parse.dict_to_json(output, pickled_data, neural_dict)
    print('pickle file saved')

    print('main_train output keys', list(json.loads(json_output).keys()))
    # main_train output keys ['mode', 'num_net', 'net1', 'trainer', 'data', 'output', 'pickled_data']

    return json_output 


def main_eval(neural_dict):
    print('\n\n\nStarting main_eval------------------------------------')

    networks = create_network_list(neural_dict)

    eval_dict = get_eval_dict(neural_dict)
    input_data = eval_dict['input']
    label = eval_dict['label']
    state = eval_dict['state']

    ### Conversions (and assertions) ----------------
    # Conversions
    input_data, label = data_convert(input_data, label)

    # Assertions
    assertions.double(input_data, label)
    assertions.data(neural_dict, input_data, label) # Check dimension sizes for inputs and labels

    ### Network and training initialization -------
    neural_net = COMPnet(networks)
    print('network created')
    
    output = eval(neural_net, state, input_data, mode='pickle') # state is pickle file
    output = output.tolist()

    dict_output = {'output': output, 'state': state}
    json_output = json.dumps(dict_output)

    print('evaluation complete')
    return json_output

if __name__ == "__main__":
    # train test
    neural_dict = {
    "mode": "train",
    "num_net": 1,
    "net1": {
        "type": "mlp",
        "dims": [
            2,
            256,
            256,
            256,
            2
        ],
        "activations": [
            ["threshold", 0.1, 0, "relu"],
            ["threshold", 0.1, 0],
            ["threshold", 0.1, 0],
            ["threshold", 0.1, 0]
        ]
    },
    "trainer": {
        "loss": "mse",
        "optim": {
            "type": "adam",
            "lr": 0.01
        },
        "num_epochs": 100
    },
    "data": {
        "input": [
            1,
            2
        ],
        "label": [
            2,
            4
        ]
    }
}


    
    json_string = json.dumps(neural_dict)

    output = main(json_string)

    # eval test
    # ['dims', 'activations', 'loss', 'optim_dict', 'num_epochs', 'input_data', 'label', 'output', 'pickled_data']
    output = json.loads(output)
    state = output['pickled_data']
    print('statetype', type(state))

    neural_dict_eval = {
    "mode": "eval",
    "num_net": 1,
    "net1": {
        "type": "mlp",
        "dims": [
            2,
            256,
            256,
            256,
            2
        ],
        "activations": [
            ["threshold", 0.1, 0, "relu"],
            ["threshold", 0.1, 0],
            ["threshold", 0.1, 0],
            ["threshold", 0.1, 0]
        ]
    },
    "state": state,
    "data": {
        "input": [
            1,
            2
        ],
        "label": [
            2,
            4
        ]
    }
}
    json_string = json.dumps(neural_dict_eval)
    output = main(json_string)
    # in future: number of networks should be key, then network --> network1, network2 , etc.
