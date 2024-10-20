import torch.nn as nn

class COMPnet(nn.Module):
    def __init__(self, networks):
        super().__init__()
        self.net_num = len(networks)

        print(networks)
        # nn.ModuleList is used to store a list of networks (nn.Module instances)
        self.networks = nn.ModuleList(networks)


    def forward(self, x):
        # Forward pass through each network sequentially
        for net in self.networks:
            x = net(x)
        return x
