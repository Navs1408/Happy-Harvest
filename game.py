import pygame
import cv2
import sys
import random
from fruit import Fruit
from hand_tracking import HandTracker

# ── Init ──────────────────────────────────────────────
pygame.init()
info = pygame.display.Info()
WIDTH  = info.current_w
HEIGHT = info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Happy Harvest 🫧🐞🍋")
clock = pygame.time.Clock()

# ── Fonts ─────────────────────────────────────────────
font_large  = pygame.font.SysFont("Arial", 80, bold=True)
font_medium = pygame.font.SysFont("Arial", 52, bold=True)
font_small  = pygame.font.SysFont("Arial", 38)

# ── Cat image ─────────────────────────────────────────
cat_img_raw = pygame.image.load("/Users/navya/HappyHarvest/Cat.jpg").convert()
cat_img = pygame.transform.scale(cat_img_raw, (280, 280))

# ── Webcam ────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ── Hand Tracker ──────────────────────────────────────
tracker = HandTracker(WIDTH, HEIGHT)

# ── Fruit paths ───────────────────────────────────────
APPLE_PATH      = "Apple.png"
WATERMELON_PATH = "Watermellon.png"
PINEAPPLE_PATH  = "Pineapple.png"
WORM_PATH       = "Worm.png"

FRUIT_CONFIG = [
    (APPLE_PATH,      False, 4),
    (WATERMELON_PATH, False, 4),
    (PINEAPPLE_PATH,  False, 4),
    (WORM_PATH,       True,  2),
]

FRUIT_POOL = []
for path, is_worm, weight in FRUIT_CONFIG:
    for _ in range(weight):
        FRUIT_POOL.append((path, is_worm))

# ── Config ────────────────────────────────────────────
MAX_WORMS   = 3
MAX_FRUITS  = 8
SPAWN_DELAY = 35
BATCH_SPAWN = 3

# ── Score popups ──────────────────────────────────────
popups = []

def add_popup(text, x, y, color):
    popups.append({"text": text, "x": x, "y": y, "alpha": 255, "color": color})

def make_fruit():
    path, is_worm = random.choice(FRUIT_POOL)
    return Fruit(path, WIDTH, HEIGHT, is_worm=is_worm)

def reset_game():
    fruits = []
    for _ in range(4):
        f = make_fruit()
        f.y = HEIGHT + random.randint(0, 200)
        fruits.append(f)
    return {
        "score":        0,
        "worms_sliced": 0,
        "fruits":       fruits,
        "spawn_timer":  0,
        "batch_timer":  0,
        "game_over":    False,
    }

state = reset_game()
trail = []

# ── Segment vs rect collision ─────────────────────────
def segment_hits_fruit(p1, p2, fruit):
    """Check if the line segment from p1 to p2 passes through the fruit rect."""
    fx, fy, fs = fruit.x, fruit.y, fruit.size
    pad = 20
    rect = pygame.Rect(fx - pad, fy - pad, fs + pad*2, fs + pad*2)

    # Check if either endpoint is inside
    if rect.collidepoint(p1) or rect.collidepoint(p2):
        return True

    # Check if segment intersects any edge of the rect
    x1, y1 = p1
    x2, y2 = p2

    def seg_intersects(ax, ay, bx, by, cx, cy, dx, dy):
        def cross(ox, oy, ax, ay, bx, by):
            return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)
        d1 = cross(cx, cy, dx, dy, ax, ay)
        d2 = cross(cx, cy, dx, dy, bx, by)
        d3 = cross(ax, ay, bx, by, cx, cy)
        d4 = cross(ax, ay, bx, by, dx, dy)
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        return False

    # Four edges of rect
    edges = [
        (rect.left,  rect.top,    rect.right, rect.top),
        (rect.right, rect.top,    rect.right, rect.bottom),
        (rect.right, rect.bottom, rect.left,  rect.bottom),
        (rect.left,  rect.bottom, rect.left,  rect.top),
    ]
    for ex1, ey1, ex2, ey2 in edges:
        if seg_intersects(x1, y1, x2, y2, ex1, ey1, ex2, ey2):
            return True
    return False

# ── Helpers ───────────────────────────────────────────
def draw_text_shadow(surface, text, font, color, x, y, shadow=(0,0,0)):
    surface.blit(font.render(text, True, shadow), (x+3, y+3))
    surface.blit(font.render(text, True, color),  (x,   y))

