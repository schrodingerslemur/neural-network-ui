import torch
import torch.nn as nn
import base64
import json

class parse:
    def dict_to_json(output, pickled_data, neural_dict): # Only for train
        encoded_pickled_data = base64.b64encode(pickled_data).decode('utf-8')
        encoded_output = output.tolist()

        output = {'output': encoded_output, 'pickled_data': encoded_pickled_data}
        dict_output = neural_dict | output

        json_output = json.dumps(dict_output)

        return json_output
    
class convert:
    def lists(param, datatype):
        assert param in ['activation', 'loss', 'optimizer'], 'invalid param type'
        assert datatype in ['list', 'dict'], 'invalid datatype'
        activation = {
                        'relu': nn.ReLU,
                        'leaky_relu': nn.LeakyReLU,
                        'prelu': nn.PReLU,
                        'elu': nn.ELU,
                        'selu': nn.SELU,
                        'gelu': nn.GELU,
                        'sigmoid': nn.Sigmoid,
                        'tanh': nn.Tanh,
                        'softmax': nn.Softmax,
                        'log_softmax': nn.LogSoftmax,
                        'softplus': nn.Softplus,
                        'softsign': nn.Softsign,
                        'hardtanh': nn.Hardtanh,
                        'hardshrink': nn.Hardshrink,
                        'softshrink': nn.Softshrink,
                        'relu6': nn.ReLU6,
                        'hardsigmoid': nn.Hardsigmoid,
                        'hardswish': nn.Hardswish,
                        'mish': nn.Mish,
                        'tanhshrink': nn.Tanhshrink,
                        'threshold': nn.Threshold
                    }
        loss = {
                    'cel': nn.CrossEntropyLoss,
                    'nl': nn.NLLLoss,
                    'bce': nn.BCELoss,
                    'bce_logits': nn.BCEWithLogitsLoss,
                    'ml_margin': nn.MultiLabelMarginLoss,
                    'ml_soft_margin': nn.MultiLabelSoftMarginLoss,
                    'mm': nn.MultiMarginLoss,
                    'mse': nn.MSELoss,
                    'l1': nn.L1Loss,
                    'smooth_l1': nn.SmoothL1Loss,
                    'poisson_nll': nn.PoissonNLLLoss,
                    'margin_rank': nn.MarginRankingLoss,
                    'hinge_embed': nn.HingeEmbeddingLoss,
                    'cosine_embed': nn.CosineEmbeddingLoss,
                    'triplet_margin': nn.TripletMarginLoss,
                    'kldiv': nn.KLDivLoss,
                    'ctc': nn.CTCLoss,
                    'huber': nn.HuberLoss,
                    'triplet_margin_dist': nn.TripletMarginWithDistanceLoss,
                    'gaussian_nll': nn.GaussianNLLLoss
                }

        optimizer = {
                        'sgd': torch.optim.SGD,
                        'adam': torch.optim.Adam,
                        'adamw': torch.optim.AdamW,
                        'rmsprop': torch.optim.RMSprop,
                        'adagrad': torch.optim.Adagrad,
                        'adadelta': torch.optim.Adadelta,
                        'adamax': torch.optim.Adamax,
                        'asgd': torch.optim.ASGD,
                        'lbfgs': torch.optim.LBFGS,
                        'rprop': torch.optim.Rprop,
                        'nadam': torch.optim.NAdam,
                        'sparse_adam': torch.optim.SparseAdam
                    }


        if param == 'activation':
            return list(activation.keys()) if datatype == 'list' else activation
        elif param == 'loss':
            return list(loss.keys()) if datatype == 'list' else loss
        else:
            return list(optimizer.keys()) if datatype == 'list' else optimizer
        
    def activation(activation_inputs):
        optional = ['leaky_relu', 'elu', 'softmax', 'log_softmax', 'hardtanh', 'hardshrink', 'softshrink', 'threshold']
        two_inputs = ['hardtanh', 'threshold']
        dim_inputs = ['softmax', 'log_softmax']

        converted_activations = []
        for activation_input in activation_inputs:
            # If the activation input is not a list, it's a single activation
            if not isinstance(activation_input, list):
                print('input', activation_input)
                assert activation_input in convert.lists('activation', 'list') or activation_input is None, f'{activation_input} is an invalid activation type'
                if activation_input is None:
                    converted_activations.append(None)
                else:
                    converted_activations.append(convert.lists('activation', 'dict')[activation_input]())
            else:
                # Tuple handling: convert each element inside the tuple
                tupled_inputs = []
                for idx in range(len(activation_input)):
                    element = activation_input[idx]
                    # If it is a string, it is an activation, not a parameter
                    if isinstance(element, str):
                        assert element in convert.lists('activation', 'list'), f'{element} is an invalid activation type'
                        if (element not in optional) or (idx+1 >= len(activation_input)) or (isinstance(activation_input[idx+1], str)):
                            tupled_inputs.append(convert.lists('activation', 'dict')[element]())
                        elif element in two_inputs:
                            first = activation_input[idx+1]
                            second = activation_input[idx+2]
                            tupled_inputs.append(convert.lists('activation', 'dict')[element](first, second))
                        elif element in dim_inputs:
                            dim = activation_input[idx+1]
                            tupled_inputs.append(convert.lists('activation', 'dict')[element](dim=dim))
                        else:
                            arg = activation_input[idx+1]
                            tupled_inputs.append(convert.lists('activation', 'dict')[element](arg))
                converted_activations.append(tupled_inputs)
        
        return converted_activations
    
    def loss(loss_input):
        assert loss_input in convert.lists('loss', 'list'), f'{loss_input} is an invalid loss type'

        return convert.lists('loss', 'dict')[loss_input]() 
    
    def optimizer(optim):
        assert optim in convert.lists('optimizer', 'list')
        # Assert optim_param are correct

        return convert.lists('optimizer', 'dict')[optim]
    

