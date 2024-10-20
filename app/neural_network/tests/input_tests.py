import json
import sys

sys.path.append('../')
from util.parameters import convert
"""
Format:
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
"""
activations = convert.lists('activation', 'list')
optimizers = convert.lists('optimizer', 'list')
losses = convert.lists('loss', 'list')

non_opt = ['relu', 'prelu', 'selu', 'gelu', 'sigmoid', 'tanh', 'softplus', 'softsign', 'relu6', 'hardsigmoid', 'hardswich', 'mish', 'tanhshrink']
optional = ['leaky_relu', 'elu', 'softmax', 'log_softmax', 'hardtanh', 'hardshrink', 'softshrink', 'threshold']
two_inputs = ['hardtanh']
dim_inputs = ['softmax', 'log_softmax']

for act in dim_inputs:
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
                [act, 1, "threshold", 0.1, 0],
                ["threshold", 0.1, 0, act, 1, act, 1],
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

    filename = f"act/dim/{act}.json"
    with open(filename, 'w') as file:
        json.dump(neural_dict, file, indent=4)
