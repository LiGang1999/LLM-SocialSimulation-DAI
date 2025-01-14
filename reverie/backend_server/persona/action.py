import sys

from persona.cognitive_modules.converse import *
from persona.cognitive_modules.execute import *
from persona.cognitive_modules.perceive import *
from persona.cognitive_modules.plan import *
from persona.cognitive_modules.reflect import *
from persona.cognitive_modules.retrieve import *


class Action:
    def __init__(self):
        pass

    def action(self):
        pass


class GaPerceive(Action):
    def __init__(self):
        pass

    def action(self, persona, maze):
        return perceive(persona, maze)


class GaRetrieve(Action):
    def __init__(self):
        pass

    def action(self, persona, perceived):
        return retrieve(persona, perceived)


class GaPlan(Action):
    def __init__(self):
        pass

    def action(self, persona, maze, personas, new_day, retrieved):
        return plan(persona, maze, personas, new_day, retrieved)


class GaExecute(Action):
    def __init__(self):
        pass

    def action(self, persona, maze, personas, plan):
        return execute(persona, maze, personas, plan)


class GaReflect(Action):
    def __init__(self):
        pass

    def action(self, persona):
        reflect(persona)


class DaiPerceive(Action):
    def __init__(self):
        pass

    def action(self, persona, maze):
        return perceive_dai(persona, maze)


class DaiRetrieve(Action):
    def __init__(self):
        pass

    def action(self, persona, perceived):
        return retrieve_dai_custom(persona, perceived)


class DaiPlan(Action):
    def __init__(self):
        pass

    def action(self, persona, retrieved):
        return plan_dai_custom(persona, retrieved)


class DaiExecute(Action):
    def __init__(self):
        pass

    def action(self, persona, maze, retrieved, plan):
        return execute_dai_custom(persona, maze, retrieved, plan)


class DaiReflect(Action):
    def __init__(self):
        pass

    def action(self, persona):
        reflect_dai(persona)
