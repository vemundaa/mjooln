import logging
import numpy as np

from mjooln.core.dic_doc import Dic

logger = logging.getLogger(__name__)


class Stats(Dic):

    def __init__(self):
        # TODO: Add configurable history for sum and delta. IE sliding averages
        self.x = np.nan
        self.count = 0
        self.sum = 0.0
        # Sum of squared elements
        self.sum_squared = 0.0
        # Sum of inverse elements
        self.sum_inverse = 0.0
        self.max = np.nan
        self.min = np.nan
        self.delta = np.nan
        self.sum_delta = np.nan
        self.sum_delta_absolute = np.nan

    def update(self, x):
        if not np.isnan(x):
            x = float(x)
            self.count += 1
            if not np.isnan(self.x):
                self.delta = x - self.x
            self.x = x
            self.sum += x
            self.sum_squared += x * x
            if x != 0.0:
                self.sum_inverse += 1/x
            if not np.isnan(self.delta):
                if np.isnan(self.sum_delta):
                    self.sum_delta = self.delta
                    self.sum_delta_absolute = np.abs(self.delta)
                else:
                    self.sum_delta += self.delta
                    self.sum_delta_absolute += np.abs(self.delta)
            if np.isnan(self.max) or x > self.max:
                self.max = x
            if np.isnan(self.min) or x < self.min:
                self.min = x

    def average(self):
        if self.count > 1:
            return self.sum / self.count
        else:
            return np.nan

    def std(self):
        if self.count > 1:
            return np.sqrt((self.count * self.sum_squared - self.sum * self.sum) /
                           (self.count * (self.count - 1)))
        else:
            return np.nan

    def average_delta(self):
        if self.count > 1:
            return self.sum_delta / (self.count - 1)
        else:
            return np.nan

    def dic(self, ignore_private=True):
        dic = super().dic(ignore_private=ignore_private)
        dic['average'] = self.average()
        dic['std'] = self.std()
        dic['average_delta'] = self.average_delta()
        return dic
