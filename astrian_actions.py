import pygame
import sys
import math
import random
import names
from astrian import Astrian
import constants

standard_velocity = 0.1

def are_colliding(circle_a, circle_b):
    distance = math.sqrt((circle_a.x - circle_b.x) ** 2 + (circle_a.y - circle_b.y) ** 2)
    colliding = distance < (circle_a.radius + circle_b.radius)
    if not colliding and circle_b.name in circle_a.colliding_actors:
        #print(f"{circle_a.name} stops colliding with {circle_b.name}")
        circle_a.colliding_actors.remove(circle_b.name)
    return colliding

def factions_match(circle_a, circle_b):
    return circle_a.faction == circle_b.faction

def roll_friendship():
    return random.random() < 0.5

def attempt_subjugate():
    return random.random() < 0.4

def random_circle(circle_a, circle_b):
    return circle_a if random.random() < 0.5 else circle_b

def subjugate(circle_a, circle_b):
    print(f"{circle_a.name} subjugates {circle_b.name}")
    circle_b.faction = circle_a.faction
    circle_b.color = circle_a.color

def attack(circle_a, circle_b):
    #print(f"{circle_a.name} attacks {circle_b.name}")
    attacker = circle_a if roll_friendship() else circle_b
    defender = circle_b if attacker == circle_a else circle_a
    defender.health -= 100
    if defender.health <= 0:
        print(f"{defender.name}  killed by {attacker.name}")
        defender.is_dead = True
        attacker.health += 10
        attacker.kill_count += 1
    # if (attacker.health <= 0):
    #     print(f"{attacker.name} killed by {defender.name}")
    #     attacker.is_dead = True
    #     defender.health += 100
    #     defender.kill_count += 1
        
def mating_cooldown(circle_a, circle_b):
    return circle_a.mating_cooldown > 0 or circle_b.mating_cooldown > 0

def roll_mating():
    return random.random() < 0.5

def mate(circle_a, circle_b):
    print(f"{circle_a.name} mates with {circle_b.name}")
    if circle_a.faction == circle_b.faction:
        child_faction = circle_a.faction
    else:
        child_faction = constants.factions[random.randint(0, 2)]
    circle_b.gestation_countdown = 2000
    circle_b.mate_astrian = circle_a
    circle_a.mating_cooldown = 3000
    circle_b.mating_cooldown = 3000

def is_with_child(astrian):
    return astrian.gestation_countdown > 0

def birth_child(game_world, astrian):
    child = Astrian(astrian.x, astrian.y, 10, astrian.color, standard_velocity, standard_velocity, astrian.faction)
    game_world.astrians.append(child)
    astrian.child_count += 1
    astrian.mate_astrian.child_count += 1
    astrian.gestation_countdown = 0
    astrian.mate_astrian = None
    print(f"{astrian.name} gives birth to {child.name}")

def handle_collision(circle_a, circle_b):
    if (circle_b.name not in circle_a.colliding_actors and circle_a.name not in circle_b.colliding_actors):
        #print(f"{circle_a.name} starts collides with {circle_b.name}")
        circle_a.colliding_actors.append(circle_b.name)
        circle_b.colliding_actors.append(circle_a.name)
        if not factions_match(circle_a, circle_b):
            first_circle = random_circle(circle_a, circle_b)
            if attempt_subjugate():
                subjugate(circle_a, circle_b)
            else:
                attack(circle_a, circle_b)
        else:
            if not mating_cooldown(circle_a, circle_b):
                if roll_mating():
                    if not mating_cooldown(circle_a, circle_b):
                        mate(circle_a, circle_b)
    else:
        # print(f"{circle_a.name} is already colliding with {circle_b.name}")
        # print(f"{circle_a.colliding_actors}")
        # print(f"{circle_b.colliding_actors}")
        pass