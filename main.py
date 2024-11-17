import pygame
import sys
import math
import random
import names
from astrian import Astrian
from gameworld import GameWorld
from ui import UIManager
import constants

# Initialize Pygame
pygame.init()

# Set up the display

screen = pygame.display.set_mode((constants.screen_width, constants.screen_height + constants.ui_height))
pygame.display.set_caption('Astra')

# Initialize font
pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

# Selected Astrian for detailed stats
selected_astrian = None

game_world = GameWorld(constants.world_width, constants.world_height, screen, [])
game_world.setup_world()

def render_astrians_tab(ui_surface, y_offset, line_height, mouse_pos=None):
    for i, astrian in enumerate(game_world.astrians):
        text_surface = font.render(f"{astrian.name}: Health={astrian.health}, Age={astrian.get_age()}, Faction={astrian.faction.name}, Kills={astrian.kill_count}, Children={astrian.child_count}", True, constants.black_color)
        ui_surface.blit(text_surface, (10, y_offset + i * line_height))
        text_rect = pygame.Rect(10, constants.screen_height + y_offset + i * line_height, 780, line_height)
        if mouse_pos and text_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                ui_manager.list_item_clicked = True
                ui_manager.selected_astrian = astrian
                ui_manager.selected_city = None
                ui_manager.selected_faction = None
            else:
                ui_manager.list_item_clicked = False
        else:
            ui_manager.list_item_clicked = False

def render_factions_tab(ui_surface, y_offset, line_height, mouse_pos=None):
    factions = game_world.factions
    # factions where astrian population is not 0
    factions = [faction for faction in factions if game_world.get_faction_count_by_name(faction.name) > 0]
    for i, faction in enumerate(factions):
        text_surface = font.render(f"{faction.name}: Leader={faction.leader.name if faction.leader else 'None'}, Members={game_world.get_faction_counts().get(faction.name, 0)}", True, constants.black_color)
        ui_surface.blit(text_surface, (10, y_offset + i * line_height))
        text_rect = pygame.Rect(10, constants.screen_height + y_offset + i * line_height, 780, line_height)
        if mouse_pos and text_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                ui_manager.list_item_clicked = True
                ui_manager.selected_faction = faction
                ui_manager.selected_city = None
                ui_manager.selected_astrian = None
            else:
                ui_manager.list_item_clicked = False
        else:
            ui_manager.list_item_clicked = False

def render_cities_tab(ui_surface, y_offset, line_height, mouse_pos=None):
    for i, faction in enumerate(game_world.factions):
        for j, city in enumerate(faction.cities):
            text_surface = font.render(f"{city.name}: Faction={city.faction.name}, Resources={city.resources}", True, constants.black_color)
            ui_surface.blit(text_surface, (10, y_offset + (i + j) * line_height))
            text_rect = pygame.Rect(10, constants.screen_height + y_offset + (i + j) * line_height, 780, line_height)
            if mouse_pos and text_rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    ui_manager.list_item_clicked = True
                    ui_manager.selected_city = city
                    ui_manager.selected_faction = None
                    ui_manager.selected_astrian = None
                else:
                    ui_manager.list_item_clicked = False
            else:
                ui_manager.list_item_clicked = False

ui_manager = UIManager(game_world)
ui_manager.add_tab("Astrians", render_astrians_tab)
ui_manager.add_tab("Factions", render_factions_tab)
ui_manager.add_tab("Cities", render_cities_tab)

factions = [
    'red',
    'white',
    'green'
]



# Main game loop
while True:
    ui_manager.handle_input()

    game_world.screen.fill(constants.black_color)

    game_world.handle_frame()

    # Render the UI
    #ui_manager.render_ui(screen, game_world.astrians, selected_astrian)
    ui_manager.render_ui(screen)

    # Display city details if hovering over a city
    if game_world.hovered_city:
        city = game_world.hovered_city
        faction = city.faction
        city_details = [
            f"City: {city.name}",
            f"Faction: {faction.name}",
            f"Age: {city.get_age()} years",
            f"Color: {faction.color}",
            f"Leader: {faction.leader.name if faction.leader else 'None'}",
            f"Members: {game_world.get_faction_counts().get(faction.name, 0)}",
            f"Resources: {city.resources}"
        ]
        for i, detail in enumerate(city_details):
            text_surface = font.render(detail, True, constants.white_color)
            screen.blit(text_surface, (10, 10 + i * 20))

    # highlighted astrian overlay
    if ui_manager.selected_astrian:
        ui_manager.selected_astrian.draw_highlight(screen, game_world.camera_x, game_world.camera_y, game_world.zoom)

    # highlighted faction overlay
    if ui_manager.selected_faction:
        for city in ui_manager.selected_faction.cities:
            city.draw_highlight(screen, game_world.camera_x, game_world.camera_y, game_world.zoom)
        for astrian in game_world.get_astrians_by_faction_name(ui_manager.selected_faction.name):
            astrian.draw_highlight(screen, game_world.camera_x, game_world.camera_y, game_world.zoom)

    if (ui_manager.selected_city):
        ui_manager.selected_city.draw_highlight(screen, game_world.camera_x, game_world.camera_y, game_world.zoom)

    # Update the display
    pygame.display.flip()

