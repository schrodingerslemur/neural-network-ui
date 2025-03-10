# PyTorch Optimizers

optimizer = torch.optim.SGD(model.parameters(), lr=0.01)               # Basic SGD
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9) # SGD with momentum

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)             # Adam, popular for deep learning
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)            # Adam with weight decay

optimizer = torch.optim.RMSprop(model.parameters(), lr=0.01)           # RMSprop, often used for RNNs
optimizer = torch.optim.Adagrad(model.parameters(), lr=0.01)           # Adagrad, good for sparse data and NLP
optimizer = torch.optim.Adadelta(model.parameters(), lr=1.0)           # Adadelta, extension of Adagrad with decay

optimizer = torch.optim.Adamax(model.parameters(), lr=0.002)           # Adamax, variant of Adam with infinity norm
optimizer = torch.optim.ASGD(model.parameters(), lr=0.01)              # ASGD, weight averaging for stability
optimizer = torch.optim.LBFGS(model.parameters(), lr=1)                # LBFGS, second-order, good for small datasets

optimizer = torch.optim.Rprop(model.parameters(), lr=0.01)             # Rprop, adjusts step sizes adaptively
optimizer = torch.optim.NAdam(model.parameters(), lr=0.002)            # NAdam, Adam with Nesterov momentum
optimizer = torch.optim.SparseAdam(model.parameters(), lr=0.01)        # SparseAdam, for sparse data (e.g., NLP)
