# game.py — Core Snake game logic and rendering

import pygame
import random
import time
from Config import *


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def cell_rect(col: int, row: int) -> pygame.Rect:
    """Return the pixel Rect for a grid cell in the play area."""
    return pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def random_cell(exclude: set, cols: int = PLAY_AREA_COLS, rows: int = GRID_ROWS) -> tuple:
    """Return a random (col, row) not in exclude set."""
    attempts = 0
    while attempts < 2000:
        c = random.randint(0, cols - 1)
        r = random.randint(0, rows - 1)
        if (c, r) not in exclude:
            return (c, r)
        attempts += 1
    return None  # Arena full (shouldn't happen in practice)


# ─────────────────────────────────────────────
#  Food item
# ─────────────────────────────────────────────

class FoodItem:
    def __init__(self, pos: tuple, kind: str = "normal"):
        self.pos = pos
        self.kind = kind          # normal | bonus | timed | poison
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = FOOD_DISAPPEAR_MS if kind in ("timed", "poison") else None

    @property
    def expired(self) -> bool:
        if self.lifetime is None:
            return False
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime

    def draw(self, surface: pygame.Surface):
        color = FOOD_COLORS.get(self.kind, GREEN)
        r = cell_rect(*self.pos)
        pygame.draw.rect(surface, color, r.inflate(-4, -4), border_radius=4)
        if self.kind == "poison":
            # skull-ish cross
            cx, cy = r.centerx, r.centery
            pygame.draw.line(surface, WHITE, (cx - 5, cy - 5), (cx + 5, cy + 5), 2)
            pygame.draw.line(surface, WHITE, (cx + 5, cy - 5), (cx - 5, cy + 5), 2)


# ─────────────────────────────────────────────
#  Power-up item
# ─────────────────────────────────────────────

class PowerUp:
    def __init__(self, pos: tuple, kind: str):
        self.pos = pos
        self.kind = kind          # speed | slow | shield
        self.spawn_time = pygame.time.get_ticks()

    @property
    def expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_FIELD_MS

    def draw(self, surface: pygame.Surface):
        color = POWERUP_COLORS.get(self.kind, WHITE)
        r = cell_rect(*self.pos)
        pygame.draw.rect(surface, color, r.inflate(-2, -2), border_radius=6)
        # small letter label
        font = pygame.font.SysFont("consolas", 11, bold=True)
        label = self.kind[0].upper()
        txt = font.render(label, True, BLACK)
        surface.blit(txt, txt.get_rect(center=r.center))


# ─────────────────────────────────────────────
#  Active power-up effect tracker
# ─────────────────────────────────────────────

class ActiveEffect:
    def __init__(self, kind: str):
        self.kind = kind
        self.start_time = pygame.time.get_ticks()

    @property
    def expired(self) -> bool:
        return pygame.time.get_ticks() - self.start_time > POWERUP_DURATION_MS

    @property
    def remaining_sec(self) -> float:
        elapsed = pygame.time.get_ticks() - self.start_time
        return max(0.0, (POWERUP_DURATION_MS - elapsed) / 1000)


# ─────────────────────────────────────────────
#  Main Game class
# ─────────────────────────────────────────────

