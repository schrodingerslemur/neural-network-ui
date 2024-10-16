import base64
import json
import torch

def parse_neural_dict(neural_dict, mode='train'):
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

def json_neural_dict(output, pickled_data, parameters):
    encoded_pickled_data = base64.b64encode(pickled_data).decode('utf-8')
    encoded_output = output.tolist()

    output = {'output': encoded_output, 'pickled_data': encoded_pickled_data}
    dict_output = parameters | output
    json_output = json.dumps(dict_output)

    # print(list(dict_output.keys()))
    # ['dims', 'activations', 'loss', 'optim_dict', 'num_epochs', 'input_data', 'label', 'output', 'pickled_data']
    return json_output

