import torch
import torch.nn as nn

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
        for activation_input in activation_inputs:
            assert activation_input in convert.lists('activation', 'list'), f'{activation_input} is an invalid activation type'

        return [convert.lists('activation','dict')[activation_input]() for activation_input in activation_inputs]
    
    def loss(loss_input):
        assert loss_input in convert.lists('loss', 'list'), f'{loss_input} is an invalid loss type'

        return convert.lists('loss', 'dict')[loss_input]() 
    
    def optimizer(opt_input):
        optim = opt_input['type']

        assert optim in convert.lists('optimizer', 'list')
        # Assert optim_param are correct

        return convert.lists('optimizer', 'dict')[optim], opt_input
    
    def optimizer_parameter(optim_param):
        optim = optim_param['type']

