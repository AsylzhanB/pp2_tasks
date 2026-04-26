import pygame
import math
from collections import deque

BRUSH_SIZES = {1: 2, 2: 5, 3: 10}

def draw_rect(surface, color, start, end, size, filled=False):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    if w == 0 or h == 0:
        return
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, color, rect, 0 if filled else size)

def draw_square(surface, color, start, end, size, filled=False):
    side = min(abs(end[0] - start[0]), abs(end[1] - start[1]))
    dx = side if end[0] >= start[0] else -side
    dy = side if end[1] >= start[1] else -side
    draw_rect(surface, color, start, (start[0] + dx, start[1] + dy), size, filled)

def draw_circle(surface, color, start, end, size, filled=False):
    cx = (start[0] + end[0]) // 2
    cy = (start[1] + end[1]) // 2
    r = int(math.hypot(end[0] - start[0], end[1] - start[1]) / 2)
    if r == 0:
        return
    pygame.draw.circle(surface, color, (cx, cy), r, 0 if filled else size)

def draw_right_triangle(surface, color, start, end, size, filled=False):
    p1 = start
    p2 = (start[0], end[1])
    p3 = end
    pygame.draw.polygon(surface, color, [p1, p2, p3], 0 if filled else size)

def draw_equilateral_triangle(surface, color, start, end, size, filled=False):
    base = abs(end[0] - start[0])
    if base == 0:
        return
    x1 = min(start[0], end[0])
    x2 = max(start[0], end[0])
    y_base = end[1]
    height = int(base * math.sqrt(3) / 2)
    p1 = (x1, y_base)
    p2 = (x2, y_base)
    p3 = ((x1 + x2) // 2, y_base - height)
    pygame.draw.polygon(surface, color, [p1, p2, p3], 0 if filled else size)

def draw_rhombus(surface, color, start, end, size, filled=False):
    cx = (start[0] + end[0]) // 2
    cy = (start[1] + end[1]) // 2
    hw = abs(end[0] - start[0]) // 2
    hh = abs(end[1] - start[1]) // 2
    if hw == 0 or hh == 0:
        return
    points = [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]
    pygame.draw.polygon(surface, color, points, 0 if filled else size)

def draw_line(surface, color, start, end, size):
    pygame.draw.line(surface, color, start, end, size)

def flood_fill(surface, pos, fill_color):
    x, y = int(pos[0]), int(pos[1])
    w, h = surface.get_size()
    if x < 0 or x >= w or y < 0 or y >= h:
        return
    target_color = surface.get_at((x, y))
    if target_color == fill_color:
        return
    surface.lock()
    queue = deque()
    queue.append((x, y))
    visited = set()
    visited.add((x, y))
    while queue:
        cx, cy = queue.popleft()
        if surface.get_at((cx, cy)) != target_color:
            continue
        surface.set_at((cx, cy), fill_color)
        for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
    surface.unlock()

def render_text_preview(surface, font, text, pos, color):
    img = font.render(text + "|", True, color)
    surface.blit(img, pos)