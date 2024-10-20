import torch
import torch.nn
import base64
import pickle

def eval(network, cache_path, input, mode='cache'): # cache_path can be cache path or pickle file
    assert mode in ['cache', 'pickle'], f"expected mode to be 'cache', or 'pickle', but got ({mode})"

    if mode == 'pickle':
        pickled_data = cache_path
        if isinstance(pickled_data, str):
            pickled_data = base64.b64decode(pickled_data.encode('utf-8'))
    
        # Unpickle the state_dict
        state_dict = pickle.loads(pickled_data)
        
        # Validate and load with strict mode to detect any mismatches
        try:
            network.load_state_dict(state_dict, strict=True)
            print("model loaded successfully")
        except RuntimeError as e:
            print(f"error: {e}")
            print("mismatch detected in the model parameters")
            print("attempting to load with strict=False for partial loading")
            
            # Load with strict=False for partial compatibility
            incompatible_keys = network.load_state_dict(state_dict, strict=False)
            print(f"missing keys: {incompatible_keys.missing_keys}")
            print(f"unexpected keys: {incompatible_keys.unexpected_keys}")
            
            if not incompatible_keys.missing_keys and not incompatible_keys.unexpected_keys:
                print("partial load successful with no parameter mismatches")
            else:
                print("some parameters could not be loaded due to architecture differences")

    else:
        network.load_state_dict(torch.load(cache_path, weights_only=True))

    output = network(input)
    return output