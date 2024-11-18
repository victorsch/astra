import sys, random, math, pygame
import constants
import time

class Faction:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.founding_time = time.time()
        self.home_base_x = random.randint(0, constants.world_width)
        self.home_base_y = random.randint(0, constants.world_height)
        self.leader = None
        self.cities = []
        self.cities.append(City(random.randint(0, constants.world_width), random.randint(0, constants.world_height), 50, self))

    @staticmethod
    def generate_random_faction_name():
        syllables = ["ka", "zu", "mi", "ra", "ta", "lo", "na", "fi", "vo", "gu"]
        name = "".join(random.choice(syllables) for _ in range(random.randint(2, 4)))
        return name.capitalize()
    
    def generate_random_city_name():
        syllables = ["ka", "zu", "mi", "ra", "ta", "lo", "na", "fi", "vo", "gu"]
        name = "".join(random.choice(syllables) for _ in range(random.randint(3, 7)))
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
    
    def get_age(self):
        seconds_time = time.time() - self.founding_time
        years = int(seconds_time / constants.year_length)
        return years
    
    def draw(self, surface, camera_x, camera_y, zoom):
        for city in self.cities:
            city.draw(surface, camera_x, camera_y, zoom)
    
class City:
    def __init__(self, x, y, size, faction):
        self.x = x
        self.y = y
        self.founding_time = time.time()
        self.name = Faction.generate_random_city_name()
        self.size = size
        self.faction = faction
        self.resources = 0

    def draw(self, surface, camera_x, camera_y, zoom):
        pygame.draw.rect(
            surface,
            self.faction.color,
            (
                int((self.x - camera_x) * zoom) - self.size // 2,
                int((self.y - camera_y) * zoom) - self.size // 2,
                int(self.size * zoom),
                int(self.size * zoom)
            )
        )

    def draw_highlight(self, surface, camera_x, camera_y, zoom):
        pygame.draw.rect(
            surface,
            (255, 255, 0),
            (
                int((self.x - camera_x) * zoom) - self.size // 2 - 5,
                int((self.y - camera_y) * zoom) - self.size // 2 - 5,
                int(self.size * zoom) + 10,
                int(self.size * zoom) + 10
            ),
            3
        )

    def claim_city(self, faction):
        if self.faction:
            if (self in self.faction.cities):
                self.faction.cities.remove(self)
        self.faction = faction
        faction.cities.append(self)

    def is_hovered(self, mouse_pos, camera_x, camera_y, zoom):
        rect = pygame.Rect(
            int((self.x - camera_x) * zoom) - self.size // 2,
            int((self.y - camera_y) * zoom) - self.size // 2,
            int(self.size * zoom),
            int(self.size * zoom)
        )
        return rect.collidepoint(mouse_pos)
    
    def get_age(self):
        seconds_time = time.time() - self.founding_time
        years = int(seconds_time / constants.year_length)
        return years
    
    def get_distance(self, astrian):
        direction_x = self.x - astrian.x
        direction_y = self.y - astrian.y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        return distance