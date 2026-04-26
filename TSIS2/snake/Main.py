import pygame
import json
import os
import sys

from Config import *
import Db
from Game import SnakeGame

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULTS = {
    "snake_color": list(GREEN),
    "grid_overlay": True,
    "sound": True,
}


def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, "r") as f:
            data = json.load(f)
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULTS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception:
        pass


def draw_text(surface, text, font, color, center):
    surf = font.render(text, True, color)
    surface.blit(surf, surf.get_rect(center=center))


def button_rect(cx, cy, w=220, h=44) -> pygame.Rect:
    return pygame.Rect(cx - w // 2, cy - h // 2, w, h)


def draw_button(surface, rect, text, font, *, highlight=False):
    color = (100, 180, 80) if highlight else (70, 70, 70)
    border = (150, 220, 110) if highlight else (130, 130, 130)
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    draw_text(surface, text, font, WHITE, rect.center)


def is_hovered(rect: pygame.Rect) -> bool:
    return rect.collidepoint(pygame.mouse.get_pos())


class MainMenuScreen:
    def __init__(self, surface, fonts):
        self.surface = surface
        self.fonts = fonts
        self.username = ""
        self.action = None
        self.error_msg = ""

        cx = WINDOW_WIDTH // 2
        self.btn_play = button_rect(cx, 300)
        self.btn_leaderboard = button_rect(cx, 358)
        self.btn_settings = button_rect(cx, 416)
        self.btn_quit = button_rect(cx, 474)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN:
                self._try_play()
            else:
                if len(self.username) < 20 and event.unicode.isprintable():
                    self.username += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_play.collidepoint(event.pos):
                self._try_play()
            elif self.btn_leaderboard.collidepoint(event.pos):
                self.action = "leaderboard"
            elif self.btn_settings.collidepoint(event.pos):
                self.action = "settings"
            elif self.btn_quit.collidepoint(event.pos):
                self.action = "quit"

    def _try_play(self):
        name = self.username.strip()
        self.action = "play" if name else None
        self.error_msg = "" if name else "Please enter a username!"

    def draw(self):
        s = self.surface
        cx = WINDOW_WIDTH // 2
        s.fill((15, 20, 15))

        draw_text(s, "SNAKE GAME", self.fonts["title"], GREEN, (cx, 90))

        draw_text(s, "Username:", self.fonts["body"], LIGHT_GRAY, (cx, 185))
        field = pygame.Rect(cx - 140, 200, 280, 36)
        pygame.draw.rect(s, (40, 60, 40), field, border_radius=6)
        pygame.draw.rect(s, GREEN, field, 2, border_radius=6)

        cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""
        draw_text(s, self.username + cursor, self.fonts["body"], WHITE, field.center)

        if self.error_msg:
            draw_text(s, self.error_msg, self.fonts["small"], RED, (cx, 245))

        for rect, label in [
            (self.btn_play, "PLAY"),
            (self.btn_leaderboard, "LEADERBOARD"),
            (self.btn_settings, "SETTINGS"),
            (self.btn_quit, "QUIT"),
        ]:
            draw_button(s, rect, label, self.fonts["body"], highlight=is_hovered(rect))


class GameOverScreen:
    def __init__(self, surface, fonts, score, level, personal_best):
        self.surface = surface
        self.fonts = fonts
        self.score = score
        self.level = level
        self.personal_best = max(personal_best, score)
        self.action = None

        cx = WINDOW_WIDTH // 2
        self.btn_retry = button_rect(cx, 390)
        self.btn_menu = button_rect(cx, 450)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_retry.collidepoint(event.pos):
                self.action = "retry"
            elif self.btn_menu.collidepoint(event.pos):
                self.action = "menu"

    def draw(self):
        s = self.surface
        cx = WINDOW_WIDTH // 2
        s.fill((20, 10, 10))

        draw_text(s, "GAME OVER", self.fonts["title"], RED, (cx, 110))
        draw_text(s, f"Score: {self.score}", self.fonts["body"], YELLOW, (cx, 230))
        draw_text(s, f"Level reached: {self.level}", self.fonts["body"], CYAN, (cx, 275))
        draw_text(s, f"Personal best: {self.personal_best}", self.fonts["body"], GREEN, (cx, 320))

        draw_button(s, self.btn_retry, "RETRY", self.fonts["body"], highlight=is_hovered(self.btn_retry))
        draw_button(s, self.btn_menu, "MAIN MENU", self.fonts["body"], highlight=is_hovered(self.btn_menu))


class LeaderboardScreen:
    def __init__(self, surface, fonts, db_available):
        self.surface = surface
        self.fonts = fonts
        self.action = None
        self.db_available = db_available
        self.rows = Db.get_leaderboard(10) if db_available else []

        cx = WINDOW_WIDTH // 2
        self.btn_back = button_rect(cx, 510)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_back.collidepoint(event.pos):
                self.action = "back"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.action = "back"

    def draw(self):
        s = self.surface
        cx = WINDOW_WIDTH // 2
        s.fill((10, 15, 25))

        draw_text(s, "LEADERBOARD", self.fonts["title"], CYAN, (cx, 45))

        if not self.db_available:
            draw_text(s, "Database not connected.", self.fonts["body"], RED, (cx, 200))
        else:
            col_x = [60, 200, 420, 540, 660]
            headers = ["RANK", "USERNAME", "SCORE", "LEVEL", "DATE"]

            for label, x in zip(headers, col_x):
                draw_text(s, label, self.fonts["small"], GRAY, (x, 110))

            pygame.draw.line(s, GRAY, (30, 126), (WINDOW_WIDTH - 30, 126), 1)

            if not self.rows:
                draw_text(s, "No scores yet", self.fonts["body"], GRAY, (cx, 310))
            else:
                for i, row in enumerate(self.rows):
                    y = 148 + i * 32
                    color = YELLOW if i == 0 else CYAN if i == 1 else ORANGE if i == 2 else WHITE
                    values = [
                        f"#{row['rank']}",
                        str(row['username'])[:14],
                        str(row['score']),
                        str(row['level_reached']),
                        str(row['played_at'])[:10] if row['played_at'] else "-",
                    ]
                    for text, x in zip(values, col_x):
                        draw_text(s, text, self.fonts["small"], color, (x, y))

        draw_button(s, self.btn_back, "BACK", self.fonts["body"], highlight=is_hovered(self.btn_back))


class SettingsScreen:
    def __init__(self, surface, fonts, settings):
        self.surface = surface
        self.fonts = fonts
        self.settings = dict(settings)
        self.action = None

        cx = WINDOW_WIDTH // 2
        self.btn_grid = button_rect(cx + 130, 210, w=110)
        self.btn_sound = button_rect(cx + 130, 280, w=110)
        self.btn_save = button_rect(cx, 490)

        self.color_rects = []
        start_x = cx - (8 * 56) // 2 + 24
        for i, (_, rgb) in enumerate([
            ("Green", (50, 205, 50)),
            ("Cyan", (0, 220, 220)),
            ("Yellow", (255, 215, 0)),
            ("Orange", (255, 140, 0)),
            ("Purple", (180, 60, 220)),
            ("Blue", (50, 100, 220)),
            ("Red", (220, 50, 50)),
            ("White", (230, 230, 230)),
        ]):
            self.color_rects.append((pygame.Rect(start_x + i * 56, 370, 44, 44), rgb))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_grid.collidepoint(event.pos):
                self.settings["grid_overlay"] = not self.settings["grid_overlay"]
            elif self.btn_sound.collidepoint(event.pos):
                self.settings["sound"] = not self.settings["sound"]
            elif self.btn_save.collidepoint(event.pos):
                self.action = "save"
            else:
                for rect, rgb in self.color_rects:
                    if rect.collidepoint(event.pos):
                        self.settings["snake_color"] = list(rgb)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.action = "back"

    def draw(self):
        s = self.surface
        cx = WINDOW_WIDTH // 2
        s.fill((15, 15, 30))

        draw_text(s, "SETTINGS", self.fonts["title"], PURPLE, (cx, 60))

        draw_text(s, "Grid Overlay:", self.fonts["body"], LIGHT_GRAY, (cx - 60, 210))
        draw_button(s, self.btn_grid, "ON" if self.settings["grid_overlay"] else "OFF",
                    self.fonts["body"], highlight=self.settings["grid_overlay"])

        draw_text(s, "Sound:", self.fonts["body"], LIGHT_GRAY, (cx - 60, 280))
        draw_button(s, self.btn_sound, "ON" if self.settings["sound"] else "OFF",
                    self.fonts["body"], highlight=self.settings["sound"])

        for rect, rgb in self.color_rects:
            pygame.draw.rect(s, rgb, rect, border_radius=6)

        draw_button(s, self.btn_save, "SAVE & BACK", self.fonts["body"],
                    highlight=is_hovered(self.btn_save))


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.fonts = {
            "title": pygame.font.SysFont("consolas", 52, bold=True),
            "body": pygame.font.SysFont("consolas", 20),
            "small": pygame.font.SysFont("consolas", 15),
        }

        self.settings = load_settings()
        self.db_ok = Db.init_db()

        self.state = "menu"
        self.current_screen = MainMenuScreen(self.screen, self.fonts)
        self.game = None
        self.username = ""
        self.player_id = None
        self.personal_best = 0

    def run(self):
        running = True
        while running:
            self.clock.tick(120)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._dispatch_event(event)

            self._update()
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _dispatch_event(self, event):
        if self.state == "play" and self.game:
            self.game.handle_event(event)
        elif self.current_screen:
            self.current_screen.handle_event(event)

    def _update(self):
        if self.state == "play" and self.game:
            self.game.update()
            if self.game.game_over:
                self._on_game_over()

        if self.state == "menu":
            self._check_menu()
        elif self.state == "game_over":
            self._check_game_over()
        elif self.state == "settings":
            if self.current_screen.action in ("save", "back"):
                if self.current_screen.action == "save":
                    self.settings = self.current_screen.settings
                    save_settings(self.settings)
                self._goto_menu()
        elif self.state == "leaderboard":
            if self.current_screen.action == "back":
                self._goto_menu()

    def _draw(self):
        if self.state == "play" and self.game:
            self.game.draw()
        else:
            self.current_screen.draw()

    def _check_menu(self):
        act = self.current_screen.action
        if act == "play":
            self.username = self.current_screen.username.strip()
            if self.db_ok:
                self.player_id = Db.get_or_create_player(self.username)
                self.personal_best = Db.get_personal_best(self.player_id) if self.player_id else 0
            self._start_game()
        elif act == "leaderboard":
            self.state = "leaderboard"
            self.current_screen = LeaderboardScreen(self.screen, self.fonts, self.db_ok)
        elif act == "settings":
            self.state = "settings"
            self.current_screen = SettingsScreen(self.screen, self.fonts, self.settings)
        elif act == "quit":
            pygame.quit()
            sys.exit()

    def _check_game_over(self):
        act = self.current_screen.action
        if act == "retry":
            self._start_game()
        elif act == "menu":
            self._goto_menu()

    def _start_game(self):
        self.state = "play"
        self.game = SnakeGame(
            self.screen,
            tuple(self.settings["snake_color"]),
            self.settings["grid_overlay"],
            self.player_id,
            self.personal_best,
        )
        self.current_screen = None

    def _on_game_over(self):
        score, level = self.game.result.values()
        if self.db_ok and self.player_id:
            Db.save_session(self.player_id, score, level)
            self.personal_best = Db.get_personal_best(self.player_id)

        self.state = "game_over"
        self.current_screen = GameOverScreen(self.screen, self.fonts, score, level, self.personal_best)
        self.game = None

    def _goto_menu(self):
        self.state = "menu"
        menu = MainMenuScreen(self.screen, self.fonts)
        menu.username = self.username
        self.current_screen = menu


if __name__ == "__main__":
    App().run()