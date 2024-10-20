import torch
import torch.nn as nn

class MLPNet(nn.Module):
    def __init__(self, dims: list, activations: list): 
        super().__init__()
        
        layer_list = []

        for i in range(len(dims)-1):
            input_dim = dims[i]
            output_dim = dims[i+1]

            layer = nn.Linear(input_dim, output_dim).double()
            activation = activations[i]

            layer_list.append(layer)
            if activation is not None:
                if isinstance(activation, list):
                    layer_list.extend(activation)
                else:
                    layer_list.append(activation)

        self.layers = nn.ModuleList(layer_list)

        self.double()
        
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


    