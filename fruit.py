import pygame
import random

class Fruit:
    def __init__(self, image_path, screen_width, screen_height, is_worm=False):
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.is_worm = is_worm
        img  = pygame.image.load(image_path).convert_alpha()
        size = int(screen_width * 0.09)
        self.image = pygame.transform.scale(img, (size, size))
        self.size  = size
        self.reset()

    def reset(self):
        self.x       = random.randint(80, self.screen_width - 80)
        self.y       = self.screen_height + 20
        self.speed_x = random.uniform(-5, 5)
        self.speed_y = random.uniform(-28, -20)
        self.gravity = 0.55
        self.sliced  = False
        self.active  = True
        self.missed  = False

    def update(self):
        if not self.active:
            return
        self.x       += self.speed_x
        self.y       += self.speed_y
        self.speed_y += self.gravity

    def draw(self, surface):
        if self.active and not self.sliced:
            surface.blit(self.image, (int(self.x), int(self.y)))

    def is_hit(self, finger_pos):
        if finger_pos is None or self.sliced or not self.active:
            return False
        fx, fy  = finger_pos
        padding = 15
        return (self.x - padding < fx < self.x + self.size + padding and
                self.y - padding < fy < self.y + self.size + padding)

    def is_off_screen(self):
        return self.y > self.screen_height + 100