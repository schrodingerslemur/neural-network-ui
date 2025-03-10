import torch
import torch.nn as nn

from network.transform import transform

class MLPNet(nn.Module):
    def __init__(self, dims: list, activations: list, transform=None): 
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

        if transform is not None:
            assert isinstance(transform, list), f"expected transform to be tuple, but got {type(transform)}"

            assert transform[0] in ['squeeze', 'unsqueeze'], f"expected transform[0] to be 'squeeze' or 'unsqueeze' but got {transform[0]}"

            assert all(isinstance(val, int) for val in transform[1:]), f"expected transform[1:] to be dim values (int) but got {transform[1:]}"

            self.transform = transform
        else:
            self.transform = None
        
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)

        if self.transform is not None:
            x = transform.forward(x, self.transform)

        print("tensor shape", x.shape)
        return x


    