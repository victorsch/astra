import pygame
import sys
import math
import random
import names
from astrian import Astrian
import constants

standard_velocity = 0.1

class AstrianHandler:
    def __init__(self, game_world):
        self.game_world = game_world

    def are_colliding(self, circle_a, circle_b):
        distance = math.sqrt((circle_a.x - circle_b.x) ** 2 + (circle_a.y - circle_b.y) ** 2)
        colliding = distance < (circle_a.radius + circle_b.radius)

        # after 2000 frames, remove the collision blocks so that collisions can be handled normally (this is to prevent a single collision from being handled an unreasonable number of times)
        if colliding:
            circle_a.remove_collision_block_countdown = 2000
            circle_b.remove_collision_block_countdown = 2000
        return colliding

    def factions_match(self, circle_a, circle_b):
        return circle_a.faction == circle_b.faction

    def roll_friendship(self):
        return random.random() < 0.5
    
    def attempt_subjugate(self, attacker):
        if (self.game_world.get_faction_count_by_name(attacker.faction.name) < 5):
            return random.random() < 0.6
        return random.random() < 0.3

    def random_circle(self, circle_a, circle_b):
        return circle_a if random.random() < 0.5 else circle_b

    def subjugate(self, circle_a, circle_b):
        print(f"{circle_a.name} subjugates {circle_b.name}")
        circle_b.faction = circle_a.faction
        circle_b.color = circle_a.color

        for faction in self.game_world.factions:
            if faction.leader != None and circle_b.name == faction.leader.name:
                faction.leader = None

    def attack(self, circle_a, circle_b):
        print(f"{circle_a.name} attacks {circle_b.name}")
        attacker = circle_a if self.roll_friendship() else circle_b
        defender = circle_b if attacker == circle_a else circle_a
        defender.health -= 125
        attacker.health -= 5
        if defender.health <= 0:
            print(f"{defender.name} killed by {attacker.name}")
            defender.is_dead = True
            attacker.kill_count += 1
            for faction in self.game_world.factions:
                if faction.leader != None and defender.name == faction.leader.name:
                    faction.leader = None
        if (attacker.health <= 0):
            print(f"{attacker.name} killed by {defender.name}")
            attacker.is_dead = True
            defender.kill_count += 1
            for faction in self.game_world.factions:
                if faction.leader != None and attacker.name == faction.leader.name:
                    faction.leader = None
            
    def mating_cooldown(self, circle_a, circle_b):
        return circle_a.mating_cooldown > 0 or circle_b.mating_cooldown > 0

    def roll_mating(self):
        return random.random() < 0.5

    def mate(self, circle_a, circle_b):
        print(f"{circle_a.name} mates with {circle_b.name}")
        if circle_a.faction == circle_b.faction:
            child_faction = circle_a.faction
        else:
            child_faction = constants.factions[random.randint(0, 2)]
        circle_b.gestation_countdown = 2000
        circle_b.mate_astrian = circle_a
        circle_a.mating_cooldown = 3000
        circle_b.mating_cooldown = 3000

    def is_with_child(self, astrian):
        return astrian.gestation_countdown > 0

    def birth_child(self, game_world, astrian):
        if (len(game_world.astrians) < 9999):
            child = Astrian(astrian.x, astrian.y, 10, astrian.color, standard_velocity, standard_velocity, astrian.faction)
            game_world.astrians.append(child)
            astrian.child_count += 1
            astrian.mate_astrian.child_count += 1
            astrian.gestation_countdown = 0
            astrian.mate_astrian = None
            print(f"{astrian.name} gives birth to {child.name}")
        else:
            astrian.gestation_countdown = 0
            astrian.mate_astrian = None

    def handle_collision(self, circle_a, circle_b):
        if (circle_b.name not in circle_a.colliding_actors and circle_a.name not in circle_b.colliding_actors):
            circle_a.colliding_actors.append(circle_b.name)
            circle_b.colliding_actors.append(circle_a.name)
            if not self.factions_match(circle_a, circle_b):
                first_circle = self.random_circle(circle_a, circle_b)
                if self.attempt_subjugate(first_circle):
                    self.subjugate(circle_a, circle_b)
                else:
                    self.attack(circle_a, circle_b)
            else:
                if not self.mating_cooldown(circle_a, circle_b):
                    if self.roll_mating():
                        if not self.mating_cooldown(circle_a, circle_b):
                            self.mate(circle_a, circle_b)
        else:
            pass