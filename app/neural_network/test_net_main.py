import json

from util.parameters import convert
from net_main import main

activations = convert.lists('activation', 'list')
optimizers = convert.lists('optimizer', 'list')
losses = convert.lists('loss', 'list')

non_opt = ['relu', 'prelu', 'selu', 'gelu', 'sigmoid', 'tanh', 'softplus', 'softsign', 'relu6', 'hardsigmoid', 'hardswish', 'mish', 'tanhshrink']
optional = ['leaky_relu', 'elu',  'softshrink', 'threshold']
two_inputs = ['hardtanh']
dim_inputs = ['softmax', 'log_softmax']

# softmax and log_softmax [-1,0] range
for act in dim_inputs:
    filename = f"tests/act/dim/{act}.json"
    with open(filename, 'r') as file:
        json_data = json.load(file)
        json_string = json.dumps(json_data)
        print(filename)
        main(json_string)

        # ['threshold', 0.1, 0, 'leaky_relu', 0.5, 'leaky_relu']