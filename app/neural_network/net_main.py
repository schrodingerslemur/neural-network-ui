import torch
import torch.nn as nn
import pickle
import json
import sys

sys.path.append('app/neural_network/')
from trainer.trainer import trainer
from eval.eval import eval
from network.COMPnet import COMPnet
from network.create_network import create_network_list, get_train_dict, get_eval_dict
from util.data import data_convert
from util.parameters import assertions, parse


def neural_main(json_string):
    neural_dict = json.loads(json_string)
    mode = neural_dict['mode']
    assert mode in ['train', 'eval'], f"Invalid mode: expected 'train' or 'eval', but got ({mode})"

    if mode == 'train':
        return main_train(neural_dict)
    else:
        return main_eval(neural_dict)


def main_train(neural_dict):
    print('\nStarting main_train -----------------------------------------')
    
    # Initialize networks and training data
    networks = create_network_list(neural_dict)
    print('networks created:', networks)

    train_dict = get_train_dict(neural_dict)
    input_data, label = data_convert(train_dict['input'], train_dict['label'])
    
    # Assertions
    assertions.double(input_data, label)  # Ensure inputs are float64
    assertions.data(neural_dict, input_data, label)

    # Initialize network and trainer
    neural_net = COMPnet(networks)
    neural_trainer = trainer(neural_net, train_dict['loss'], train_dict['optim'])
    print('trainer created')

    # Train model
    cache_path = neural_trainer.train(input_data, label, num_epochs=train_dict['num_epochs'])
    print('training completed successfully')

    # Evaluate and save model
    output = eval(neural_net, cache_path, input_data)
    state_dict = neural_net.state_dict()
    pickled_data = pickle.dumps(state_dict)
    json_output = parse.dict_to_json(output, pickled_data, neural_dict)
    print('model saved and pickle file generated')

    return json_output


def main_eval(neural_dict):
    print('\nStarting main_eval------------------------------------')

    # Initialize networks and evaluation data
    networks = create_network_list(neural_dict)
    eval_dict = get_eval_dict(neural_dict)          # ['input', 'label', 'state']
    input_data= data_convert(eval_dict['input'], None)

    # Initialize network and evaluate
    neural_net = COMPnet(networks)
    print('network created')
    output = eval(neural_net, eval_dict['state'], input_data, mode='pickle')
    
    # Convert evaluation output to JSON
    output_dict = {'output': output.tolist(), 'state': eval_dict['state']}
    json_output = json.dumps(output_dict)
    print('evaluation complete')

    return json_output


if __name__ == "__main__":
    # Example for training
    neural_dict_train = {
        "mode": "train",
        "num_net": 2,
        "net1": {
            "type": "mlp",
            "dims": [32, 256, 256, 256, 2],
            "activations": [
                ["threshold", 0.1, 0, "relu"],
                ["threshold", 0.1, 0],
                ["threshold", 0.1, 0],
                [None]
            ]
        },
        "net2": {
            "type": "cnn",
            "dims": [
            {"layer": "conv", "in_channels": 3, "out_channels": 16, "kernel_size": 3},
            {"layer": "pool", "type": "avg", "kernel_size": 2, "stride": 2},  # Pooling layer
            {"layer": "conv", "in_channels": 16, "out_channels": 32, "kernel_size": 3},
            {"layer": "pool", "type": "max", "kernel_size": 2, "stride": 2} 
            ],
            "activations": ["relu", ["relu", "relu"], None, "selu"]
        },
        "trainer": {
            "loss": "mse",
            "optim": {"type": "adam", "lr": 0.01},
            "num_epochs": 100
        },
        "data": {
            "input": "torch.randn(1,2,32,32)",
            "label": "torch.randn(1,32,5,16)"
        }
    }

    json_string_train = json.dumps(neural_dict_train)
    output_train = neural_main(json_string_train)

    # Example for evaluation
    # output_train_dict = json.loads(output_train)
    # state = output_train_dict['pickled_data']

    # neural_dict_eval = {
    #     "mode": "eval",
    #     "num_net": 1,
    #     "net1": {
    #         "type": "mlp",
    #         "dims": [2, 256, 256, 256, 2],
    #         "activations": [
    #             ["threshold", 0.1, 0, "relu"],
    #             ["threshold", 0.1, 0],
    #             ["threshold", 0.1, 0],
    #             ["threshold", 0.1, 0]
    #         ]
    #     },
    #     "state": state,
    #     "data": {
    #         "input": [1, 2],
    #         "label": [2, 4]
    #     }
    # }

    # json_string_eval = json.dumps(neural_dict_eval)
    # output_eval = main(json_string_eval)

