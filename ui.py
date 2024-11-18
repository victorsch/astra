import pygame, sys, math, random, names, time
import constants
from ui_tab import Tab

class UIManager:
    def __init__(self, game_world):
        self.game_world = game_world
        self.tabs = []
        self.current_tab = None
        self.font = pygame.font.SysFont('Arial', 20)
        self.selected_astrian = None
        self.selected_faction = None
        self.selected_city = None
        self.list_item_clicked = False
        self.astrian_back_button_rect = None
        # Camera position and zoom level
        self.dragging = False
        self.drag_start_x, self.drag_start_y = 0, 0
        self.scroll_offset = 0

    def add_tab(self, name, render_function):
        tab = Tab(name, render_function)
        self.tabs.append(tab)
        if self.current_tab is None:
            self.current_tab = tab

    def switch_tab(self, tab_name):
        for tab in self.tabs:
            if tab.name == tab_name:
                self.current_tab = tab
                self.scroll_offset = 0
                break

    # def render_ui(self, surface, astrians, selected_astrian):
    #     ui_surface = pygame.Surface((constants.screen_width, constants.ui_height))
    #     ui_surface.fill(constants.grey_color)
    #     y_offset = 10 - self.scroll_offset
    #     line_height = 20

    #     if self.selected_astrian:
    #         fields = [
    #             f"Name: {self.selected_astrian.name}",
    #             f"Health: {self.selected_astrian.health}",
    #             f"Faction: {self.selected_astrian.faction.name}",
    #             f"Kills: {self.selected_astrian.kill_count}",
    #             f"Children: {self.selected_astrian.child_count}",
    #             f"Pregnant: {self.selected_astrian.gestation_countdown > 0}",
    #             f"Gestation: {self.selected_astrian.gestation_countdown}",
    #             f"Mating Cooldown: {self.selected_astrian.mating_cooldown}",
    #             f"Collision Block Countdown: {self.selected_astrian.remove_collision_block_countdown}",
    #             f"Objective: {self.selected_astrian.current_action.name if self.selected_astrian.current_action is not None else ''}",
    #             f"Colliding Actors: {[actor for actor in self.selected_astrian.colliding_actors]}"
    #         ]

    #         for i, field in enumerate(fields):
    #             text_surface = self.font.render(field, True, constants.black_color)
    #             ui_surface.blit(text_surface, (10, y_offset + i * line_height))

    #         # Render the back button
    #         back_button_rect = pygame.Rect(10, y_offset + len(fields) * line_height + 20, 100, 30)
    #         pygame.draw.rect(ui_surface, constants.black_color, back_button_rect, 2)
    #         back_text_surface = self.font.render("Back", True, constants.black_color)
    #         #global astrian_back_button_rect
    #         self.astrian_back_button_rect = pygame.Rect(10, constants.screen_height + y_offset + len(fields) * line_height + 20, 100, 30)
    #         ui_surface.blit(back_text_surface, (20, y_offset + len(fields) * line_height + 25))

    #     else:
    #         for i, astrian in enumerate(self.game_world.astrians):
    #             text_surface = self.font.render(f"{astrian.name}: Health={astrian.health}, Faction={astrian.faction.name}, Age={astrian.get_age()}, Kills={astrian.kill_count}, Children={astrian.child_count}", True, constants.black_color)
    #             ui_surface.blit(text_surface, (10, y_offset + i * line_height))

    #         # Count the number of Astrians in each faction
    #         faction_counts = self.game_world.get_faction_counts()

    #         # Render the faction counts on the right side of the UI
    #         x_offset = constants.screen_width - 150
    #         y_offset = 10
    #         for faction, count in faction_counts.items():
    #             text_surface = self.font.render(f"{faction.capitalize()}: {count}", True, constants.black_color)
    #             ui_surface.blit(text_surface, (x_offset, y_offset))
    #             y_offset += line_height

    #         # Display the world age in the bottom right corner
    #         world_age = self.game_world.get_world_age()
    #         world_age_text = self.font.render(f"World Age: {int(world_age)}s", True, constants.black_color)
    #         ui_surface.blit(world_age_text, (constants.screen_width - 200, constants.ui_height - 30))

    #     surface.blit(ui_surface, (0, constants.screen_height))

    def render_ui(self, surface):
        ui_surface = pygame.Surface((constants.screen_width, constants.ui_height))
        ui_surface.fill(constants.grey_color)
        y_offset = 10 - self.scroll_offset
        line_height = 20

        if self.selected_astrian:
            self.render_astrian(ui_surface)

        elif (self.selected_city):
            self.render_city(ui_surface)

        elif (self.selected_faction):
            self.render_faction(ui_surface)

        else:
            # Render tab buttons
            tab_x_offset = 10
            tab_y_offset = 10 - self.scroll_offset
            for tab in self.tabs:
                tab_button_rect = pygame.Rect(tab_x_offset, tab_y_offset, 100, 30)
                pygame.draw.rect(ui_surface, constants.black_color, tab_button_rect, 2)
                tab_text_surface = self.font.render(tab.name, True, constants.black_color)
                ui_surface.blit(tab_text_surface, (tab_x_offset + 10, tab_y_offset + 5))
                tab_x_offset += 110

            # Render the current tab's content below the tabs
            content_y_offset = tab_y_offset + 40 - self.scroll_offset
            if self.current_tab:
                self.current_tab.render_function(ui_surface, content_y_offset, line_height)

        # world age
        self.render_world_age(ui_surface)

        surface.blit(ui_surface, (0, constants.screen_height))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.scroll_offset = max(0, self.scroll_offset - constants.scroll_speed)
                elif event.key == pygame.K_DOWN:
                    self.scroll_offset += constants.scroll_speed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] < constants.screen_height:  # Mouse is on the game world
                    if event.button == 4:  # Scroll up to zoom in
                        self.game_world.zoom = min(2.0, self.game_world.zoom + 0.02)
                    elif event.button == 5:  # Scroll down to zoom out
                        self.game_world.zoom = max(0.05, self.game_world.zoom - 0.02)
                    elif event.button == 1:  # Left click to start dragging
                        self.dragging = True
                        self.drag_start_x, self.drag_start_y = mouse_pos
                else:
                    if event.button == 4:  # Scroll up
                        self.scroll_offset = max(0, self.scroll_offset - constants.scroll_speed)
                    elif event.button == 5:  # Scroll down
                        total_text_height = len(self.game_world.astrians) * 20 + 10 # 
                        max_scroll_offset = max(0, total_text_height - constants.ui_height + 20)
                        self.scroll_offset = min(max_scroll_offset, self.scroll_offset + constants.scroll_speed)
                    elif event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()

                        # Check for tab clicks
                        tab_x_offset = 10
                        tab_y_offset = 10 - self.scroll_offset
                        for tab in self.tabs:
                            tab_button_rect = pygame.Rect(tab_x_offset, constants.screen_height + tab_y_offset, 100, 30)
                            print(tab_button_rect)
                            print(mouse_pos)
                            if tab_button_rect.collidepoint(mouse_pos):
                                self.switch_tab(tab.name)
                                return
                            tab_x_offset += 110

                        # Check for clicks on the lists
                        if self.current_tab:
                            content_y_offset = tab_y_offset + 40 - self.scroll_offset
                            self.current_tab.render_function(self.game_world.screen, content_y_offset, 20, mouse_pos)

                        # Check for clicks on Astrians, factions, or cities
                        if not self.list_item_clicked and (self.selected_astrian or self.selected_faction or self.selected_city):
                            if self.is_back_button_clicked(mouse_pos, self.scroll_offset):
                                self.selected_astrian = None
                                self.selected_faction = None
                                self.selected_city = None
                        # else:
                        #     clicked_astrian = self.get_clicked_astrian(mouse_pos, self.game_world.astrians, self.scroll_offset)
                        #     if clicked_astrian:
                        #         self.selected_astrian = clicked_astrian
                        #     else:
                        #         clicked_faction = self.get_clicked_faction(mouse_pos, self.game_world.factions, self.scroll_offset)
                        #         if clicked_faction:
                        #             self.selected_faction = clicked_faction
                        #         else:
                        #             clicked_city = self.get_clicked_city(mouse_pos, self.game_world.factions, self.scroll_offset)
                        #             if clicked_city:
                        #                 self.selected_city = clicked_city

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click to stop dragging
                    self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.game_world.camera_x -= (mouse_x - self.drag_start_x) / self.game_world.zoom
                    self.game_world.camera_y -= (mouse_y - self.drag_start_y) / self.game_world.zoom
                    self.drag_start_x, self.drag_start_y = mouse_x, mouse_y
                else:
                    self.game_world.check_hovered_city(pygame.mouse.get_pos())


    def render_world_age(self, surface):
        world_age = time.time() - self.game_world.start_time  # Assuming game_world has a start_time attribute
        world_age_years = int(world_age / constants.year_length)
        world_age_text = f"World Age: {int(world_age_years)} years"
        world_age_surface = self.font.render(world_age_text, True, constants.black_color)
        surface.blit(world_age_surface, (constants.screen_width - world_age_surface.get_width() - 10, 10))
    
    def render_astrian(self, ui_surface):
        y_offset = 10 - self.scroll_offset
        line_height = 20
        fields = [
            f"Name: {self.selected_astrian.name}",
            f"Health: {self.selected_astrian.health}",
            f"Faction: {self.selected_astrian.faction.name}",
            f"Kills: {self.selected_astrian.kill_count}",
            f"Children: {self.selected_astrian.child_count}",
            f"Pregnant: {self.selected_astrian.gestation_countdown > 0}",
            f"Gestation: {self.selected_astrian.gestation_countdown}",
            f"Mating Cooldown: {self.selected_astrian.mating_cooldown}",
            f"Collision Block Countdown: {self.selected_astrian.remove_collision_block_countdown}",
            f"Objective: {self.selected_astrian.current_action.name if self.selected_astrian.current_action is not None else ''}",
            f"Colliding Actors: {[actor for actor in self.selected_astrian.colliding_actors]}"
        ]

        for i, field in enumerate(fields):
            text_surface = self.font.render(field, True, constants.black_color)
            ui_surface.blit(text_surface, (10, y_offset + i * line_height))

        # Render the back button
        back_button_rect = pygame.Rect(10, y_offset + len(fields) * line_height + 20, 100, 30)
        pygame.draw.rect(ui_surface, constants.black_color, back_button_rect, 2)
        back_text_surface = self.font.render("Back", True, constants.black_color)
        #global astrian_back_button_rect
        self.astrian_back_button_rect = pygame.Rect(10, constants.screen_height + y_offset + len(fields) * line_height + 20, 100, 30)
        ui_surface.blit(back_text_surface, (20, y_offset + len(fields) * line_height + 25))

    
    def render_faction(self, ui_surface):
        y_offset = 10 - self.scroll_offset
        line_height = 20
        fields = [
            f"Name: {self.selected_faction.name}",
            f"Leader: {self.selected_faction.leader.name if self.selected_faction.leader else 'None'}",
            f"Members: {self.game_world.get_faction_counts().get(self.selected_faction.name, 0)}",
            f"Age: {self.selected_faction.get_age()}",
            f"Cities: {len(self.selected_faction.cities)}",
        ]

        for i, field in enumerate(fields):
            text_surface = self.font.render(field, True, constants.black_color)
            ui_surface.blit(text_surface, (10, y_offset + i * line_height))

        # Render the back button
        back_button_rect = pygame.Rect(10, y_offset + len(fields) * line_height + 20, 100, 30)
        pygame.draw.rect(ui_surface, constants.black_color, back_button_rect, 2)
        back_text_surface = self.font.render("Back", True, constants.black_color)
        #global astrian_back_button_rect
        self.astrian_back_button_rect = pygame.Rect(10, constants.screen_height + y_offset + len(fields) * line_height + 20, 100, 30)
        ui_surface.blit(back_text_surface, (20, y_offset + len(fields) * line_height + 25))

    def render_city(self, ui_surface):
        y_offset = 10 - self.scroll_offset
        line_height = 20
        fields = [
            f"Name: {self.selected_city.name}",
            f"Faction: {self.selected_city.faction.name}",
            f"Resources: {self.selected_city.resources}",
            f"Age: {self.selected_city.get_age()}",
        ]

        for i, field in enumerate(fields):
            text_surface = self.font.render(field, True, constants.black_color)
            ui_surface.blit(text_surface, (10, y_offset + i * line_height))

        # Render the back button
        back_button_rect = pygame.Rect(10, y_offset + len(fields) * line_height + 20, 100, 30)
        pygame.draw.rect(ui_surface, constants.black_color, back_button_rect, 2)
        back_text_surface = self.font.render("Back", True, constants.black_color)
        #global astrian_back_button_rect
        self.astrian_back_button_rect = pygame.Rect(10, constants.screen_height + y_offset + len(fields) * line_height + 20, 100, 30)
        ui_surface.blit(back_text_surface, (20, y_offset + len(fields) * line_height + 25))

    def get_clicked_astrian(self, mouse_pos, astrians, scroll_offset):
        y_offset = 10 - self.scroll_offset
        for i, astrian in enumerate(astrians):
            text_rect = pygame.Rect(10, constants.screen_height + y_offset + i * 20, 780, 20)
            if text_rect.collidepoint(mouse_pos):
                return astrian
        return None

    def get_clicked_faction(self, mouse_pos, factions, scroll_offset):
        y_offset = 10 - self.scroll_offset
        for i, faction in enumerate(factions):
            text_rect = pygame.Rect(10, constants.screen_height + y_offset + i * 20, 780, 20)
            if text_rect.collidepoint(mouse_pos):
                return faction
        return None

    def get_clicked_city(self, mouse_pos, factions, scroll_offset):
        y_offset = 10 - self.scroll_offset
        for faction in factions:
            for i, city in enumerate(faction.cities):
                text_rect = pygame.Rect(10, constants.screen_height + y_offset + i * 20, 780, 20)
                if text_rect.collidepoint(mouse_pos):
                    return city
        return None

    def is_back_button_clicked(self, mouse_pos, scroll_offset):
        if (self.astrian_back_button_rect is None):
            return False
        y_offset = 10 - self.scroll_offset
        return self.astrian_back_button_rect.collidepoint(mouse_pos)