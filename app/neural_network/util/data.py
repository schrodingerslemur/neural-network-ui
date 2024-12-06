import torch
import numpy as np
import pandas as pd
import re
# Changes any datatype to tensor
def data_convert(d1, d2): # input_data and label
    if d2 is None:
        return convert(d1)
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
    elif isinstance(d, str):
        return convert_str(d)
    else:
        raise TypeError(f"Unsupported data type: {type(d)}")

def convert_str(d):
    #torch.randn(1,1,16,2)
    assert d.startswith('torch.randn'), f"expected string to start with 'torch.randn' but got {d}"

    dims = list(map(int, re.findall(r'\d+', d)))

    return torch.randn(*dims, dtype=torch.float64)

    