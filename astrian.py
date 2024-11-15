
import pygame
import sys
import math
import random
import names
import constants
from enum import Enum
from faction import Faction, City

max_health = 150

class Astrian:
    def __init__(self, x, y, radius, color, velocity_x, velocity_y, faction=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.faction = faction
        self.health = 100
        self.name = names.get_full_name()
        self.is_dead = False
        self.has_target = False
        self.direction_change_counter = 0
        self.mating_cooldown = 0
        self.gestation_countdown = 0
        self.remove_collision_block_countdown = 0
        self.mate_astrian = None
        self.kill_count = 0
        self.child_count = 0
        self.current_action = None
        self.colliding_actors = []
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        self.resources = 0
        
        if (self.faction.leader == None):
            self.faction.leader = self

    def move(self, game_world):
        if self.current_action:
            self.current_action.perform()
            if self.current_action.evaluate_complete():
                if (self.current_action.name == "SeekFoeObjective"):
                    self.current_action = RandomMovementObjective(self, game_world, 200) # Since we reach the target go somewhere random so we can trigger the attack again 
                elif (self.current_action.name == "SeekMateObjective"):
                    self.current_action = RandomMovementObjective(self, game_world, 500) # Since we reach the target go somewhere random so we can trigger the attack again 
                else:
                    self.current_action = None
        else:
            # Select a new objective if none is active
            faction_count = game_world.get_faction_counts().get(self.faction.name, 0)
            if faction_count == 1:  # Trigger SeekFoeObjective if faction has only 1 member left
                self.current_action = SeekFoeObjective(self, game_world)
            elif faction_count < 3 and self.is_leader():  # Trigger ResettleObjective if faction has less than 3 members and is leader
                self.current_action = ResettleObjective(self, game_world)
            elif self.is_leader() and any(city.resources >= constants.city_resource_cost for city in self.faction.cities):  # Trigger SettleNewCityObjective if any city has more than 50 resources
                self.current_action = SettleNewCityObjective(self, game_world)
            else:
                rand = random.random()
                # Select a new action if none is active
                if rand > 0.85:  # 10% chance to claim an empty faction
                    self.current_action = ClaimEmptyFactionObjective(self, game_world)
                elif rand > 0.70:  # 50% chance to move to home base
                    self.current_action = MoveToHomeBaseObjective(self, game_world)
                elif rand > 0.30:
                    self.current_action = SeekMateObjective(self, game_world)
                elif rand > 0.02:
                    self.current_action = RandomMovementObjective(self, game_world, 250)
                else:
                    if (faction_count > 20):
                        self.current_action = BranchOffObjective(self, game_world)                    
                    else:
                        self.current_action = RandomMovementObjective(self, game_world, 250)
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def is_leader(self):
        # Assuming the leader is the first Astrian in the faction
        return self.faction and self.faction.leader == self

    def kill(self):
        self.is_dead = True

    def draw(self, surface, camera_x, camera_y, zoom):
        pygame.draw.circle(surface, self.color, (int((self.x - camera_x) * zoom), int((self.y - camera_y) * zoom)), int(self.radius * zoom))

    def draw_highlight(self, surface, camera_x, camera_y, zoom):
        pygame.draw.circle(surface, (255, 255, 0), (int((self.x - camera_x) * zoom), int((self.y - camera_y) * zoom)), int(self.radius * zoom) + 5, 3)

class Objective:
    def __init__(self, astrian, game_world):
        self.name = "Objective" 
        self.astrian = astrian
        self.game_world = game_world

    def perform(self):
        raise NotImplementedError("Subclasses must implement this method")

    def evaluate_complete(self):
        raise NotImplementedError("Subclasses must implement this method")
    
class MoveToHomeBaseObjective(Objective):
    def __init__(self, astrian, game_world):
        super().__init__(astrian, game_world)
        self.city = self._find_nearest_home_base()
        self.name = "MoveToHomeBaseObjective"

    def _find_nearest_home_base(self):
        nearest_city_x = None
        nearest_city_y = None
        nearest_city = None
        min_distance = float('inf')
        for faction in self.game_world.factions:
            if faction.name == self.astrian.faction.name:
                for city in faction.cities:
                    base_x = city.x
                    base_y = city.y
                    distance = math.sqrt((self.astrian.x - base_x) ** 2 + (self.astrian.y - base_y) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_city_x = base_x
                        nearest_city_y = base_y
                        nearest_city = city
        return nearest_city

    def perform(self):
        direction_x = self.city.x - self.astrian.x
        direction_y = self.city.y - self.astrian.y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance > 0:
            self.astrian.velocity_x = (direction_x / distance) * .3  # Constant speed
            self.astrian.velocity_y = (direction_y / distance) * .3
        self.astrian.x += self.astrian.velocity_x
        self.astrian.y += self.astrian.velocity_y

    def evaluate_complete(self):
        distance = math.sqrt((self.astrian.x - self.city.x) ** 2 + (self.astrian.y - self.city.y) ** 2)
        completed = distance < self.astrian.radius
        if (completed):
            if (self.astrian.health < max_health):
                self.city.resources += self.astrian.resources
                self.astrian.health += 2
                self.astrian.resources = 0
        return completed
    
class RandomMovementObjective(Objective):
    def __init__(self, astrian, game_world, radius):
        super().__init__(astrian, game_world)
        self.radius = radius
        self.world_width = constants.world_width
        self.world_height = constants.world_height
        self.target_x, self.target_y = self._choose_random_point()
        self.name = "RandomMovementObjective"

    def _choose_random_point(self):
        while True:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.radius)
            target_x = self.astrian.x + distance * math.cos(angle)
            target_y = self.astrian.y + distance * math.sin(angle)
            if 0 <= target_x <= self.world_width and 0 <= target_y <= self.world_height:
                return target_x, target_y

    def perform(self):
        direction_x = self.target_x - self.astrian.x
        direction_y = self.target_y - self.astrian.y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance > 0:
            self.astrian.velocity_x = (direction_x / distance) * .3  # Constant speed
            self.astrian.velocity_y = (direction_y / distance) * .3
        self.astrian.x += self.astrian.velocity_x
        self.astrian.y += self.astrian.velocity_y

        # Ensure the Astrian stays within bounds
        if self.astrian.x > self.world_width:
            self.astrian.x = self.world_width
            self.astrian.velocity_x *= -1
        elif self.astrian.x < 0:
            self.astrian.x = 0
            self.astrian.velocity_x *= -1

        if self.astrian.y > self.world_height:
            self.astrian.y = self.world_height
            self.astrian.velocity_y *= -1
        elif self.astrian.y < 0:
            self.astrian.y = 0
            self.astrian.velocity_y *= -1

    def evaluate_complete(self):
        distance = math.sqrt((self.astrian.x - self.target_x) ** 2 + (self.astrian.y - self.target_y) ** 2)
        completed = distance < self.astrian.radius
        if (completed):
            self.astrian.resources += 1
        return completed
    
class BranchOffObjective(Objective):
    def __init__(self, astrian, game_world):
        super().__init__(astrian, game_world)
        self.world_width = constants.world_width
        self.world_height = constants.world_height
        self.target_x, self.target_y = self._choose_random_point()
        self.name = "BranchOffObjective"

    def _choose_random_point(self):
        while True:
            target_x = random.uniform(0, self.world_width)
            target_y = random.uniform(0, self.world_height)
            if 0 <= target_x <= self.world_width and 0 <= target_y <= self.world_height:
                return target_x, target_y

    def perform(self):
        direction_x = self.target_x - self.astrian.x
        direction_y = self.target_y - self.astrian.y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance > 0:
            self.astrian.velocity_x = (direction_x / distance) * 1  # Constant speed
            self.astrian.velocity_y = (direction_y / distance) * 1
        self.astrian.x += self.astrian.velocity_x
        self.astrian.y += self.astrian.velocity_y

        # Ensure the Astrian stays within bounds
        if self.astrian.x > self.world_width:
            self.astrian.x = self.world_width
            self.astrian.velocity_x *= -1
        elif self.astrian.x < 0:
            self.astrian.x = 0
            self.astrian.velocity_x *= -1

        if self.astrian.y > self.world_height:
            self.astrian.y = self.world_height
            self.astrian.velocity_y *= -1
        elif self.astrian.y < 0:
            self.astrian.y = 0
            self.astrian.velocity_y *= -1

    def evaluate_complete(self):
        distance = math.sqrt((self.astrian.x - self.target_x) ** 2 + (self.astrian.y - self.target_y) ** 2)
        if distance < self.astrian.radius:
            self._start_new_faction()
            return True
        return False

    def _start_new_faction(self):
        new_faction = Faction.create_new_faction()
        self.game_world.factions.append(new_faction)
        self.astrian.faction = new_faction
        self.astrian.color = new_faction.color

class SeekMateObjective(Objective):
    def __init__(self, astrian, game_world):
        super().__init__(astrian, game_world)
        self.target_astrian = self._find_nearest_faction_member()
        self.name = "SeekMateObjective"

    def _find_nearest_faction_member(self):
        nearest_astrian = None
        min_distance = float('inf')
        for other_astrian in self.game_world.astrians:
            if other_astrian != self.astrian and other_astrian.faction == self.astrian.faction:
                distance = math.sqrt((self.astrian.x - other_astrian.x) ** 2 + (self.astrian.y - other_astrian.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_astrian = other_astrian
        return nearest_astrian

    def perform(self):
        if self.target_astrian:
            direction_x = self.target_astrian.x - self.astrian.x
            direction_y = self.target_astrian.y - self.astrian.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if distance > 0:
                self.astrian.velocity_x = (direction_x / distance) * 1  # Constant speed
                self.astrian.velocity_y = (direction_y / distance) * 1
            self.astrian.x += self.astrian.velocity_x
            self.astrian.y += self.astrian.velocity_y

            # Ensure the Astrian stays within bounds
            if self.astrian.x > self.game_world.width:
                self.astrian.x = self.game_world.width
                self.astrian.velocity_x *= -1
            elif self.astrian.x < 0:
                self.astrian.x = 0
                self.astrian.velocity_x *= -1

            if self.astrian.y > self.game_world.height:
                self.astrian.y = self.game_world.height
                self.astrian.velocity_y *= -1
            elif self.astrian.y < 0:
                self.astrian.y = 0
                self.astrian.velocity_y *= -1

    def evaluate_complete(self):
        if self.target_astrian:
            distance = math.sqrt((self.astrian.x - self.target_astrian.x) ** 2 + (self.astrian.y - self.target_astrian.y) ** 2)
            return distance < self.astrian.radius
        return True
    
class SeekFoeObjective(Objective):
    def __init__(self, astrian, game_world):
        super().__init__(astrian, game_world)
        self.target_astrian = self._find_nearest_enemy_member()
        self.name = "SeekFoeObjective"

    def _find_nearest_enemy_member(self):
        nearest_astrian = None
        min_distance = float('inf')
        for other_astrian in self.game_world.astrians:
            if other_astrian.name != self.astrian.name and other_astrian.faction.name != self.astrian.faction.name:
                distance = math.sqrt((self.astrian.x - other_astrian.x) ** 2 + (self.astrian.y - other_astrian.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_astrian = other_astrian
        return nearest_astrian

    def perform(self):
        if self.target_astrian:
            direction_x = self.target_astrian.x - self.astrian.x
            direction_y = self.target_astrian.y - self.astrian.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if distance > 0:
                self.astrian.velocity_x = (direction_x / distance) * 1  # Constant speed
                self.astrian.velocity_y = (direction_y / distance) * 1
            self.astrian.x += self.astrian.velocity_x
            self.astrian.y += self.astrian.velocity_y

            # Ensure the Astrian stays within bounds
            if self.astrian.x > self.game_world.width:
                self.astrian.x = self.game_world.width
                self.astrian.velocity_x *= -1
            elif self.astrian.x < 0:
                self.astrian.x = 0
                self.astrian.velocity_x *= -1

            if self.astrian.y > self.game_world.height:
                self.astrian.y = self.game_world.height
                self.astrian.velocity_y *= -1
            elif self.astrian.y < 0:
                self.astrian.y = 0
                self.astrian.velocity_y *= -1

    def evaluate_complete(self):
        if self.target_astrian:
            distance = math.sqrt((self.astrian.x - self.target_astrian.x) ** 2 + (self.astrian.y - self.target_astrian.y) ** 2)
            if (distance < self.astrian.radius):
                print(f"{self.astrian.name} attacking {self.target_astrian.name}")
            return distance < self.astrian.radius
        return True
    

class ResettleObjective(Objective):
    def __init__(self, astrian, game_world):
        super().__init__(astrian, game_world)
        self.target_x, self.target_y = self._find_new_home_base_location()
        self.name = "ResettleObjective"

    def _find_new_home_base_location(self):
        counter = 0
        while True:
            counter += 1
            target_x = random.uniform(0, self.game_world.width)
            target_y = random.uniform(0, self.game_world.height)
            if self._is_location_valid(target_x, target_y):
                return target_x, target_y
            if counter > 100:
                return target_x, target_y

    def _is_location_valid(self, x, y):
        for faction in self.game_world.factions:
            for city in faction.cities:
                distance = math.sqrt((x - city.x) ** 2 + (y - city.y) ** 2)
                if distance < 200:
                    return False
        return True

    def perform(self):
        direction_x = self.target_x - self.astrian.x
        direction_y = self.target_y - self.astrian.y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance > 0:
            self.astrian.velocity_x = (direction_x / distance) * 1  # Constant speed
            self.astrian.velocity_y = (direction_y / distance) * 1
        self.astrian.x += self.astrian.velocity_x
        self.astrian.y += self.astrian.velocity_y

        # Ensure the Astrian stays within bounds
        if self.astrian.x > self.game_world.width:
            self.astrian.x = self.game_world.width
            self.astrian.velocity_x *= -1
        elif self.astrian.x < 0:
            self.astrian.x = 0
            self.astrian.velocity_x *= -1

        if self.astrian.y > self.game_world.height:
            self.astrian.y = self.game_world.height
            self.astrian.velocity_y *= -1
        elif self.astrian.y < 0:
            self.astrian.y = 0
            self.astrian.velocity_y *= -1

    def evaluate_complete(self):
        distance = math.sqrt((self.astrian.x - self.target_x) ** 2 + (self.astrian.y - self.target_y) ** 2)
        if distance < self.astrian.radius:
            self._resettle_home_base()
            return True
        return False

    def _resettle_home_base(self):
        self.astrian.faction.home_base_x = self.target_x
        self.astrian.faction.home_base_y = self.target_y


class ClaimEmptyFactionObjective(Objective):
    def __init__(self, astrian, game_world):
        super().__init__(astrian, game_world)
        self.target_city = None
        self.target_faction, self.target_city, self.target_base_x, self.target_base_y = self._find_empty_faction()
        self.name = "ClaimEmptyFactionObjective"

    def _find_empty_faction(self):
        empty_faction = None
        target_city = None
        nearest_base_x = None
        nearest_base_y = None
        min_distance = float('inf')
        faction_counts = self.game_world.get_faction_counts()
        for faction in self.game_world.get_empty_factions():
            #if faction_counts.get(faction.name, 0) == 0:
            #print(f"{faction.name} is empty")
            #print(f"{faction_counts.get(faction.name, 0)}")
            for city in faction.cities:
                base_x = city.x
                base_y = city.y
                distance = math.sqrt((self.astrian.x - base_x) ** 2 + (self.astrian.y - base_y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    empty_faction = faction
                    target_city = city  
                    nearest_base_x = base_x
                    nearest_base_y = base_y
                    faction.cities.remove(city)
        return empty_faction, target_city, nearest_base_x, nearest_base_y

    def perform(self):
        if self.target_faction:
            direction_x = self.target_base_x - self.astrian.x
            direction_y = self.target_base_y - self.astrian.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if distance > 0:
                self.astrian.velocity_x = (direction_x / distance) * 0.3  # Constant speed
                self.astrian.velocity_y = (direction_y / distance) * 0.3
            self.astrian.x += self.astrian.velocity_x
            self.astrian.y += self.astrian.velocity_y

            # Ensure the Astrian stays within bounds
            if self.astrian.x > self.game_world.width:
                self.astrian.x = self.game_world.width
                self.astrian.velocity_x *= -1
            elif self.astrian.x < 0:
                self.astrian.x = 0
                self.astrian.velocity_x *= -1

            if self.astrian.y > self.game_world.height:
                self.astrian.y = self.game_world.height
                self.astrian.velocity_y *= -1
            elif self.astrian.y < 0:
                self.astrian.y = 0
                self.astrian.velocity_y *= -1

    def evaluate_complete(self):
        if self.target_faction:
            distance = math.sqrt((self.astrian.x - self.target_base_x) ** 2 + (self.astrian.y - self.target_base_y) ** 2)
            if distance < self.astrian.radius:
                if (random.random() < 0.50): # random chance to claim
                    self._claim_faction()
                else: # else destroy
                    if (self.target_city in self.target_faction.cities):
                        self.target_faction.cities.remove(self.target_city)
                    if (self.target_faction in self.game_world.factions):
                        self.game_world.factions.remove(self.target_faction)
                return True
            return False
        else:
            return True # If no empty factions, return True
        return True

    def _claim_faction(self):
        # if the faction count of the city is still 0, claim it
        if self.game_world.get_faction_counts().get(self.target_faction.name, 0) == 0:
            self.target_city.claim_city(self.astrian.faction)
            print(f"{self.astrian.name} claimed {self.target_faction.name}")
        else:
            pass


class SettleNewCityObjective(Objective):
    def __init__(self, astrian, game_world):
        super().__init__(astrian, game_world)
        self.target_city = self._find_city_with_resources()
        self.name = "SettleNewCityObjective"
        self.new_city_x, self.new_city_y = self._find_new_city_location()
        self.astrian_holding_resources = False

    def _find_city_with_resources(self):
        for city in self.astrian.faction.cities:
            if city.resources > 50:
                return city
        return None

    def _find_new_city_location(self):
        while True:
            x = random.randint(0, self.game_world.width)
            y = random.randint(0, self.game_world.height)
            return x, y

    def perform(self):
        if self.astrian_holding_resources:
            direction_x = self.new_city_x - self.astrian.x
            direction_y = self.new_city_y - self.astrian.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if distance > 0:
                self.astrian.velocity_x = (direction_x / distance) * 0.3
                self.astrian.velocity_y = (direction_y / distance) * 0.3
            self.astrian.x += self.astrian.velocity_x
            self.astrian.y += self.astrian.velocity_y
        elif self.target_city:
            direction_x = self.target_city.x - self.astrian.x
            direction_y = self.target_city.y - self.astrian.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if distance > 0:
                self.astrian.velocity_x = (direction_x / distance) * 0.3  # Constant speed
                self.astrian.velocity_y = (direction_y / distance) * 0.3
            self.astrian.x += self.astrian.velocity_x
            self.astrian.y += self.astrian.velocity_y
        

    def evaluate_complete(self):
        if self.astrian_holding_resources:
            distance = math.sqrt((self.astrian.x - self.new_city_x) ** 2 + (self.astrian.y - self.new_city_y) ** 2)
            if distance < self.astrian.radius:
                self._settle_new_city()
                return True
        elif self.target_city:
            distance = math.sqrt((self.astrian.x - self.target_city.x) ** 2 + (self.astrian.y - self.target_city.y) ** 2)
            if distance < self.astrian.radius:
                self.target_city.resources -= constants.city_resource_cost
                self.astrian.resources += constants.city_resource_cost
                self.astrian_holding_resources = True
        return False

    def _settle_new_city(self):
        if self.target_city:
            self.astrian.resources -= constants.city_resource_cost
            new_city = City(self.new_city_x, self.new_city_y, 50, self.astrian.faction)
            self.astrian.faction.cities.append(new_city)