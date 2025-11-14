"""
Save/Load Menu UI - User interface for managing game saves.

Allows players to:
- View list of all save files
- Load a saved game
- Create a new manual save
- Delete save files
"""

import pygame
from typing import Optional, List, Dict


class SaveLoadMenu:
    """
    User interface for save/load management.

    Displays a menu with save file list and controls for:
    - Loading saves
    - Creating new saves
    - Deleting saves
    """

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the save/load menu.

        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Visibility
        self.visible = False

        # Menu dimensions
        self.menu_width = 800
        self.menu_height = 600
        self.menu_x = (screen_width - self.menu_width) // 2
        self.menu_y = (screen_height - self.menu_height) // 2

        # Fonts
        self.font_title = pygame.font.Font(None, 48)
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        # Colors
        self.color_bg = (20, 20, 30)
        self.color_panel = (40, 40, 50)
        self.color_text = (255, 255, 255)
        self.color_highlight = (100, 150, 255)
        self.color_selected = (150, 200, 255)
        self.color_button = (60, 60, 80)
        self.color_button_hover = (80, 80, 100)
        self.color_delete = (200, 50, 50)
        self.color_delete_hover = (255, 70, 70)

        # Save list
        self.save_files: List[Dict] = []
        self.selected_index: Optional[int] = None
        self.scroll_offset = 0
        self.max_visible_saves = 8

        # Input state
        self.creating_new_save = False
        self.new_save_name = ""
        self.delete_confirmation = None  # Index of save to delete

        # Button rects (for click detection)
        self.button_rects = {}

        # Result from menu (for game to act on)
        self.load_save_name: Optional[str] = None
        self.save_game_name: Optional[str] = None
        self.delete_save_name: Optional[str] = None

    def toggle(self):
        """Toggle menu visibility."""
        self.visible = not self.visible
        if self.visible:
            # Reset state when opening
            self.creating_new_save = False
            self.new_save_name = ""
            self.delete_confirmation = None
            self.selected_index = None

    def show(self):
        """Show the menu."""
        self.visible = True
        self.creating_new_save = False
        self.new_save_name = ""
        self.delete_confirmation = None

    def hide(self):
        """Hide the menu."""
        self.visible = False

    def update_save_list(self, save_files: List[Dict]):
        """
        Update the list of save files.

        Args:
            save_files: List of save file info dictionaries
        """
        self.save_files = save_files

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False

        # Handle new save name input
        if self.creating_new_save:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Confirm new save
                    if self.new_save_name.strip():
                        self.save_game_name = self.new_save_name.strip()
                        self.creating_new_save = False
                        self.new_save_name = ""
                        return True
                elif event.key == pygame.K_ESCAPE:
                    # Cancel
                    self.creating_new_save = False
                    self.new_save_name = ""
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.new_save_name = self.new_save_name[:-1]
                    return True
                elif event.unicode and event.unicode.isprintable():
                    if len(self.new_save_name) < 30:  # Max name length
                        self.new_save_name += event.unicode
                    return True
            return True  # Consume all events while typing

        # Handle delete confirmation
        if self.delete_confirmation is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    # Confirm delete
                    save_info = self.save_files[self.delete_confirmation]
                    self.delete_save_name = save_info['name']
                    self.delete_confirmation = None
                    self.selected_index = None
                    return True
                elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    # Cancel delete
                    self.delete_confirmation = None
                    return True
            return True  # Consume all events during confirmation

        # Keyboard events
        if event.type == pygame.KEYDOWN:
            # ESC to close menu
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True

            # Arrow keys for navigation
            elif event.key == pygame.K_UP:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = max(0, self.selected_index - 1)
                self._ensure_visible(self.selected_index)
                return True

            elif event.key == pygame.K_DOWN:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = min(len(self.save_files) - 1, self.selected_index + 1)
                self._ensure_visible(self.selected_index)
                return True

            # Enter to load selected
            elif event.key == pygame.K_RETURN:
                if self.selected_index is not None and 0 <= self.selected_index < len(self.save_files):
                    save_info = self.save_files[self.selected_index]
                    self.load_save_name = save_info['name']
                    return True

            # Delete key to delete selected
            elif event.key == pygame.K_DELETE:
                if self.selected_index is not None and 0 <= self.selected_index < len(self.save_files):
                    self.delete_confirmation = self.selected_index
                    return True

        # Mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check button clicks
            for button_name, rect in self.button_rects.items():
                if rect.collidepoint(mouse_pos):
                    if button_name == "new_save":
                        self.creating_new_save = True
                        self.new_save_name = ""
                        return True
                    elif button_name == "close":
                        self.hide()
                        return True
                    elif button_name.startswith("load_"):
                        index = int(button_name.split("_")[1])
                        save_info = self.save_files[index]
                        self.load_save_name = save_info['name']
                        return True
                    elif button_name.startswith("delete_"):
                        index = int(button_name.split("_")[1])
                        self.delete_confirmation = index
                        return True

            # Check save list clicks
            list_start_y = self.menu_y + 80
            for i in range(min(self.max_visible_saves, len(self.save_files) - self.scroll_offset)):
                actual_index = i + self.scroll_offset
                item_y = list_start_y + i * 60
                item_rect = pygame.Rect(self.menu_x + 20, item_y, self.menu_width - 240, 55)

                if item_rect.collidepoint(mouse_pos):
                    self.selected_index = actual_index
                    return True

        # Mouse wheel for scrolling
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.y < 0:  # Scroll down
                max_scroll = max(0, len(self.save_files) - self.max_visible_saves)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
            return True

        return False

    def _ensure_visible(self, index: int):
        """Ensure the given index is visible by adjusting scroll offset."""
        if index < self.scroll_offset:
            self.scroll_offset = index
        elif index >= self.scroll_offset + self.max_visible_saves:
            self.scroll_offset = index - self.max_visible_saves + 1

    def render(self, screen: pygame.Surface):
        """
        Render the save/load menu.

        Args:
            screen: Pygame surface to render to
        """
        if not self.visible:
            return

        # Clear button rects for this frame
        self.button_rects.clear()

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Main menu panel
        menu_surface = pygame.Surface((self.menu_width, self.menu_height))
        menu_surface.fill(self.color_bg)
        pygame.draw.rect(menu_surface, self.color_highlight, (0, 0, self.menu_width, self.menu_height), 3)

        # Title
        title_text = self.font_title.render("Save / Load Game", True, self.color_text)
        title_rect = title_text.get_rect(centerx=self.menu_width // 2, top=20)
        menu_surface.blit(title_text, title_rect)

        # Render based on state
        if self.creating_new_save:
            self._render_new_save_dialog(menu_surface)
        elif self.delete_confirmation is not None:
            self._render_delete_confirmation(menu_surface)
        else:
            self._render_save_list(menu_surface)

        # Blit menu to screen
        screen.blit(menu_surface, (self.menu_x, self.menu_y))

    def _render_save_list(self, surface: pygame.Surface):
        """Render the list of save files."""
        # Instructions
        instructions = "↑↓: Navigate  |  ENTER: Load  |  DEL: Delete  |  ESC: Close"
        instr_text = self.font_small.render(instructions, True, (150, 150, 150))
        instr_rect = instr_text.get_rect(centerx=self.menu_width // 2, top=65)
        surface.blit(instr_text, instr_rect)

        # Save list
        list_start_y = 100
        if not self.save_files:
            # No saves
            no_saves_text = self.font_medium.render("No save files found", True, (150, 150, 150))
            no_saves_rect = no_saves_text.get_rect(center=(self.menu_width // 2, 300))
            surface.blit(no_saves_text, no_saves_rect)
        else:
            # Render visible saves
            for i in range(min(self.max_visible_saves, len(self.save_files) - self.scroll_offset)):
                actual_index = i + self.scroll_offset
                save_info = self.save_files[actual_index]

                item_y = list_start_y + i * 60
                self._render_save_item(surface, save_info, actual_index, 20, item_y)

        # Buttons at bottom
        button_y = self.menu_height - 70

        # New Save button
        new_save_rect = pygame.Rect(20, button_y, 200, 50)
        self.button_rects["new_save"] = new_save_rect.move(self.menu_x, self.menu_y)
        mouse_pos = pygame.mouse.get_pos()
        local_mouse = (mouse_pos[0] - self.menu_x, mouse_pos[1] - self.menu_y)
        button_color = self.color_button_hover if new_save_rect.collidepoint(local_mouse) else self.color_button
        pygame.draw.rect(surface, button_color, new_save_rect)
        pygame.draw.rect(surface, self.color_highlight, new_save_rect, 2)
        new_text = self.font_medium.render("New Save", True, self.color_text)
        new_rect = new_text.get_rect(center=new_save_rect.center)
        surface.blit(new_text, new_rect)

        # Close button
        close_rect = pygame.Rect(self.menu_width - 220, button_y, 200, 50)
        self.button_rects["close"] = close_rect.move(self.menu_x, self.menu_y)
        button_color = self.color_button_hover if close_rect.collidepoint(local_mouse) else self.color_button
        pygame.draw.rect(surface, button_color, close_rect)
        pygame.draw.rect(surface, self.color_highlight, close_rect, 2)
        close_text = self.font_medium.render("Close", True, self.color_text)
        close_rect_text = close_text.get_rect(center=close_rect.center)
        surface.blit(close_text, close_rect_text)

    def _render_save_item(self, surface: pygame.Surface, save_info: Dict, index: int, x: int, y: int):
        """Render a single save file item."""
        item_width = self.menu_width - 240
        item_height = 55

        # Background
        is_selected = (index == self.selected_index)
        bg_color = self.color_selected if is_selected else self.color_panel
        pygame.draw.rect(surface, bg_color, (x, y, item_width, item_height))
        if is_selected:
            pygame.draw.rect(surface, self.color_highlight, (x, y, item_width, item_height), 2)

        # Save name
        name_text = self.font_large.render(save_info['name'], True, self.color_text)
        surface.blit(name_text, (x + 10, y + 5))

        # Info line (day, money, timestamp)
        info_parts = []
        if 'day' in save_info:
            info_parts.append(f"Day {save_info['day']}")
        if 'money' in save_info:
            info_parts.append(f"${save_info['money']:,.0f}")
        if 'timestamp' in save_info:
            # Format timestamp
            timestamp_str = save_info['timestamp']
            if 'T' in timestamp_str:
                date_part, time_part = timestamp_str.split('T')
                time_short = time_part.split('.')[0]  # Remove microseconds
                info_parts.append(f"{date_part} {time_short}")

        info_text = self.font_small.render("  |  ".join(info_parts), True, (180, 180, 180))
        surface.blit(info_text, (x + 10, y + 32))

        # Load button
        load_button_rect = pygame.Rect(x + item_width + 10, y, 100, 25)
        self.button_rects[f"load_{index}"] = load_button_rect.move(self.menu_x, self.menu_y)
        mouse_pos = pygame.mouse.get_pos()
        local_mouse = (mouse_pos[0] - self.menu_x, mouse_pos[1] - self.menu_y)
        button_color = self.color_button_hover if load_button_rect.collidepoint(local_mouse) else self.color_button
        pygame.draw.rect(surface, button_color, load_button_rect)
        pygame.draw.rect(surface, self.color_highlight, load_button_rect, 1)
        load_text = self.font_small.render("Load", True, self.color_text)
        load_text_rect = load_text.get_rect(center=load_button_rect.center)
        surface.blit(load_text, load_text_rect)

        # Delete button
        delete_button_rect = pygame.Rect(x + item_width + 120, y + 30, 100, 25)
        self.button_rects[f"delete_{index}"] = delete_button_rect.move(self.menu_x, self.menu_y)
        button_color = self.color_delete_hover if delete_button_rect.collidepoint(local_mouse) else self.color_delete
        pygame.draw.rect(surface, button_color, delete_button_rect)
        pygame.draw.rect(surface, (255, 100, 100), delete_button_rect, 1)
        delete_text = self.font_small.render("Delete", True, self.color_text)
        delete_text_rect = delete_text.get_rect(center=delete_button_rect.center)
        surface.blit(delete_text, delete_text_rect)

    def _render_new_save_dialog(self, surface: pygame.Surface):
        """Render the new save name input dialog."""
        # Dialog box
        dialog_width = 600
        dialog_height = 200
        dialog_x = (self.menu_width - dialog_width) // 2
        dialog_y = (self.menu_height - dialog_height) // 2

        pygame.draw.rect(surface, self.color_panel, (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(surface, self.color_highlight, (dialog_x, dialog_y, dialog_width, dialog_height), 3)

        # Title
        title_text = self.font_large.render("Enter Save Name", True, self.color_text)
        title_rect = title_text.get_rect(centerx=self.menu_width // 2, top=dialog_y + 20)
        surface.blit(title_text, title_rect)

        # Input box
        input_box = pygame.Rect(dialog_x + 50, dialog_y + 70, dialog_width - 100, 40)
        pygame.draw.rect(surface, (60, 60, 80), input_box)
        pygame.draw.rect(surface, self.color_highlight, input_box, 2)

        # Input text
        input_text = self.font_medium.render(self.new_save_name + "_", True, self.color_text)
        surface.blit(input_text, (input_box.x + 10, input_box.y + 8))

        # Instructions
        instr_text = self.font_small.render("ENTER: Confirm  |  ESC: Cancel", True, (150, 150, 150))
        instr_rect = instr_text.get_rect(centerx=self.menu_width // 2, top=dialog_y + 130)
        surface.blit(instr_text, instr_rect)

    def _render_delete_confirmation(self, surface: pygame.Surface):
        """Render the delete confirmation dialog."""
        save_info = self.save_files[self.delete_confirmation]

        # Dialog box
        dialog_width = 600
        dialog_height = 200
        dialog_x = (self.menu_width - dialog_width) // 2
        dialog_y = (self.menu_height - dialog_height) // 2

        pygame.draw.rect(surface, self.color_panel, (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(surface, self.color_delete, (dialog_x, dialog_y, dialog_width, dialog_height), 3)

        # Title
        title_text = self.font_large.render("Delete Save?", True, self.color_delete)
        title_rect = title_text.get_rect(centerx=self.menu_width // 2, top=dialog_y + 20)
        surface.blit(title_text, title_rect)

        # Save name
        name_text = self.font_medium.render(f'"{save_info["name"]}"', True, self.color_text)
        name_rect = name_text.get_rect(centerx=self.menu_width // 2, top=dialog_y + 70)
        surface.blit(name_text, name_rect)

        # Warning
        warning_text = self.font_small.render("This action cannot be undone!", True, (255, 200, 100))
        warning_rect = warning_text.get_rect(centerx=self.menu_width // 2, top=dialog_y + 105)
        surface.blit(warning_text, warning_rect)

        # Instructions
        instr_text = self.font_medium.render("Press Y to confirm, N to cancel", True, (150, 150, 150))
        instr_rect = instr_text.get_rect(centerx=self.menu_width // 2, top=dialog_y + 140)
        surface.blit(instr_text, instr_rect)

    def get_and_clear_load_request(self) -> Optional[str]:
        """Get and clear any pending load request."""
        result = self.load_save_name
        self.load_save_name = None
        return result

    def get_and_clear_save_request(self) -> Optional[str]:
        """Get and clear any pending save request."""
        result = self.save_game_name
        self.save_game_name = None
        return result

    def get_and_clear_delete_request(self) -> Optional[str]:
        """Get and clear any pending delete request."""
        result = self.delete_save_name
        self.delete_save_name = None
        return result
