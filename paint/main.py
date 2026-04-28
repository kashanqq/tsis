import pygame
import sys
import math
import datetime

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint - Extended")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)

COLORS = [BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE]

# Canvas surface to draw persistently
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# UI Parameters
UI_HEIGHT = 100

# Tools and Sizes
tools = ["pen", "line", "eraser", "fill", "text", "rect", "sqr", "circ", "rtri", "eqtri", "rhomb"]
brush_sizes = {"S(1)": 2, "M(2)": 5, "L(3)": 10}

# Current State
current_color = BLACK
current_tool = "pen"
current_size = brush_sizes["S(1)"]

font = pygame.font.SysFont("Verdana", 14)
text_font = pygame.font.SysFont("Verdana", 24)

# Text Tool state
typing_text = False
current_text = ""
text_pos = (0, 0)

def draw_ui():
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, UI_HEIGHT))
    
    # Draw tools buttons
    tool_x = 10
    for t in tools:
        color = DARK_GRAY if current_tool == t else (220, 220, 220)
        btn_rect = pygame.Rect(tool_x, 10, 65, 35)
        pygame.draw.rect(screen, color, btn_rect)
        pygame.draw.rect(screen, BLACK, btn_rect, 2)
        text = font.render(t, True, BLACK)
        # Center text roughly
        text_rect = text.get_rect(center=btn_rect.center)
        screen.blit(text, text_rect)
        tool_x += 70

    # Draw color buttons
    color_x = 10
    for c in COLORS:
        btn_rect = pygame.Rect(color_x, 55, 35, 35)
        pygame.draw.rect(screen, c, btn_rect)
        if current_color == c:
            pygame.draw.rect(screen, BLACK, btn_rect, 3)
        else:
            pygame.draw.rect(screen, BLACK, btn_rect, 1)
        color_x += 45

    # Draw brush size buttons
    size_x = color_x + 20
    for s_name, s_val in brush_sizes.items():
        color = DARK_GRAY if current_size == s_val else (220, 220, 220)
        btn_rect = pygame.Rect(size_x, 55, 65, 35)
        pygame.draw.rect(screen, color, btn_rect)
        pygame.draw.rect(screen, BLACK, btn_rect, 2)
        text = font.render(s_name, True, BLACK)
        text_rect = text.get_rect(center=btn_rect.center)
        screen.blit(text, text_rect)
        size_x += 75

    # Draw hint
    hint_text = font.render("Ctrl+S: Save as PNG", True, BLACK)
    screen.blit(hint_text, (size_x + 20, 62))


def handle_ui_click(pos):
    global current_tool, current_color, current_size
    x, y = pos
    if y <= UI_HEIGHT:
        # Check tool click
        tool_x = 10
        for t in tools:
            if tool_x <= x <= tool_x + 65 and 10 <= y <= 45:
                current_tool = t
                return True
            tool_x += 70
        
        # Check color click
        color_x = 10
        for c in COLORS:
            if color_x <= x <= color_x + 35 and 55 <= y <= 90:
                current_color = c
                return True
            color_x += 45
            
        # Check size click
        size_x = color_x + 20
        for s_name, s_val in brush_sizes.items():
            if size_x <= x <= size_x + 65 and 55 <= y <= 90:
                current_size = s_val
                return True
            size_x += 75
            
        return True # clicked in UI area but not on a specific button
    return False

