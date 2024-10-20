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
        # print(dict_output)
        try:
            json.dumps(neural_dict)
        except:
            print(neural_dict)
        print('dicttype', type(dict_output))
        json_output = json.dumps(dict_output)

        return json_output
    
    def dict_to_param(neural_dict, mode='train'):
        assert mode in ['train', 'eval'], f"expected mode to be 'train' or 'eval', but got ({mode})"
        def assert_not_none(*type_dicts):
            for type_dict in type_dicts:
                assert type_dict is not None, f'{type_dict} did not parse properly'

        # Network parse
        network_dict = neural_dict.get('network')
        assert_not_none(network_dict)
        dims = network_dict.get('dims')
        activations = network_dict.get('activations')
        assert_not_none(dims, activations)

        # Trainer parse
        trainer_dict = neural_dict.get('trainer')
        assert_not_none(trainer_dict)

        # Parameters parse
        parameters_dict = trainer_dict.get('parameters')
        assert_not_none(parameters_dict)
        loss = parameters_dict.get('loss')
        optim_dict = parameters_dict.get('optim')  
        num_epochs = parameters_dict.get('num_epochs')
        assert_not_none(loss, optim_dict, num_epochs)

        # Data parse
        data_dict = trainer_dict.get('data')
        assert_not_none(data_dict)
        input_data = data_dict.get('input')
        label = data_dict.get('label')
        assert_not_none(input_data, label)

        if mode == 'eval':
            pickle_file = network_dict.get('state')
            assert_not_none(pickle_file)
            return {
            'dims': dims,
            'activations': activations,
            'loss': loss,
            'optim_dict': optim_dict,
            'num_epochs': num_epochs,
            'input_data': input_data,
            'label': label,
            'state': pickle_file
            }
        
        return {
            'dims': dims,
            'activations': activations,
            'loss': loss,
            'optim_dict': optim_dict,
            'num_epochs': num_epochs,
            'input_data': input_data,
            'label': label,
        }
    
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
                assert activation_input in convert.lists('activation', 'list'), f'{activation_input} is an invalid activation type'
                converted_activations.append(convert.lists('activation', 'dict')[activation_input]())
            else:
                # Tuple handling: convert each element inside the tuple
                tupled_inputs = []
                for idx in range(len(activation_input)):
                    element = activation_input[idx]
                    # If it is a string, it is an activation, not a parameter
                    if isinstance(element, str):
                        assert element in convert.lists('activation', 'list'), f'{element} is an invalid activation type'
                        print(element)
                        print(idx+1, len(activation_input))
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
    
    def optimizer_parameter(optim_param):
        optim = optim_param['type']

class assertions:
    def dims(dims, activations): # Ensure len(dim) = len(activation) + 1
        assert (len(dims)-len(activations) == 1), 'Dim length should be activation length + 1'
    
    def data(neural_dict, inputs, label): # Ensure input and label data has same dimensions as input and label dimensions
        num_net = neural_dict['num_net']
        first_dim = neural_dict['net1']['dims'][0]
        last_dim = neural_dict[f'net{num_net}']['dims'][-1]
        
        assert inputs.size(-1) == first_dim, f'input size ({inputs.size(-1)}) does not match first dim size ({first_dim})'
        assert label.size(-1) == last_dim, f'label size ({label.size(-1)}) does not match last dim size ({last_dim})'

    def double(inputs, label): # Ensure input and label data type is double/float64
        assert inputs.dtype == torch.float64, f'inputs expected to be float64, but got {inputs.dtype}'
        assert label.dtype == torch.float64, f'labels expected to be float64, but got {label.dtype}'

    def not_none(*type_dicts):
        for type_dict in type_dicts:
            assert type_dict is not None, f'{type_dict} did not parse properly'

