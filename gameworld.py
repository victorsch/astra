import sys, random, math, string, pygame, time
import constants
from astrian import Astrian
from faction import Faction
from astrian_actions import AstrianHandler

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
        self.start_time = time.time()
        self.quadtree = Quadtree(0, pygame.Rect(0, 0, width, height))
        self.hovered_city = None
        self.astrian_handler = AstrianHandler(self)

    def get_world_age(self):
        return time.time() - self.start_time

    def handle_frame(self):
        self.quadtree.clear()
        for astrian in self.astrians:
            self.quadtree.insert(astrian)

        self.draw_cities()
        self.handle_dead_faction_leaders()
        # for i in range(len(self.astrians)):
        #     for j in range(i + 1, len(self.astrians)):
        #         if astrian_actions.are_colliding(self.astrians[i], self.astrians[j]):
        #             astrian_actions.handle_collision(self.astrians[i], self.astrians[j])      
        for astrian in self.astrians:
            astrian.check_age()
            if not astrian.is_dead:
                self.handle_astrian_frame(astrian)
                astrian.move(self)
                astrian.draw(self.screen, self.camera_x, self.camera_y, self.zoom)
                possible_collisions = []
                self.quadtree.retrieve(possible_collisions, astrian.rect)
                for other in possible_collisions:
                    if other != astrian and self.astrian_handler.are_colliding(astrian, other):
                        self.astrian_handler.handle_collision(astrian, other)
            else:
                # if (astrian.faction.leader is not None and astrian.faction.leader.name == astrian.name):
                #     print(f"LEADER DIED: {astrian.name}")
                #     astrian.faction.leader = None
                #     # pick a new leader if any are possible
                #     for other_astrian in self.astrians:
                #         if (other_astrian.faction.name == astrian.faction.name and not other_astrian.is_dead):
                #             print(f"NEW LEADER: {other_astrian.name}")
                #             astrian.faction.leader = other_astrian
                #             break
                self.astrians.remove(astrian)

    def handle_astrian_frame(self, astrian):
        if (astrian.mating_cooldown > 0):
            astrian.mating_cooldown -= 1
        if self.astrian_handler.is_with_child(astrian):
                astrian.gestation_countdown -= 1
                if astrian.gestation_countdown <= 0:
                    self.astrian_handler.birth_child(self, astrian)
        if (astrian.remove_collision_block_countdown > 0):
            astrian.remove_collision_block_countdown -= 1
            if (astrian.remove_collision_block_countdown > 5):
                astrian.colliding_actors = []
            
    def handle_dead_faction_leaders(self):
        for faction in self.factions:
            if (faction.leader is None or faction.leader.is_dead):
                for astrian in self.astrians:
                    if (astrian.faction.name == faction.name and not astrian.is_dead and astrian.get_age() < 20):
                        faction.leader = astrian
                        break

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
        #return faction_counts
    
    def get_empty_factions(self): # returns a list of factions with no astrians
        empty_factions = []
        for faction in self.factions:
            has_astrian = False
            for astrian in self.astrians:
                if astrian.faction.name == faction.name:
                    has_astrian = True
                    break
            if not has_astrian:
                empty_factions.append(faction)
        return empty_factions
    
    def get_faction_by_name(self, name):
        for faction in self.factions:
            if faction.name == name:
                return faction
        return None
    
    def get_faction_count_by_name(self, name):
        count = 0
        for astrian in self.astrians:
            if astrian.faction.name == name:
                count += 1
        return count
    
    def check_faction_can_build_more_cities(self, faction):
        # there should be at least one city per 10 astrians, so if theres 7 astrians we cant build another city    
        astrian_count = 0
        for astrian in self.astrians:
            if astrian.faction.name == faction.name:
                astrian_count += 1
        city_count = 0
        for city in faction.cities:
            city_count += 1
        return astrian_count / 10 > city_count
    
    def get_astrians_by_faction_name(self, name):
        astrians = []
        for astrian in self.astrians:
            if astrian.faction.name == name:
                astrians.append(astrian)
        return astrians

    def draw_cities(self):
        for faction in self.factions:
            faction.draw(self.screen, self.camera_x, self.camera_y, self.zoom)
            
    def check_hovered_city(self, mouse_pos):
        self.hovered_city = None
        for faction in self.factions:
            for city in faction.cities:
                if city.is_hovered(mouse_pos, self.camera_x, self.camera_y, self.zoom):
                    self.hovered_city = city
                    break

class Quadtree:
    def __init__(self, level, bounds):
        self.level = level
        self.bounds = bounds
        self.objects = []
        self.nodes = []

    def clear(self):
        self.objects = []
        for node in self.nodes:
            node.clear()
        self.nodes = []

    def split(self):
        sub_width = self.bounds.width / 2
        sub_height = self.bounds.height / 2
        x = self.bounds.x
        y = self.bounds.y

        self.nodes = [
            Quadtree(self.level + 1, pygame.Rect(x + sub_width, y, sub_width, sub_height)),
            Quadtree(self.level + 1, pygame.Rect(x, y, sub_width, sub_height)),
            Quadtree(self.level + 1, pygame.Rect(x, y + sub_height, sub_width, sub_height)),
            Quadtree(self.level + 1, pygame.Rect(x + sub_width, y + sub_height, sub_width, sub_height))
        ]

    def get_index(self, rect):
        index = -1
        vertical_midpoint = self.bounds.x + (self.bounds.width / 2)
        horizontal_midpoint = self.bounds.y + (self.bounds.height / 2)

        top_quadrant = rect.y < horizontal_midpoint and rect.y + rect.height < horizontal_midpoint
        bottom_quadrant = rect.y > horizontal_midpoint

        if rect.x < vertical_midpoint and rect.x + rect.width < vertical_midpoint:
            if top_quadrant:
                index = 1
            elif bottom_quadrant:
                index = 2
        elif rect.x > vertical_midpoint:
            if top_quadrant:
                index = 0
            elif bottom_quadrant:
                index = 3

        return index

    def insert(self, obj):
        if self.nodes:
            index = self.get_index(obj.rect)
            if index != -1:
                self.nodes[index].insert(obj)
                return

        self.objects.append(obj)

        if len(self.objects) > 10 and self.level < 5:
            if not self.nodes:
                self.split()

            i = 0
            while i < len(self.objects):
                index = self.get_index(self.objects[i].rect)
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1

    def retrieve(self, return_objects, rect):
        index = self.get_index(rect)
        if index != -1 and self.nodes:
            self.nodes[index].retrieve(return_objects, rect)

        return_objects.extend(self.objects)

        return return_objects