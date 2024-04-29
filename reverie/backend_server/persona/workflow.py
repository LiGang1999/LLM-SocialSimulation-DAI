import sys
from action import *

class WorkFlow:
    def __init__(self):
        pass

    def work():
        pass

class GaWorkFlow(WorkFlow):
    def __init__(self):
        self.perceive = GaPerceive()
        self.retrieve = GaRetrieve()
        self.plan = GaPlan()
        self.execute = GaExecute()
        self.reflect = GaReflect()

    def work(self, persona, maze, personas, curr_tile, curr_time):
        persona.scratch.curr_tile = curr_tile

        new_day = False
        if not persona.scratch.curr_time: 
            new_day = "First day"
        elif (persona.scratch.curr_time.strftime('%A %B %d')
            != curr_time.strftime('%A %B %d')):
            new_day = "New day"
        persona.scratch.curr_time = curr_time

        perceived = self.perceive.action(persona, maze)
        retrieved = self.retrieve.action(persona, perceived)
        plan = self.plan.action(persona, maze, personas, new_day, retrieved)
        self.reflect.action(persona)

        return self.execute.action(persona, maze, personas, plan)
