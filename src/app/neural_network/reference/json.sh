Input JSON format
# Train
{
    "mode": "train",
    "num_net": 1
    "net1": {
        "type": "mlp",
        "dims": [
            10,
            256,
            256,
            256,
            10
        ],
        "activations": [
            ["threshold", 0.1, 0, "relu"],
            ["threshold", 0.1, 0],
            ["threshold", 0.1, 0],
            ["threshold", 0.1, 0]
        ]
    },
    "trainer": {
            "loss": "mse",
            "optim": {
                "type": "adam",
                "lr": 0.01
                }
            "num_epochs": 100
        },
        "data": {
            "input": [
                1,
                2
            ],
            "label": [
                2,
                4
            ]
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
dict_output = {'output': output, 'state': state} # state is pickle file
json_output = json.dumps(dict_output)
