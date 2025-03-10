from torch.utils.data import Dataset

class Input_Dataset(Dataset):
    def __init__(self, input_data, labels, datatype='tensor', transform=None): # transforms for future image augmentation
        self.data = self.convert_type(input_data, datatype)
        self.labels = self.convert_type(labels, datatype)
        self.transform = transform

    def convert_type(self, data, datatype):
        if datatype == 'tensor':
            return data
        # elif datatype in ['np', 'list']
        # else:
            # Assert error, datatype not valid

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sample = self.data[idx]
        label = self.labels[idx]

        if self.transform:
            sample = self.transform(sample)
        
        return sample, label

# Dataloader call 
'''
dataset = Input_Dataset(input_data, labels) # datatype='tensor', transform=None
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
for batch_data, batch_labels in dataloader:
    training loop

# Needs to be called within trainer function
'''