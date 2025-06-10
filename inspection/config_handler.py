import json
import numpy as np

def save_config(filename, config):
    # Convert any numpy arrays to lists before saving
    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, bytes):  # for images, but not used here
            return obj.decode()
        return obj
    with open(filename, "w") as f:
        json.dump(config, f, default=convert, indent=2)

def load_config(filename):
    with open(filename, "r") as f:
        config = json.load(f)
    # Convert lists back to numpy arrays where needed in app logic
    return config