class assertions:
    def dims(dims, activations): # Ensure len(dim) = len(activation) + 1
        assert (len(dims)-len(activations) == 1), 'Dim length should be activation length + 1'
    
    def data(neural_dict, inputs, label): # Ensure input and label data has same dimensions as input and label dimensions
        num_net = neural_dict['num_net']
        first_net = neural_dict['net1']
        last_net = neural_dict[f'net{num_net}']

        first_type = first_net['type']
        last_type = last_net['type']

        if first_type == 'mlp':
            first_dim = first_net['dims'][0]
        elif first_type == 'cnn':
            first_dim = first_net['in_channels']

        if last_type == 'mlp':
            last_dim = last_net['dims'][-1]
        elif last_type == 'cnn':
            # Solve for last_dim: either pooling or convolution layers
            last_dim = assertions.last_cnn(last_net)

        
        assert inputs.size(-1) == first_dim, f'input size ({inputs.size(-1)}) does not match first dim size ({first_dim})'
        assert label.size(-1) == last_dim, f'label size ({label.size(-1)}) does not match last dim size ({last_dim})'

    def last_cnn(net):
        last_layer = net['dims'][-1]

        if last_layer['layer'] == 'conv':
            output = last_layer['out_channels']
        else:
            kernel = last_layer['kernel_size']
            stride = last_layer['stride']

            second_last_layer = net['dims'][-2]
            second_last_output = second_last_layer['out_channels']

            output = ((second_last_output-kernel)/stride) + 1

        return int(output)
            


    def double(inputs, label): # Ensure input and label data type is double/float64
        assert inputs.dtype == torch.float64, f'inputs expected to be float64, but got {inputs.dtype}'
        assert label.dtype == torch.float64, f'labels expected to be float64, but got {label.dtype}'

    def not_none(*type_dicts):
        for type_dict in type_dicts:
            assert type_dict is not None, f'{type_dict} did not parse properly'

