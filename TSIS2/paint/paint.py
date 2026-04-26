import pygame
import sys
import math
from datetime import datetime
from tools import (
    BRUSH_SIZES,
    draw_rect, draw_square, draw_circle,
    draw_right_triangle, draw_equilateral_triangle, draw_rhombus,
    draw_line, flood_fill, render_text_preview,
)
WINDOW_W, WINDOW_H = 1100, 700
TOOLBAR_W = 160
CANVAS_X = TOOLBAR_W
CANVAS_Y = 0
CANVAS_W = WINDOW_W - TOOLBAR_W
CANVAS_H = WINDOW_H
BG_COLOR = (30, 30, 38)
TOOLBAR_BG = (22, 22, 30)
PANEL_BORDER = (55, 55, 70)
ACCENT = (100, 160, 255)
TEXT_COLOR = (220, 220, 235)
DIM_TEXT = (120, 120, 140)
CANVAS_BG = (255, 255, 255)
BTN_NORMAL = (40, 40, 52)
BTN_HOVER = (55, 55, 72)
BTN_ACTIVE = (70, 110, 200)
SIZE_BTN_NORMAL = (40, 40, 52)
SIZE_BTN_ACTIVE = (200, 130, 60)
PALETTE = [
    (0,0,0),(255,255,255),(192,192,192),(128,128,128),
    (255,0,0),(128,0,0),(255,165,0),(128,80,0),
    (255,255,0),(128,128,0),(0,255,0),(0,128,0),
    (0,255,255),(0,128,128),(0,0,255),(0,0,128),
    (255,0,255),(128,0,128),(255,105,180),(139,69,19),
]
TOOLS = [
    ("Pencil","P"),("Line","L"),("Rect","R"),("Square","Q"),
    ("Circle","C"),("R.Tri","T"),("Eq.Tri","E"),("Rhombus","H"),
    ("Fill","F"),("Eraser","X"),("Text","A"),
]
class Button:
    def __init__(self, rect, label, shortcut=""):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.shortcut = shortcut
        self.active = False
        self.hovered = False
    def draw(self, surface, font, small_font):
        bg = BTN_ACTIVE if self.active else (BTN_HOVER if self.hovered else BTN_NORMAL)
        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, 1, border_radius=6)
        lbl = font.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, lbl.get_rect(center=self.rect.center).move(0, -4 if self.shortcut else 0))
        if self.shortcut:
            sc = small_font.render(f"[{self.shortcut}]", True, DIM_TEXT)
            surface.blit(sc, sc.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 4))
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Paint — Extended")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui", 13, bold=True)
    sm_font = pygame.font.SysFont("segoeui", 11)
    txt_font = pygame.font.SysFont("segoeui", 22)
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(CANVAS_BG)
    active_tool = "Pencil"
    active_color = (0, 0, 0)
    brush_idx = 1
    drawing = False
    prev_pos = None
    shape_start = None
    canvas_snap = None
    text_active = False
    text_pos = (0, 0)
    text_buffer = ""
    tool_buttons = []
    for i, (name, sc) in enumerate(TOOLS):
        row = i // 2
        col = i % 2
        bx = 8 + col * 74
        by = 50 + row * 46
        tool_buttons.append(Button((bx, by, 70, 40), name, sc))
    brush_buttons = []
    for i, (k, v) in enumerate(BRUSH_SIZES.items()):
        bx = 8 + i * 48
        brush_buttons.append(Button((bx, WINDOW_H - 80, 44, 32), f"{'S' if k==1 else 'M' if k==2 else 'L'}", str(k)))
    PAL_COLS = 4
    PAL_SIZE = 28
    PAL_PAD = 4
    PAL_START_Y = WINDOW_H - 270
    pal_rects = []
    for idx, col in enumerate(PALETTE):
        r = idx // PAL_COLS
        c = idx % PAL_COLS
        rx = 10 + c * (PAL_SIZE + PAL_PAD)
        ry = PAL_START_Y + r * (PAL_SIZE + PAL_PAD)
        pal_rects.append((pygame.Rect(rx, ry, PAL_SIZE, PAL_SIZE), col))
    def draw_toolbar():
        pygame.draw.rect(screen, TOOLBAR_BG, (0, 0, TOOLBAR_W, WINDOW_H))
        pygame.draw.line(screen, PANEL_BORDER, (TOOLBAR_W, 0), (TOOLBAR_W, WINDOW_H), 1)
        title = font.render("🖌 PAINT", True, ACCENT)
        screen.blit(title, (12, 12))
        for btn in tool_buttons:
            btn.active = (btn.label == active_tool)
            btn.draw(screen, font, sm_font)
        lbl = sm_font.render("BRUSH SIZE", True, DIM_TEXT)
        screen.blit(lbl, (8, WINDOW_H - 92))
        for i, btn in enumerate(brush_buttons):
            btn.active = (i + 1 == brush_idx)
            btn.draw(screen, font, sm_font)
        lbl2 = sm_font.render("COLOR", True, DIM_TEXT)
        screen.blit(lbl2, (8, PAL_START_Y - 18))
        for rect, col in pal_rects:
            pygame.draw.rect(screen, col, rect, border_radius=4)
            if col == active_color:
                pygame.draw.rect(screen, ACCENT, rect, 2, border_radius=4)
            else:
                pygame.draw.rect(screen, PANEL_BORDER, rect, 1, border_radius=4)
        sw = pygame.Rect(8, WINDOW_H - 50, 60, 34)
        pygame.draw.rect(screen, active_color, sw, border_radius=6)
        pygame.draw.rect(screen, PANEL_BORDER, sw, 1, border_radius=6)
        lbl3 = sm_font.render("Active", True, DIM_TEXT)
        screen.blit(lbl3, (76, WINDOW_H - 40))
        hint = sm_font.render("Ctrl+S = Save", True, DIM_TEXT)
        screen.blit(hint, (8, WINDOW_H - 12))
    def to_canvas(pos):
        return (pos[0] - CANVAS_X, pos[1] - CANVAS_Y)
    def in_canvas(pos):
        return CANVAS_X <= pos[0] < CANVAS_X + CANVAS_W and 0 <= pos[1] < CANVAS_H
    def save_canvas():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = f"canvas_{ts}.png"
        pygame.image.save(canvas, fn)
        pygame.display.set_caption(f"Paint — Saved: {fn}")
    def draw_shape(surf, tool, start, end, color, size):
        if tool == "Rect":
            draw_rect(surf, color, start, end, size)
        elif tool == "Square":
            draw_square(surf, color, start, end, size)
        elif tool == "Circle":
            draw_circle(surf, color, start, end, size)
        elif tool == "R.Tri":
            draw_right_triangle(surf, color, start, end, size)
        elif tool == "Eq.Tri":
            draw_equilateral_triangle(surf, color, start, end, size)
        elif tool == "Rhombus":
            draw_rhombus(surf, color, start, end, size)
        elif tool == "Line":
            draw_line(surf, color, start, end, size)
    SHAPE_TOOLS = {"Rect","Square","Circle","R.Tri","Eq.Tri","Rhombus","Line"}
    running = True
    while running:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        brush_px = BRUSH_SIZES[brush_idx]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    save_canvas()
                    continue
                if event.key == pygame.K_1:
                    brush_idx = 1
                elif event.key == pygame.K_2:
                    brush_idx = 2
                elif event.key == pygame.K_3:
                    brush_idx = 3
                KEY_TOOL = {
                    pygame.K_p:"Pencil",pygame.K_l:"Line",
                    pygame.K_r:"Rect",pygame.K_q:"Square",
                    pygame.K_c:"Circle",pygame.K_t:"R.Tri",
                    pygame.K_e:"Eq.Tri",pygame.K_h:"Rhombus",
                    pygame.K_f:"Fill",pygame.K_x:"Eraser",
                    pygame.K_a:"Text",
                }
                if event.key in KEY_TOOL and not text_active:
                    active_tool = KEY_TOOL[event.key]
                if text_active:
                    if event.key == pygame.K_RETURN:
                        img = txt_font.render(text_buffer, True, active_color)
                        canvas.blit(img, text_pos)
                        text_active = False
                        text_buffer = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handled = False
                for btn in tool_buttons:
                    if btn.handle_event(event):
                        active_tool = btn.label
                        text_active = False
                        text_buffer = ""
                        handled = True
                for i, btn in enumerate(brush_buttons):
                    if btn.handle_event(event):
                        brush_idx = i + 1
                        handled = True
                for rect, col in pal_rects:
                    if rect.collidepoint(event.pos):
                        active_color = col
                        handled = True
                if handled:
                    continue
                if in_canvas(event.pos):
                    cp = to_canvas(event.pos)
                    if active_tool == "Fill":
                        flood_fill(canvas, cp, active_color)
                    elif active_tool == "Text":
                        text_active = True
                        text_pos = cp
                        text_buffer = ""
                    elif active_tool in ["Pencil","Eraser"]:
                        drawing = True
                        prev_pos = cp
                    elif active_tool in SHAPE_TOOLS:
                        drawing = True
                        shape_start = cp
                        canvas_snap = canvas.copy()
            if event.type == pygame.MOUSEMOTION:
                for btn in tool_buttons:
                    btn.handle_event(event)
                for btn in brush_buttons:
                    btn.handle_event(event)
                if drawing and in_canvas(event.pos):
                    cp = to_canvas(event.pos)
                    if active_tool == "Pencil":
                        if prev_pos:
                            pygame.draw.line(canvas, active_color, prev_pos, cp, brush_px)
                        prev_pos = cp
                    elif active_tool == "Eraser":
                        er = max(brush_px, 8)
                        pygame.draw.circle(canvas, CANVAS_BG, cp, er)
                        prev_pos = cp
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing:
                    if in_canvas(event.pos):
                        cp = to_canvas(event.pos)
                        if active_tool in SHAPE_TOOLS and shape_start:
                            canvas.blit(canvas_snap, (0, 0))
                            draw_shape(canvas, active_tool, shape_start, cp, active_color, brush_px)
                    drawing = False
                    prev_pos = None
                    shape_start = None
                    canvas_snap = None
        screen.fill(BG_COLOR)
        display_canvas = canvas.copy()
        if drawing and active_tool in SHAPE_TOOLS and shape_start:
            cp = to_canvas(mouse_pos)
            if canvas_snap:
                display_canvas.blit(canvas_snap, (0, 0))
            draw_shape(display_canvas, active_tool, shape_start, cp, active_color, brush_px)
        if text_active:
            render_text_preview(display_canvas, txt_font, text_buffer, text_pos, active_color)
        screen.blit(display_canvas, (CANVAS_X, CANVAS_Y))
        if active_tool == "Eraser" and in_canvas(mouse_pos):
            er = max(brush_px, 8)
            pygame.draw.circle(screen, (180,180,180), mouse_pos, er, 1)
        draw_toolbar()
        tool_hint = f"Tool: {active_tool}  |  Size: {brush_px}px  |  Color: RGB{active_color}"
        if text_active:
            tool_hint += "  |  TEXT MODE: type then Enter"
        hint_surf = sm_font.render(tool_hint, True, DIM_TEXT)
        screen.blit(hint_surf, (CANVAS_X + 8, WINDOW_H - 16))
        pygame.display.flip()
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()