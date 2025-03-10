import torch
import torch.optim
import sys
import os
import tempfile

from torch.utils.data import DataLoader

sys.path.append('../')
from dataloader.dataset import Input_Dataset

# Epoch, loss, optimizer
class trainer:
    def __init__(self, network, loss, optim):
        self.network = network
        self.loss = loss

        optimizer = optim['type']
        lr = optim.get('lr')
        lr = 0.001 if lr is None else lr
        momentum = optim.get('momentum')

        if momentum is None:
            self.optim = optimizer(network.parameters(), lr=lr)
        else:
            self.optim = optimizer(network.parameters(), lr=lr, momentum=momentum)

    def train(self, input_data, label, num_epochs=100, batch_size=16, print_every=10):
        dataset = Input_Dataset(input_data, label)
        dataloader = DataLoader(dataset, batch_size=batch_size)
        
        for epoch in range(num_epochs):
            for batch_data, batch_labels in dataloader:
                output = self.network(batch_data)

                computed_loss = self.loss(output, batch_labels)
                self.optim.zero_grad()

                computed_loss.backward()
                self.optim.step()

            if epoch % print_every == 0:
                print(f'(Epoch: {epoch}, Loss:{computed_loss.item()}')

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            cache_path = temp_file.name
            torch.save(self.network.state_dict(), cache_path)
        
        return cache_path
    
    
'''
dataset = Input_Dataset(input_data, labels) # datatype='tensor', transform=None
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
for batch_data, batch_labels in dataloader:
    training loop
'''
