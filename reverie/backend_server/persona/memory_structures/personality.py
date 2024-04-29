import sys

from memory import *

class BigFiveTree: 
    def __init__(self): 
        pass

class PersonalityTree(Memory): 
    def __init__(self): 
        super().__init__()
        self.bigFiveTree = BigFiveTree()