class SnakeGame:
    def __init__(self, surface: pygame.Surface, snake_color, grid_overlay: bool,
                 player_id: int, personal_best: int):
        self.surface = surface
        self.snake_color = snake_color
        self.grid_overlay = grid_overlay
        self.player_id = player_id
        self.personal_best = personal_best

        # Fonts
        self.font_sm = pygame.font.SysFont("consolas", 14)
        self.font_md = pygame.font.SysFont("consolas", 18, bold=True)

        self._init_state()

    # ── State initialisation ──────────────────

    def _init_state(self):
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.game_over = False

        # Snake: list of (col, row), head = [0]
        mid_col = PLAY_AREA_COLS // 2
        mid_row = GRID_ROWS // 2
        self.snake = [(mid_col, mid_row), (mid_col - 1, mid_row), (mid_col - 2, mid_row)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

        # Obstacles
        self.obstacles: set = set()

        # Foods & power-ups
        self.foods: list[FoodItem] = []
        self.powerup: PowerUp | None = None
        self.active_effect: ActiveEffect | None = None
        self.shield_ready = False   # shield collected but not triggered

        # Speed
        self.current_speed = BASE_SPEED  # ms per move
        self._last_move_time = pygame.time.get_ticks()

        # Spawn initial food
        self._spawn_food()

    # ── Occupied cells helper ─────────────────

    def _occupied(self) -> set:
        occ = set(self.snake) | self.obstacles
        for f in self.foods:
            occ.add(f.pos)
        if self.powerup:
            occ.add(self.powerup.pos)
        return occ

    # ── Level / Speed ─────────────────────────

    def _advance_level(self):
        self.level += 1
        self.food_eaten = 0
        speed_ms = max(MIN_SPEED, BASE_SPEED - (self.level - 1) * SPEED_INCREMENT)
        self.current_speed = speed_ms
        if self.level >= OBSTACLE_START_LEVEL:
            self._add_obstacles()

    def _effective_speed(self) -> int:
        base = self.current_speed
        if self.active_effect and not self.active_effect.expired:
            if self.active_effect.kind == "speed":
                return int(base * SPEED_BOOST_FACTOR)
            elif self.active_effect.kind == "slow":
                return int(base * SLOW_MOTION_FACTOR)
        return base

    # ── Obstacle placement ────────────────────

    def _add_obstacles(self):
        count = OBSTACLES_PER_LEVEL
        snake_set = set(self.snake)
        # Safety zone: 3-cell radius around snake head
        hcol, hrow = self.snake[0]
        safe = {(hcol + dc, hrow + dr)
                for dc in range(-3, 4) for dr in range(-3, 4)}
        attempts = 0
        added = 0
        while added < count and attempts < 500:
            pos = random_cell(self._occupied() | safe)
            if pos and pos not in self.obstacles and pos not in snake_set:
                self.obstacles.add(pos)
                added += 1
            attempts += 1

    # ── Food spawning ─────────────────────────

    def _spawn_food(self):
        # Keep at most 2 food items on the field
        while len(self.foods) < 2:
            occ = self._occupied()
            pos = random_cell(occ)
            if pos is None:
                break
            # Decide kind
            r = random.random()
            if r < POISON_APPEAR_CHANCE:
                kind = "poison"
            elif r < 0.45:
                kind = "bonus"
            elif r < 0.70:
                kind = "timed"
            else:
                kind = "normal"
            self.foods.append(FoodItem(pos, kind))

    # ── Power-up spawning ─────────────────────

    def _try_spawn_powerup(self):
        if self.powerup is not None:
            return
        if random.random() < POWERUP_SPAWN_CHANCE:
            pos = random_cell(self._occupied())
            if pos:
                kind = random.choice(["speed", "slow", "shield"])
                self.powerup = PowerUp(pos, kind)

    # ── Event handling ────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            dx, dy = self.direction
            if event.key in (pygame.K_UP, pygame.K_w) and dy == 0:
                self.next_direction = (0, -1)
            elif event.key in (pygame.K_DOWN, pygame.K_s) and dy == 0:
                self.next_direction = (0, 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a) and dx == 0:
                self.next_direction = (-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and dx == 0:
                self.next_direction = (1, 0)

    # ── Update (one tick) ─────────────────────

    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        # Expire timed / poison foods
        self.foods = [f for f in self.foods if not f.expired]
        self._spawn_food()

        # Expire field power-up
        if self.powerup and self.powerup.expired:
            self.powerup = None

        # Expire active effect
        if self.active_effect and self.active_effect.expired:
            self.active_effect = None

        # Move on speed tick
        if now - self._last_move_time < self._effective_speed():
            return
        self._last_move_time = now

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # ── Collision: walls
        if not (0 <= new_head[0] < PLAY_AREA_COLS and 0 <= new_head[1] < GRID_ROWS):
            if self.shield_ready:
                self.shield_ready = False
                # Wrap or bounce — just cancel move (stay in place)
                return
            self.game_over = True
            return

        # ── Collision: self
        if new_head in self.snake[:-1]:
            if self.shield_ready:
                self.shield_ready = False
                return
            self.game_over = True
            return

        # ── Collision: obstacle
        if new_head in self.obstacles:
            if self.shield_ready:
                self.shield_ready = False
                return
            self.game_over = True
            return

        # Move snake
        self.snake.insert(0, new_head)

        # ── Eat food?
        eaten_food = next((f for f in self.foods if f.pos == new_head), None)
        if eaten_food:
            self.foods.remove(eaten_food)
            if eaten_food.kind == "poison":
                # Shorten by 2
                for _ in range(2):
                    if len(self.snake) > 1:
                        self.snake.pop()
                if len(self.snake) <= 1:
                    self.game_over = True
                    return
                # Do NOT pop tail (snake shortened above)
            else:
                pts = FOOD_POINTS.get(eaten_food.kind, 10)
                self.score += pts
                self.food_eaten += 1
                if self.food_eaten >= FOOD_PER_LEVEL:
                    self._advance_level()
                self._try_spawn_powerup()
                # Do NOT pop tail — snake grows
        else:
            self.snake.pop()  # Normal move: remove tail

        self._spawn_food()

        # ── Pick up power-up?
        if self.powerup and self.powerup.pos == new_head:
            kind = self.powerup.kind
            self.powerup = None
            if kind == "shield":
                self.shield_ready = True
            else:
                self.active_effect = ActiveEffect(kind)

    # ── Drawing ───────────────────────────────

    def draw(self):
        play_w = PLAY_AREA_W   # pre-computed: GRID_COLS * CELL_SIZE

        # Background — play area only (sidebar drawn separately below)
        pygame.draw.rect(self.surface, DARK_GRAY, (0, 0, play_w, WINDOW_HEIGHT))

        # Grid overlay
        if self.grid_overlay:
            for c in range(GRID_COLS + 1):
                x = c * CELL_SIZE
                pygame.draw.line(self.surface, (45, 45, 45), (x, 0), (x, WINDOW_HEIGHT))
            for r in range(GRID_ROWS + 1):
                y = r * CELL_SIZE
                pygame.draw.line(self.surface, (45, 45, 45), (0, y), (play_w, y))

        # Obstacles
        for (c, r) in self.obstacles:
            rect = cell_rect(c, r)
            pygame.draw.rect(self.surface, BROWN, rect)
            pygame.draw.rect(self.surface, BLACK, rect, 1)

        # Foods
        for food in self.foods:
            food.draw(self.surface)

        # Power-up on field
        if self.powerup:
            self.powerup.draw(self.surface)

        # Snake body
        for i, (c, r) in enumerate(self.snake):
            rect = cell_rect(c, r)
            color = self.snake_color if i > 0 else tuple(min(255, v + 60) for v in self.snake_color)
            pygame.draw.rect(self.surface, color, rect.inflate(-2, -2), border_radius=5)

        # ── Sidebar ───────────────────────────
        sidebar_x = play_w
        pygame.draw.rect(self.surface, (20, 20, 20), (sidebar_x, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.surface, GRAY, (sidebar_x, 0), (sidebar_x, WINDOW_HEIGHT), 2)

        def sb_text(text, y, color=LIGHT_GRAY, font=None):
            f = font or self.font_sm
            surf = f.render(text, True, color)
            self.surface.blit(surf, (sidebar_x + 10, y))

        y = 15
        sb_text("SCORE", y, LIGHT_GRAY);          y += 18
        sb_text(str(self.score), y, YELLOW, self.font_md); y += 30
        sb_text("LEVEL", y, LIGHT_GRAY);           y += 18
        sb_text(str(self.level), y, CYAN, self.font_md);   y += 30
        sb_text("BEST", y, LIGHT_GRAY);             y += 18
        best = max(self.personal_best, self.score)
        sb_text(str(best), y, GREEN, self.font_md);         y += 35

        # Active effect
        if self.active_effect and not self.active_effect.expired:
            effect_color = POWERUP_COLORS.get(self.active_effect.kind, WHITE)
            sb_text("EFFECT", y, LIGHT_GRAY);       y += 18
            sb_text(self.active_effect.kind.upper(), y, effect_color, self.font_md); y += 20
            sb_text(f"{self.active_effect.remaining_sec:.1f}s", y, effect_color); y += 25
        elif self.shield_ready:
            sb_text("SHIELD", y, PURPLE, self.font_md); y += 25

        # Legend
        y = WINDOW_HEIGHT - 150
        sb_text("— FOOD —", y, GRAY);              y += 20
        sb_text("■ Normal +10", y, GREEN);          y += 16
        sb_text("■ Bonus  +25", y, YELLOW);         y += 16
        sb_text("■ Timed  +15", y, ORANGE);         y += 16
        sb_text("✕ Poison -2s", y, DARK_RED);       y += 16

    # ── Public accessors ──────────────────────

    @property
    def result(self) -> dict:
        return {
            "score": self.score,
            "level_reached": self.level,
        }