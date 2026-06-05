import pygame
import cv2
import sys
import random
import json
import os
from fruit import Fruit
from hand_tracking import HandTracker

# ── Init ──────────────────────────────────────────────
pygame.init()
info   = pygame.display.Info()
WIDTH  = info.current_w
HEIGHT = info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Happy Harvest")
clock  = pygame.time.Clock()

# ── Fonts ─────────────────────────────────────────────
font_large  = pygame.font.SysFont("Arial", 80,  bold=True)
font_huge   = pygame.font.SysFont("Arial", 100, bold=True)
font_medium = pygame.font.SysFont("Arial", 52,  bold=True)
font_small  = pygame.font.SysFont("Arial", 38)
font_tiny   = pygame.font.SysFont("Arial", 28)

# ── Assets ────────────────────────────────────────────
cat_img = pygame.transform.scale(
    pygame.image.load("assets/Cat.jpg").convert(), (280, 280))

def make_heart_surf(color, size=50):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    r = size // 4
    pygame.draw.circle(s, color, (size//4,   size//4), r)
    pygame.draw.circle(s, color, (3*size//4, size//4), r)
    pts = [(0, size//3), (size//2, size), (size, size//3)]
    pygame.draw.polygon(s, color, pts)
    return s

heart_on  = make_heart_surf((255, 60,  60))
heart_off = make_heart_surf((80,  80,  80))

# ── High score ────────────────────────────────────────
SCORE_FILE = "highscore.json"

def load_high_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE) as f:
            return json.load(f).get("high_score", 0)
    return 0

def save_high_score(score):
    current = load_high_score()
    if score > current:
        with open(SCORE_FILE, "w") as f:
            json.dump({"high_score": score}, f)

# ── Webcam ────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ── Hand Tracker ──────────────────────────────────────
tracker = HandTracker(WIDTH, HEIGHT)

# ── Fruit config ──────────────────────────────────────
APPLE_PATH      = "assets/Apple.png"
WATERMELON_PATH = "assets/Watermellon.png"
PINEAPPLE_PATH  = "assets/Pineapple.png"
WORM_PATH       = "assets/Worm.png"

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

# ── Constants ─────────────────────────────────────────
MAX_LIVES   = 3
MAX_FRUITS  = 8
SPAWN_DELAY = 35
BATCH_SPAWN = 3

# ── Game states ───────────────────────────────────────
STATE_SPLASH   = "splash"
STATE_PLAYING  = "playing"
STATE_GAMEOVER = "gameover"

# ── Popups ────────────────────────────────────────────
popups = []

def add_popup(text, x, y, color, big=False):
    popups.append({
        "text": text, "x": x, "y": y,
        "alpha": 255, "color": color, "big": big
    })

# ── Segment collision ─────────────────────────────────
def segment_hits_fruit(p1, p2, fruit):
    fx, fy, fs = fruit.x, fruit.y, fruit.size
    pad  = 20
    rect = pygame.Rect(fx - pad, fy - pad, fs + pad*2, fs + pad*2)
    if rect.collidepoint(p1) or rect.collidepoint(p2):
        return True
    x1, y1 = p1
    x2, y2 = p2

    def cross(ox, oy, ax, ay, bx, by):
        return (ax-ox)*(by-oy) - (ay-oy)*(bx-ox)

    def seg_int(ax, ay, bx, by, cx, cy, dx, dy):
        d1 = cross(cx,cy,dx,dy,ax,ay)
        d2 = cross(cx,cy,dx,dy,bx,by)
        d3 = cross(ax,ay,bx,by,cx,cy)
        d4 = cross(ax,ay,bx,by,dx,dy)
        return (((d1>0 and d2<0) or (d1<0 and d2>0)) and
                ((d3>0 and d4<0) or (d3<0 and d4>0)))

    for ex1,ey1,ex2,ey2 in [
        (rect.left,  rect.top,    rect.right, rect.top),
        (rect.right, rect.top,    rect.right, rect.bottom),
        (rect.right, rect.bottom, rect.left,  rect.bottom),
        (rect.left,  rect.bottom, rect.left,  rect.top),
    ]:
        if seg_int(x1,y1,x2,y2,ex1,ey1,ex2,ey2):
            return True
    return False

# ── Helpers ───────────────────────────────────────────
def draw_text_shadow(surface, text, font, color, x, y, shadow=(0,0,0)):
    surface.blit(font.render(text, True, shadow), (x+3, y+3))
    surface.blit(font.render(text, True, color),  (x,   y))

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
        "score":       0,
        "lives":       MAX_LIVES,
        "fruits":      fruits,
        "spawn_timer": 0,
        "batch_timer": 0,
        "game_over":   False,
    }

# ── Screens ───────────────────────────────────────────
def draw_splash(bg):
    screen.blit(bg, (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    title = font_huge.render("Happy Harvest", True, (0, 0, 0))
    screen.blit(title, (WIDTH//2 - title.get_width()//2 + 3,
                         HEIGHT//2 - 230 + 3))
    title = font_huge.render("Happy Harvest", True, (255, 220, 50))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 230))

    hs = load_high_score()
    draw_text_shadow(screen, f"Best Score: {hs}",
                     font_medium, (100, 255, 180),
                     WIDTH//2 - 160, HEIGHT//2 - 60)

    alpha  = int(180 + 75 * abs(pygame.time.get_ticks() % 1000 / 500 - 1))
    prompt = font_medium.render("Raise your finger to start!", True, (255, 255, 255))
    prompt.set_alpha(alpha)
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 60))

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
    hs = load_high_score()
    draw_text_shadow(screen, f"Best Score:  {hs}",
                     font_small, (100, 255, 180),
                     WIDTH//2 - 160, HEIGHT//2 + 130)
    draw_text_shadow(screen, "Press  R  to restart",
                     font_small, (220, 220, 220),
                     WIDTH//2 - 160, HEIGHT//2 + 185)
    draw_text_shadow(screen, "Press  ESC  to quit",
                     font_small, (180, 180, 180),
                     WIDTH//2 - 150, HEIGHT//2 + 240)

def draw_hud(state):
    draw_text_shadow(screen, f"Score: {state['score']}",
                     font_medium, (255, 240, 100), 20, 20)
    hs = load_high_score()
    draw_text_shadow(screen, f"Best: {hs}",
                     font_tiny, (180, 255, 180), 20, 80)
    for i in range(MAX_LIVES):
        img = heart_on if i < state["lives"] else heart_off
        screen.blit(img, (WIDTH//2 - (MAX_LIVES*60)//2 + i*60, 18))

# ── Main state ────────────────────────────────────────
game_state     = STATE_SPLASH
state          = reset_game()
trail          = []
splash_started = False
start_timer    = 0

# ── Main loop ─────────────────────────────────────────
while True:

    ret, frame = cap.read()
    if not ret:
        continue

    frame     = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_srf = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    bg        = pygame.transform.scale(frame_srf, (WIDTH, HEIGHT))

    finger_pos = tracker.get_index_tip(frame)
    if finger_pos:
        trail.append(finger_pos)
        if len(trail) > 18:
            trail.pop(0)
    else:
        trail.clear()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release(); pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                cap.release(); pygame.quit(); sys.exit()
            if game_state == STATE_GAMEOVER and event.key == pygame.K_r:
                state          = reset_game()
                game_state     = STATE_SPLASH
                trail.clear()
                popups.clear()

    # ── SPLASH ────────────────────────────────────────
    if game_state == STATE_SPLASH:
        draw_splash(bg)
        if finger_pos:
            if not splash_started:
                splash_started = True
                start_timer    = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - start_timer > 1500:
                game_state     = STATE_PLAYING
                splash_started = False
        else:
            splash_started = False

    # ── PLAYING ───────────────────────────────────────
    elif game_state == STATE_PLAYING:
        screen.blit(bg, (0, 0))

        state["spawn_timer"] += 1
        if (state["spawn_timer"] >= SPAWN_DELAY and
                len(state["fruits"]) < MAX_FRUITS):
            state["fruits"].append(make_fruit())
            state["spawn_timer"] = 0

        state["batch_timer"] += 1
        if state["batch_timer"] >= 90:
            count = BATCH_SPAWN - max(0, len(state["fruits"]) - 2)
            for _ in range(max(1, count)):
                if len(state["fruits"]) < MAX_FRUITS:
                    f   = make_fruit()
                    f.x = random.randint(100, WIDTH - 100)
                    state["fruits"].append(f)
            state["batch_timer"] = 0

        for fruit in state["fruits"]:
            fruit.update()
            fruit.draw(screen)

            if not fruit.sliced:
                hit = fruit.is_hit(finger_pos)
                if not hit and len(trail) >= 2:
                    for i in range(len(trail) - 1):
                        if segment_hits_fruit(trail[i], trail[i+1], fruit):
                            hit = True
                            break

                if hit:
                    fruit.sliced = True
                    if fruit.is_worm:
                        state["lives"] -= 1
                        add_popup("-1 life", int(fruit.x), int(fruit.y),
                                  (255, 80, 80), big=True)
                        if state["lives"] <= 0:
                            save_high_score(state["score"])
                            game_state = STATE_GAMEOVER
                    else:
                        state["score"] += 1
                        add_popup("+1", int(fruit.x), int(fruit.y),
                                  (100, 255, 100))

            if fruit.is_off_screen() and not fruit.sliced and not fruit.missed:
                fruit.missed = True
                if not fruit.is_worm:
                    state["score"] = max(0, state["score"] - 1)
                    add_popup("-1", int(fruit.x), HEIGHT - 80, (255, 200, 80))

        state["fruits"] = [f for f in state["fruits"]
                           if not f.is_off_screen() and not f.sliced]

        draw_hud(state)

        if len(trail) > 2:
            for i in range(1, len(trail)):
                pygame.draw.line(screen, (255,255,255),
                                 trail[i-1], trail[i], max(1, i//3))

        if finger_pos:
            pygame.draw.circle(screen, (255,120,0), finger_pos, 16)
            pygame.draw.circle(screen, (255,255,255), finger_pos, 16, 3)

        for p in popups:
            f = font_medium if p["big"] else font_small
            s = f.render(p["text"], True, p["color"])
            s.set_alpha(p["alpha"])
            screen.blit(s, (p["x"], p["y"]))
            p["y"]     -= 2
            p["alpha"] -= 5
        popups[:] = [p for p in popups if p["alpha"] > 0]

    # ── GAME OVER ─────────────────────────────────────
    elif game_state == STATE_GAMEOVER:
        screen.blit(bg, (0, 0))
        draw_game_over(state["score"])

    pygame.display.flip()
    clock.tick(30)