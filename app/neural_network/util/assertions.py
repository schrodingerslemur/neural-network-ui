import torch

class assertions:
    def dims(dims, activations): # Ensure len(dim) = len(activation) + 1
        assert (len(dims)-len(activations) == 1), 'Dim length should be activation length + 1'
    
    def data(inputs, label, dims): # Ensure input and label data has same dimensions as input and label dimensions
        assert inputs.size(-1) == dims[0], f'input size ({inputs.size(-1)}) does not match first dim size ({dims[0]})'
        assert label.size(-1) == dims[-1], f'label size ({label.size(-1)}) does not match last dim size ({dims[-1]})'
    def double(inputs, label): # Ensure input and label data type is double/float64
        assert inputs.dtype == torch.float64, f'inputs expected to be float64, but got {inputs.dtype}'
        assert label.dtype == torch.float64, f'labels expected to be float64, but got {label.dtype}'
    