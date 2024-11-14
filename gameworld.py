import sys, random, math, string
import constants
from astrian import Astrian
import astrian_actions
from faction import Faction

class GameWorld:
    def __init__(self, width, height, screen, astrians=[]):
        self.width = width
        self.height = height
        self.astrians = astrians
        self.screen = screen
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        self.factions = []

    def handle_frame(self):
        for i in range(len(self.astrians)):
            for j in range(i + 1, len(self.astrians)):
                if astrian_actions.are_colliding(self.astrians[i], self.astrians[j]):
                    astrian_actions.handle_collision(self.astrians[i], self.astrians[j])      
        for astrian in self.astrians:
            if not astrian.is_dead:
                self.handle_astrian_frame(astrian)
                astrian.move(self)
                astrian.draw(self.screen, self.camera_x, self.camera_y, self.zoom)
            else:
                if (astrian.faction.leader is not None and astrian.faction.leader.name == astrian.name):
                    astrian.faction.leader = None
                    # pick a new leader if any are possible
                    for other_astrian in self.astrians:
                        if (other_astrian.faction.name == astrian.faction.name and not other_astrian.is_dead):
                            astrian.faction.leader = other_astrian
                            break
                self.astrians.remove(astrian)

    def handle_astrian_frame(self, astrian):
        if (astrian.mating_cooldown > 0):
            astrian.mating_cooldown -= 1
        if astrian_actions.is_with_child(astrian):
                astrian.gestation_countdown -= 1
                if astrian.gestation_countdown <= 0:
                    astrian_actions.birth_child(self, astrian)

    def generate_random_faction_name(self):
        syllables = ["ka", "zu", "mi", "ra", "ta", "lo", "na", "fi", "vo", "gu"]
        name = "".join(random.choice(syllables) for _ in range(random.randint(2, 4)))
        return name.capitalize()

    def generate_random_faction_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r, g, b)
    
    def setup_world(self):
        for i in range(2):
            faction = Faction.create_new_faction()
            self.factions.append(faction)
            for j in range(4):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                radius = 10
                color = faction.color
                velocity_x = random.uniform(-1, 1)
                velocity_y = random.uniform(-1, 1)
                astrian = Astrian(x, y, radius, color, velocity_x, velocity_y, faction)
                self.astrians.append(astrian)
    
    def get_faction_counts(self):
        faction_counts = {}
        for faction in self.factions:
            faction_counts[faction.name] = 0
        for astrian in self.astrians:
            faction_counts[astrian.faction.name] += 1
        # return factions greater than 0
        return {k: v for k, v in faction_counts.items() if v > 0}