import pygame
import sys
import math
import random
import names
from astrian import Astrian
from gameworld import GameWorld
import constants

# Initialize Pygame
pygame.init()

# Set up the display

screen = pygame.display.set_mode((constants.screen_width, constants.screen_height + constants.ui_height))
pygame.display.set_caption('Astra')

# Initialize font
pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

astrian_back_button_rect = None

# def render_ui(surface, astrians, scroll_offset, selected_astrian):
#     ui_surface = pygame.Surface((constants.screen_width, constants.ui_height))
#     ui_surface.fill(constants.grey_color)
#     y_offset = 10 - scroll_offset
#     if selected_astrian:
#         text_surface = font.render(f"Name: {selected_astrian.name}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset))
#         text_surface = font.render(f"Health: {selected_astrian.health}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 20))
#         text_surface = font.render(f"Faction: {selected_astrian.faction.name}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 40))
#         text_surface = font.render(f"Kills: {selected_astrian.kill_count}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 60))
#         text_surface = font.render(f"Children: {selected_astrian.child_count}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 80))
#         text_surface = font.render(f"Pregnant: {selected_astrian.gestation_countdown > 0}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 100))
#         text_surface = font.render(f"Gestation: {selected_astrian.gestation_countdown}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 120))
#         text_surface = font.render(f"Mating Cooldown: {selected_astrian.mating_cooldown}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 140))
#         text_surface = font.render(f"Objective: {selected_astrian.current_action.name if selected_astrian.current_action is not None else ''}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 160))
#         # colliding actors
#         text_surface = font.render(f"Colliding Actors: {[actor for actor in selected_astrian.colliding_actors]}", True, constants.black_color)
#         ui_surface.blit(text_surface, (10, y_offset + 180))
#         # Render the back button
#         back_button_rect = pygame.Rect(10, y_offset + 200, 100, 30)
#         pygame.draw.rect(ui_surface, constants.black_color, back_button_rect, 2)
#         back_text_surface = font.render("Back", True, constants.black_color)
#         ui_surface.blit(back_text_surface, (20, y_offset + 205))
#     else:
#         for i, astrian in enumerate(game_world.astrians):
#             text_surface = font.render(f"{astrian.name}: Health={astrian.health}, Faction={astrian.faction.name}, Kills={astrian.kill_count}, Children={astrian.child_count}", True, constants.black_color)
#             ui_surface.blit(text_surface, (10, y_offset + i * 20))
#         # Count the number of Astrians in each faction
#         faction_counts = game_world.get_faction_counts()
#         # for astrian in astrians:
#         #     if astrian.faction in faction_counts:
#         #         faction_counts[astrian.faction] += 1

#         # Render the faction counts on the right side of the UI
#         x_offset = constants.screen_width - 150
#         y_offset = 10
#         for faction, count in faction_counts.items():
#             text_surface = font.render(f"{faction.capitalize()}: {count}", True, constants.black_color)
#             ui_surface.blit(text_surface, (x_offset, y_offset))
#             y_offset += 20

#         # Display the world age in the bottom right corner
#         world_age = game_world.get_world_age()
#         world_age_text = font.render(f"World Age: {int(world_age)}s", True, constants.black_color)
#         ui_surface.blit(world_age_text, (constants.screen_width - 200, constants.ui_height - 30))
#     surface.blit(ui_surface, (0, constants.screen_height))


