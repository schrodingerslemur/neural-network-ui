import torch
import torch.nn as nn
import sys

sys.path.append('../')
from util.parameters import assertions, convert

# Convolutional and pooling layers (input and output layers) 
# Conv2d: in_channels, out_channels, kernel_size, stride, padding
# MaxPool2d: kernel_size, stride

class CNNNet(nn.Module):
    def __init__(self, dims, activations):
        print('dims', dims)
        print('activations', activations)
        print('true', dims is None)
        super().__init__()
        # Example input
        #     "dims": [
        #     {"layer": "conv", "in_channels": 3, "out_channels": 16, "kernel_size": 3},
        #     {"layer": "pool", "type": "avg", "kernel_size": 2, "stride": 2},  # Pooling layer
        #     {"layer": "conv", "in_channels": 16, "out_channels": 32, "kernel_size": 3},
        #     {"layer": "pool", "type": "max", "kernel_size": 2, "stride": 2}   # Pooling layer
        #      ]
        #     "activations": ["relu", ["relu", "relu"], None, "selu"] # len(activations) = len(dims) 
        layers = []

        for i in range(len(dims)):
            dim = dims[i]
            activation = activations[i]

            layer = dim.get('layer')
            assert layer in ['conv', 'pool'], f"expected layer to be 'conv' or 'pool', but got ({layer})"

            if layer == 'conv':
                in_channel = dim.get('in_channels')
                out_channel = dim.get('out_channels')
                kernel = dim.get('kernel_size')

                # Need stride and paddding too
                stride = dim.get('stride')
                if stride is None:
                    stride = 3

                padding = dim.get('padding')
                if padding is None:
                    padding = 2
                    
                assertions.not_none(in_channel, out_channel, kernel)
                assert all(isinstance(var, int) for var in (in_channel, out_channel, kernel, stride, padding))

                layer = nn.Conv2d(in_channel, out_channel, kernel_size=kernel, stride=stride, padding=padding)

            elif layer == 'pool':
                kernel_size = dim.get('kernel_size')
                stride = dim.get('stride')
                pool_type = dim.get('type')

                assertions.not_none(kernel_size, stride)
                assert pool_type in ['avg', 'max'], f"expected pooling type to be 'avg' or 'max' but got ({pool_type})"

                if pool_type == 'avg':
                    layer = nn.AvgPool2d(kernel_size, stride)
                else:
                    layer = nn.MaxPool2d(kernel_size, stride)
            
            layers.append(layer)
            print('activation', activation)
            if activation is not None:
                if isinstance(activation, list):
                    layers.extend(activation)   
                else:
                    layers.append(activation)       

        print('cnn layers', layers, type(layers))
        self.network = nn.ModuleList(layers)

        self.double()

    def forward(self, x):
        for layer in self.network:
            print(layer)
            print(x.shape, 'shape')
            x = layer(x)
        return x