Input JSON format
# Train
neural_dict = {
                'mode': 'train',
                'network': {
                    'dims': [10, 256, 256, 256, 10],
                    'activations': ['relu', 'relu', 'relu', 'relu']
                },
                'trainer': {
                    'parameters': {
                        'loss': 'mse',
                        'optim': {
                            'type': 'adam',
                            'lr': 0.01},
                        'num_epochs': 100
                    },
                    'data': {
                        'input': [1,2,3,4,5,6,7,8,9,10],
                        'label': [2,4,6,8,10,12,14,16,18,20]
                    }
                }
            }
# Eval
neural_dict_eval = {
            'mode': 'eval',
            'network': {
                'dims': [10, 256, 256, 256, 10],
                'activations': ['relu', 'relu', 'relu', 'relu'],
                'state': state
            },
            'trainer': {
                'parameters': {
                    'loss': 'mse',
                    'optim': {
                        'type': 'adam',
                        'lr': 0.01},
                    'num_epochs': 100
                },
                'data': {
                    'input': [1,2,3,4,5,6,7,8,9,10],
                    'label': [2,4,6,8,10,12,14,16,18,20]
                }
            }
        }
Output JSON format
# Train
Dict.keys(): ['dims', 'activations', 'loss', 'optim_dict', 'num_epochs', 'input_data', 'label', 'output', 'pickled_data'] in JSON

# Eval
Output tensor to list in JSON (careful as it is a list now)
