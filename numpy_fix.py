import numpy as np

# Update numpy float types
if hasattr(np, 'float'):
    NUMPY_FLOAT = np.float64
else:
    NUMPY_FLOAT = float

def fix_numpy_float(number):
    """Convert number to proper numpy float type"""
    return NUMPY_FLOAT(number)