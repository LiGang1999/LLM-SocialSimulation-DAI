import datetime  # extend planning cycle
import pprint
import sys

from persona.action import *
from utils.logs import L


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
        elif persona.scratch.curr_time.strftime("%A %B %d") != curr_time.strftime("%A %B %d"):
            new_day = "New day"
            if curr_time.strftime("%A %B %d") > maze.last_planning_day.strftime(
                "%A %B %d"
            ):  # extend planning cycle
                maze.need_stagely_planning = True
        persona.scratch.curr_time = curr_time

        perceived = self.perceive.action(persona, maze)
        retrieved = self.retrieve.action(persona, perceived)
        plan = self.plan.action(persona, maze, personas, new_day, retrieved)
        self.reflect.action(persona)

        return self.execute.action(persona, maze, personas, plan)


class DaiWorkFlow(WorkFlow):
    def __init__(self):
        self.perceive = DaiPerceive()
        self.retrieve = DaiRetrieve()
        self.plan = DaiPlan()
        self.execute = DaiExecute()
        self.reflect = DaiReflect()

    def work(self, persona, maze, curr_time):

        new_day = False
        if not persona.scratch.curr_time:
            new_day = "First day"
        elif persona.scratch.curr_time.strftime("%A %B %d") != curr_time.strftime("%A %B %d"):
            new_day = "New day"
        persona.scratch.curr_time = curr_time

        L.debug(f"{persona.name} Perceive begin")
        perceived, all_news = self.perceive.action(persona, maze)
        L.debug(f"{persona.name} Perceive end, Retrieve begin.")
        retrieved = self.retrieve.action(persona, perceived)
        L.debug(f"{persona.name} Retrieve end, Plan begin.")
        plan = self.plan.action(persona, retrieved)
        L.debug(f"{persona.name} Plan end, Execute begin. plan={plan}")
        self.execute.action(persona, maze, retrieved, plan, all_news)
        L.debug(f"{persona.name} Execute end, Reflect begin")
        self.reflect.action(persona)
        L.debug(f"{persona.name} Reflect end")

        return