def render_ui(surface, astrians, scroll_offset, selected_astrian, game_world):
    ui_surface = pygame.Surface((constants.screen_width, constants.ui_height))
    ui_surface.fill(constants.grey_color)
    y_offset = 10 - scroll_offset
    line_height = 20

    if selected_astrian:
        fields = [
            f"Name: {selected_astrian.name}",
            f"Health: {selected_astrian.health}",
            f"Faction: {selected_astrian.faction.name}",
            f"Kills: {selected_astrian.kill_count}",
            f"Children: {selected_astrian.child_count}",
            f"Pregnant: {selected_astrian.gestation_countdown > 0}",
            f"Gestation: {selected_astrian.gestation_countdown}",
            f"Mating Cooldown: {selected_astrian.mating_cooldown}",
            f"Collision Block Countdown: {selected_astrian.remove_collision_block_countdown}",
            f"Objective: {selected_astrian.current_action.name if selected_astrian.current_action is not None else ''}",
            f"Colliding Actors: {[actor for actor in selected_astrian.colliding_actors]}"
        ]

        for i, field in enumerate(fields):
            text_surface = font.render(field, True, constants.black_color)
            ui_surface.blit(text_surface, (10, y_offset + i * line_height))

        # Render the back button
        back_button_rect = pygame.Rect(10, y_offset + len(fields) * line_height + 20, 100, 30)
        pygame.draw.rect(ui_surface, constants.black_color, back_button_rect, 2)
        back_text_surface = font.render("Back", True, constants.black_color)
        global astrian_back_button_rect
        astrian_back_button_rect = pygame.Rect(10, constants.screen_height + y_offset + len(fields) * line_height + 20, 100, 30)
        ui_surface.blit(back_text_surface, (20, y_offset + len(fields) * line_height + 25))

    else:
        for i, astrian in enumerate(game_world.astrians):
            text_surface = font.render(f"{astrian.name}: Health={astrian.health}, Faction={astrian.faction.name}, Age={astrian.get_age()}, Kills={astrian.kill_count}, Children={astrian.child_count}", True, constants.black_color)
            ui_surface.blit(text_surface, (10, y_offset + i * line_height))

        # Count the number of Astrians in each faction
        faction_counts = game_world.get_faction_counts()

        # Render the faction counts on the right side of the UI
        x_offset = constants.screen_width - 150
        y_offset = 10
        for faction, count in faction_counts.items():
            text_surface = font.render(f"{faction.capitalize()}: {count}", True, constants.black_color)
            ui_surface.blit(text_surface, (x_offset, y_offset))
            y_offset += line_height

        # Display the world age in the bottom right corner
        world_age = game_world.get_world_age()
        world_age_text = font.render(f"World Age: {int(world_age)}s", True, constants.black_color)
        ui_surface.blit(world_age_text, (constants.screen_width - 200, constants.ui_height - 30))

    surface.blit(ui_surface, (0, constants.screen_height))


def get_clicked_astrian(mouse_pos, astrians, scroll_offset):
    y_offset = 10 - scroll_offset
    for i, astrian in enumerate(game_world.astrians):
        text_rect = pygame.Rect(10, constants.screen_height + y_offset + i * 20, 780, 20)
        if text_rect.collidepoint(mouse_pos):
            return astrian
    return None

def is_back_button_clicked(mouse_pos, scroll_offset):
    y_offset = 10 - scroll_offset
    back_button_rect = pygame.Rect(10, constants.screen_height + y_offset + 200, 100, 30)
    return astrian_back_button_rect.collidepoint(mouse_pos)

# Selected Astrian for detailed stats
selected_astrian = None

game_world = GameWorld(constants.world_width, constants.world_height, screen, [])
game_world.setup_world()


# Camera position and zoom level
dragging = False
drag_start_x, drag_start_y = 0, 0

scroll_offset = 0

factions = [
    'red',
    'white',
    'green'
]

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                scroll_offset = max(0, scroll_offset - constants.scroll_speed)
            elif event.key == pygame.K_DOWN:
                scroll_offset += constants.scroll_speed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] < constants.screen_height:  # Mouse is on the game world
                if event.button == 4:  # Scroll up to zoom in
                    game_world.zoom = min(2.0, game_world.zoom + 0.1)
                elif event.button == 5:  # Scroll down to zoom out
                    game_world.zoom = max(0.2, game_world.zoom - 0.1)
                elif event.button == 1:  # Left click to start dragging
                    dragging = True
                    drag_start_x, drag_start_y = mouse_pos
            else:
                if event.button == 4:  # Scroll up
                    scroll_offset = max(0, scroll_offset - constants.scroll_speed)
                elif event.button == 5:  # Scroll down
                    total_text_height = len(game_world.astrians) * 20
                    max_scroll_offset = max(0, total_text_height - constants.ui_height + 20)
                    scroll_offset = min(max_scroll_offset, scroll_offset + constants.scroll_speed)
                elif event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if selected_astrian:
                        if is_back_button_clicked(mouse_pos, scroll_offset):
                            selected_astrian = None
                    else:
                        selected_astrian = get_clicked_astrian(mouse_pos, game_world.astrians, scroll_offset)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click to stop dragging
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                game_world.camera_x -= (mouse_x - drag_start_x) / game_world.zoom
                game_world.camera_y -= (mouse_y - drag_start_y) / game_world.zoom
                drag_start_x, drag_start_y = mouse_x, mouse_y
            else:
                game_world.check_hovered_city(pygame.mouse.get_pos())

    game_world.screen.fill(constants.black_color)

    game_world.handle_frame()

    # Render the UI
    render_ui(screen, game_world.astrians, scroll_offset, selected_astrian, game_world)

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
    if selected_astrian:
        selected_astrian.draw_highlight(screen, game_world.camera_x, game_world.camera_y, game_world.zoom)

    # Update the display
    pygame.display.flip()

