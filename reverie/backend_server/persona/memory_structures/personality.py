import sys

from persona.memory_structures.memory import *

class BigFiveTree: 
    def __init__(self): 
        pass

class PersonalityTree(Memory): 
    def __init__(self): 
        super().__init__()
        self.bigFiveTree = BigFiveTree()
