import sys, random, math
import constants

class Faction:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.home_base_x = random.randint(0, constants.world_width)
        self.home_base_y = random.randint(0, constants.world_height)
        self.leader = None

    @staticmethod
    def generate_random_faction_name():
        syllables = ["ka", "zu", "mi", "ra", "ta", "lo", "na", "fi", "vo", "gu"]
        name = "".join(random.choice(syllables) for _ in range(random.randint(2, 4)))
        return name.capitalize()

    @staticmethod
    def generate_random_faction_color():
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r, g, b)
    
    @staticmethod
    def create_new_faction():
        faction = Faction(Faction.generate_random_faction_name(), Faction.generate_random_faction_color())
        return faction