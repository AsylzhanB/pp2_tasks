import pygame
import random
from Config import *

def cell_rect(col: int, row: int) -> pygame.Rect:
    return pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

def random_cell(exclude: set, cols: int = PLAY_AREA_COLS, rows: int = GRID_ROWS) -> tuple:
    attempts = 0
    while attempts < 2000:
        c = random.randint(0, cols - 1)
        r = random.randint(0, rows - 1)
        if (c, r) not in exclude:
            return (c, r)
        attempts += 1
    return None

class FoodItem:
    def __init__(self, pos: tuple, kind: str = "normal"):
        self.pos = pos
        self.kind = kind
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
            cx, cy = r.centerx, r.centery
            pygame.draw.line(surface, WHITE, (cx - 5, cy - 5), (cx + 5, cy + 5), 2)
            pygame.draw.line(surface, WHITE, (cx + 5, cy - 5), (cx - 5, cy + 5), 2)

class PowerUp:
    def __init__(self, pos: tuple, kind: str):
        self.pos = pos
        self.kind = kind
        self.spawn_time = pygame.time.get_ticks()
    @property
    def expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_FIELD_MS

    def draw(self, surface: pygame.Surface):
        color = POWERUP_COLORS.get(self.kind, WHITE)
        r = cell_rect(*self.pos)
        pygame.draw.rect(surface, color, r.inflate(-2, -2), border_radius=6)
        font = pygame.font.SysFont("consolas", 11, bold=True)
        label = self.kind[0].upper()
        txt = font.render(label, True, BLACK)
        surface.blit(txt, txt.get_rect(center=r.center))
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
class SnakeGame:
    def __init__(self, surface: pygame.Surface, snake_color, grid_overlay: bool, player_id: int, personal_best: int):
        self.surface = surface
        self.snake_color = snake_color
        self.grid_overlay = grid_overlay
        self.player_id = player_id
        self.personal_best = personal_best
        self.font_sm = pygame.font.SysFont("consolas", 14)
        self.font_md = pygame.font.SysFont("consolas", 18, bold=True)
        self._init_state()
    def _init_state(self):
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.game_over = False
        mid_col = PLAY_AREA_COLS // 2
        mid_row = GRID_ROWS // 2
        self.snake = [(mid_col, mid_row), (mid_col - 1, mid_row), (mid_col - 2, mid_row)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.obstacles: set = set()
        self.foods: list[FoodItem] = []
        self.powerup: PowerUp | None = None
        self.active_effect: ActiveEffect | None = None
        self.shield_ready = False
        self.current_speed = BASE_SPEED
        self._last_move_time = pygame.time.get_ticks()
        self._spawn_food()
    def _occupied(self) -> set:
        occ = set(self.snake) | self.obstacles
        for f in self.foods:
            occ.add(f.pos)
        if self.powerup:
            occ.add(self.powerup.pos)
        return occ
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
    def _add_obstacles(self):
        count = OBSTACLES_PER_LEVEL
        snake_set = set(self.snake)
        hcol, hrow = self.snake[0]
        safe = {(hcol + dc, hrow + dr) for dc in range(-3, 4) for dr in range(-3, 4)}
        attempts = 0
        added = 0
        while added < count and attempts < 500:
            pos = random_cell(self._occupied() | safe)
            if pos and pos not in self.obstacles and pos not in snake_set:
                self.obstacles.add(pos)
                added += 1
            attempts += 1
    def _spawn_food(self):
        while len(self.foods) < 2:
            occ = self._occupied()
            pos = random_cell(occ)
            if pos is None:
                break
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
    def _try_spawn_powerup(self):
        if self.powerup is not None:
            return
        if random.random() < POWERUP_SPAWN_CHANCE:
            pos = random_cell(self._occupied())
            if pos:
                kind = random.choice(["speed", "slow", "shield"])
                self.powerup = PowerUp(pos, kind)
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
    def update(self):
        if self.game_over:
            return
        now = pygame.time.get_ticks()
        self.foods = [f for f in self.foods if not f.expired]
        self._spawn_food()
        if self.powerup and self.powerup.expired:
            self.powerup = None
        if self.active_effect and self.active_effect.expired:
            self.active_effect = None
        if now - self._last_move_time < self._effective_speed():
            return
        self._last_move_time = now
        self.direction = self.next_direction
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        if not (0 <= new_head[0] < PLAY_AREA_COLS and 0 <= new_head[1] < GRID_ROWS):
            if self.shield_ready:
                self.shield_ready = False
                return
            self.game_over = True
            return
        if new_head in self.snake[:-1] or new_head in self.obstacles:
            if self.shield_ready:
                self.shield_ready = False
                return
            self.game_over = True
            return
        self.snake.insert(0, new_head)
        eaten_food = next((f for f in self.foods if f.pos == new_head), None)
        if eaten_food:
            self.foods.remove(eaten_food)
            if eaten_food.kind == "poison":
                for _ in range(2):
                    if len(self.snake) > 1:
                        self.snake.pop()
                if len(self.snake) <= 1:
                    self.game_over = True
                    return
            else:
                self.score += FOOD_POINTS.get(eaten_food.kind, 10)
                self.food_eaten += 1
                if self.food_eaten >= FOOD_PER_LEVEL:
                    self._advance_level()
                self._try_spawn_powerup()
        else:
            self.snake.pop()
        self._spawn_food()
        if self.powerup and self.powerup.pos == new_head:
            kind = self.powerup.kind
            self.powerup = None
            if kind == "shield":
                self.shield_ready = True
            else:
                self.active_effect = ActiveEffect(kind)
    def draw(self):
        play_w = PLAY_AREA_W
        pygame.draw.rect(self.surface, DARK_GRAY, (0, 0, play_w, WINDOW_HEIGHT))
        if self.grid_overlay:
            for c in range(GRID_COLS + 1):
                x = c * CELL_SIZE
                pygame.draw.line(self.surface, (45, 45, 45), (x, 0), (x, WINDOW_HEIGHT))
            for r in range(GRID_ROWS + 1):
                y = r * CELL_SIZE
                pygame.draw.line(self.surface, (45, 45, 45), (0, y), (play_w, y))
        for (c, r) in self.obstacles:
            rect = cell_rect(c, r)
            pygame.draw.rect(self.surface, BROWN, rect)
            pygame.draw.rect(self.surface, BLACK, rect, 1)
        for food in self.foods:
            food.draw(self.surface)
        if self.powerup:
            self.powerup.draw(self.surface)
        for i, (c, r) in enumerate(self.snake):
            rect = cell_rect(c, r)
            color = self.snake_color if i > 0 else tuple(min(255, v + 60) for v in self.snake_color)
            pygame.draw.rect(self.surface, color, rect.inflate(-2, -2), border_radius=5)
    @property
    def result(self) -> dict:
        return {"score": self.score, "level_reached": self.level}