def draw_game_over(score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))
    draw_text_shadow(screen, "GAME OVER  :(",
                     font_large, (255, 60, 60),
                     WIDTH//2 - 320, HEIGHT//2 - 340)
    screen.blit(cat_img, (WIDTH//2 - 140, HEIGHT//2 - 240))
    draw_text_shadow(screen, f"Final Score: {score}",
                     font_medium, (255, 230, 80),
                     WIDTH//2 - 210, HEIGHT//2 + 60)
    draw_text_shadow(screen, "Press  R  to restart",
                     font_small, (220, 220, 220),
                     WIDTH//2 - 160, HEIGHT//2 + 150)
    draw_text_shadow(screen, "Press  ESC  to quit",
                     font_small, (180, 180, 180),
                     WIDTH//2 - 150, HEIGHT//2 + 210)

# ── Main loop ─────────────────────────────────────────
while True:

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    bg = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
    screen.blit(bg, (0, 0))

    finger_pos = tracker.get_index_tip(frame)
    if finger_pos:
        trail.append(finger_pos)
        if len(trail) > 18:
            trail.pop(0)
    else:
        trail.clear()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                cap.release()
                pygame.quit()
                sys.exit()
            if state["game_over"] and event.key == pygame.K_r:
                state = reset_game()
                trail.clear()
                popups.clear()

    if not state["game_over"]:

        # Spawn
        state["spawn_timer"] += 1
        if (state["spawn_timer"] >= SPAWN_DELAY and
                len(state["fruits"]) < MAX_FRUITS):
            state["fruits"].append(make_fruit())
            state["spawn_timer"] = 0

        # Batch spawn
        state["batch_timer"] += 1
        if state["batch_timer"] >= 90:
            count = BATCH_SPAWN - max(0, len(state["fruits"]) - 2)
            for _ in range(max(1, count)):
                if len(state["fruits"]) < MAX_FRUITS:
                    f = make_fruit()
                    f.x = random.randint(100, WIDTH - 100)
                    state["fruits"].append(f)
            state["batch_timer"] = 0

        # Update fruits
        for fruit in state["fruits"]:
            fruit.update()
            fruit.draw(screen)

            # Slice detection along entire trail segment
            if not fruit.sliced:
                hit = False
                # Check current point
                if fruit.is_hit(finger_pos):
                    hit = True
                # Check each segment of the trail for fast swipes
                if not hit and len(trail) >= 2:
                    for i in range(len(trail) - 1):
                        if segment_hits_fruit(trail[i], trail[i+1], fruit):
                            hit = True
                            break

                if hit:
                    fruit.sliced = True
                    if fruit.is_worm:
                        state["score"] = max(0, state["score"] - 1)
                        state["worms_sliced"] += 1
                        add_popup("-1 🐛", int(fruit.x), int(fruit.y), (255, 80, 80))
                        if state["worms_sliced"] >= MAX_WORMS:
                            state["game_over"] = True
                    else:
                        state["score"] += 1
                        add_popup("+1", int(fruit.x), int(fruit.y), (100, 255, 100))

            # Missed fruit
            if fruit.is_off_screen() and not fruit.sliced and not fruit.missed:
                fruit.missed = True
                if not fruit.is_worm:
                    state["score"] = max(0, state["score"] - 1)
                    add_popup("-1", int(fruit.x), HEIGHT - 80, (255, 200, 80))

        # Clean up
        state["fruits"] = [f for f in state["fruits"]
                           if not f.is_off_screen() and not f.sliced]

        # Score
        draw_text_shadow(screen, f"Score: {state['score']}",
                         font_medium, (255, 240, 100), 20, 20)

        # Worm counter
        w_color = (255, 80, 80) if state["worms_sliced"] > 0 else (180, 255, 180)
        draw_text_shadow(screen,
                         f"Worms: {state['worms_sliced']} / {MAX_WORMS}",
                         font_small, w_color, WIDTH - 300, 20)

        # Slice trail
        if len(trail) > 2:
            for i in range(1, len(trail)):
                pygame.draw.line(screen, (255, 255, 255),
                                 trail[i-1], trail[i], max(1, i//3))

        # Finger dot
        if finger_pos:
            pygame.draw.circle(screen, (255, 120, 0), finger_pos, 16)
            pygame.draw.circle(screen, (255, 255, 255), finger_pos, 16, 3)

        # Popups
        for p in popups:
            s = font_small.render(p["text"], True, p["color"])
            s.set_alpha(p["alpha"])
            screen.blit(s, (p["x"], p["y"]))
            p["y"]     -= 2
            p["alpha"] -= 6
        popups[:] = [p for p in popups if p["alpha"] > 0]

    else:
        draw_game_over(state["score"])

    pygame.display.flip()
    clock.tick(30)