def draw_shape(surface, tool, color, start_pos, end_pos, width):
    x1, y1 = start_pos
    x2, y2 = end_pos
    if tool == "rect":
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(surface, color, rect, width)
    elif tool == "sqr":
        side = max(abs(x2 - x1), abs(y2 - y1))
        rx = x1 + side if x2 > x1 else x1 - side
        ry = y1 + side if y2 > y1 else y1 - side
        rect = pygame.Rect(min(x1, rx), min(y1, ry), side, side)
        pygame.draw.rect(surface, color, rect, width)
    elif tool == "circ":
        dist = math.hypot(x2 - x1, y2 - y1)
        pygame.draw.circle(surface, color, start_pos, int(dist), width)
    elif tool == "rtri":
        points = [(x1, y1), (x1, y2), (x2, y2)]
        if len(set(points)) == 3: # valid polygon
            pygame.draw.polygon(surface, color, points, width)
    elif tool == "eqtri":
        mid_x = (x1 + x2) / 2
        points = [(mid_x, y1), (x1, y2), (x2, y2)]
        if len(set(points)) == 3:
            pygame.draw.polygon(surface, color, points, width)
    elif tool == "rhomb":
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        points = [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
        if len(set(points)) >= 3:
            pygame.draw.polygon(surface, color, points, width)
    elif tool == "line":
        pygame.draw.line(surface, color, start_pos, end_pos, width * 2)

def flood_fill(surface, x, y, fill_color):
    target_color = surface.get_at((x, y))
    if target_color == fill_color:
        return

    width, height = surface.get_size()
    pixel_array = pygame.PixelArray(surface)
    
    target_color_mapped = surface.map_rgb(target_color)
    fill_color_mapped = surface.map_rgb(fill_color)
    
    q = [(x, y)]
    
    while q:
        cx, cy = q.pop()
        if pixel_array[cx, cy] == target_color_mapped:
            left_x = cx
            while left_x > 0 and pixel_array[left_x - 1, cy] == target_color_mapped:
                left_x -= 1
            
            right_x = cx
            while right_x < width - 1 and pixel_array[right_x + 1, cy] == target_color_mapped:
                right_x += 1
                
            for i in range(left_x, right_x + 1):
                pixel_array[i, cy] = fill_color_mapped
                if cy > 0 and pixel_array[i, cy - 1] == target_color_mapped:
                    q.append((i, cy - 1))
                if cy < height - 1 and pixel_array[i, cy + 1] == target_color_mapped:
                    q.append((i, cy + 1))
                    
    pixel_array.close()


def main():
    global current_tool, current_color, current_size
    global typing_text, current_text, text_pos

    clock = pygame.time.Clock()
    drawing = False
    start_pos = None
    last_pos = None

    while True:
        screen.blit(canvas, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if typing_text:
                    if event.key == pygame.K_RETURN:
                        # commit text
                        txt_surf = text_font.render(current_text, True, current_color)
                        canvas.blit(txt_surf, text_pos)
                        typing_text = False
                        current_text = ""
                    elif event.key == pygame.K_ESCAPE:
                        typing_text = False
                        current_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        current_text = current_text[:-1]
                    else:
                        current_text += event.unicode
                else:
                    if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        fname = f"canvas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        pygame.image.save(canvas, fname)
                        print(f"Saved to {fname}")
                    elif event.key == pygame.K_1:
                        current_size = brush_sizes["S(1)"]
                    elif event.key == pygame.K_2:
                        current_size = brush_sizes["M(2)"]
                    elif event.key == pygame.K_3:
                        current_size = brush_sizes["L(3)"]

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # if we were typing, commit if clicking elsewhere
                    if typing_text:
                        if current_text:
                            txt_surf = text_font.render(current_text, True, current_color)
                            canvas.blit(txt_surf, text_pos)
                        typing_text = False
                        current_text = ""

                    if not handle_ui_click(event.pos):
                        if event.pos[1] > UI_HEIGHT:
                            if current_tool == "text":
                                typing_text = True
                                text_pos = event.pos
                                current_text = ""
                            elif current_tool == "fill":
                                flood_fill(canvas, event.pos[0], event.pos[1], current_color)
                            else:
                                drawing = True
                                start_pos = event.pos
                                last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    drawing = False
                    end_pos = event.pos
                    if current_tool not in ["pen", "eraser"]:
                        draw_shape(canvas, current_tool, current_color, start_pos, end_pos, current_size)

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    if current_tool == "pen":
                        pygame.draw.line(canvas, current_color, last_pos, event.pos, current_size * 2)
                        pygame.draw.circle(canvas, current_color, event.pos, current_size)
                        last_pos = event.pos
                    elif current_tool == "eraser":
                        pygame.draw.line(canvas, WHITE, last_pos, event.pos, current_size * 2)
                        pygame.draw.circle(canvas, WHITE, event.pos, current_size)
                        last_pos = event.pos

        # Real-time preview for shapes
        if drawing and current_tool not in ["pen", "eraser"]:
            mouse_pos = pygame.mouse.get_pos()
            draw_shape(screen, current_tool, current_color, start_pos, mouse_pos, current_size)

        # Real-time preview for text
        if typing_text:
            # Blinking cursor simulation could be added, but simple '|' is fine
            txt_surf = text_font.render(current_text + "|", True, current_color)
            screen.blit(txt_surf, text_pos)

        # Draw UI on top of everything
        draw_ui()

        pygame.display.flip()
        clock.tick(120)

if __name__ == "__main__":
    main()
