import itk
import numpy as np


class CommandIterationUpdate:
    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.optimizer.AddObserver(itk.IterationEvent(), self)

    def __call__(self, *args):
        iteration = self.optimizer.GetCurrentIteration()
        metric_value = self.optimizer.GetValue()
        position = np.array(self.optimizer.GetCurrentPosition())
        print(f"Iteration {iteration}: Value = {metric_value}, Position = {position}")
