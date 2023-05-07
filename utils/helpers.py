import numpy as np

class Rounder(object):
    @staticmethod
    def round(arr):
        decimals = 5
        arr = np.power(10, decimals) * np.round(arr, decimals=decimals)
        return arr.astype(int)