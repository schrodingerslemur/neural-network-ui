import torch
import numpy as np
import pandas as pd
# Changes any datatype to tensor
def data_convert(d1, d2): # input_data and label
    return convert(d1), convert(d2)

def convert(d):
    if isinstance(d, torch.Tensor):
        return d.double()
    elif isinstance(d, list):
        return torch.tensor(d, dtype=torch.float64)
    elif isinstance(d, np.ndarray):
        return torch.from_numpy(d).double()
    elif isinstance(d, pd.DataFrame):
        return torch.tensor(d.values, dtype=torch.float64)
    else:
        raise TypeError(f"Unsupported data type: {type(d)}")

    