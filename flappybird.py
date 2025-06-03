import pygame
import sys
import random

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 400, 600
GROUND_HEIGHT = 100
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FlappyBird")

SKY_BLUE = (135, 206, 235)
CLOUD_WHITE = (255, 255, 255)
GROUND_COLOR = (222, 161, 133)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
ORANGE = (255, 165, 0)

class Cloud:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def update(self):
        self.x -= self.speed
        if self.x + self.width < 0:
            self.x = WIDTH
            self.y = random.randint(20, 100)

    def draw(self, surface):
        pygame.draw.ellipse(surface, CLOUD_WHITE, (self.x, self.y, self.width, self.height))

clouds = [
    Cloud(random.randint(0, WIDTH), random.randint(20, 100), random.randint(80, 120), random.randint(40, 60), random.uniform(0.5, 1.5))
    for _ in range(3)
]

def create_ground_surface():
    ground_surf = pygame.Surface((WIDTH, GROUND_HEIGHT))
    ground_surf.fill(GROUND_COLOR)
    for i in range(0, WIDTH, 20):
        pygame.draw.line(ground_surf, DARK_GREEN, (i, 0), (i, GROUND_HEIGHT), 2)
    return ground_surf

GROUND_SURFACE = create_ground_surface()

def draw_background(surface):
    surface.fill(SKY_BLUE)
    for cloud in clouds:
        cloud.update()
        cloud.draw(surface)

def draw_ground(surface, x_offset):
    surface.blit(GROUND_SURFACE, (x_offset, HEIGHT - GROUND_HEIGHT))
    surface.blit(GROUND_SURFACE, (x_offset + WIDTH, HEIGHT - GROUND_HEIGHT))

class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.width = 34
        self.height = 24
        self.gravity = 0.5
        self.velocity = 0
        self.jump_strength = -8

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        if self.y < 0:
            self.y = 0
            self.velocity = 0

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self, surface):
        center = (int(self.x + self.width / 2), int(self.y + self.height / 2))
        radius = self.width // 2
        pygame.draw.circle(surface, YELLOW, center, radius)
        eye_center = (int(self.x + self.width * 0.65), int(self.y + self.height * 0.35))
        pygame.draw.circle(surface, BLACK, eye_center, 3)
        beak_points = [
            (int(self.x + self.width), int(self.y + self.height / 2)),
            (int(self.x + self.width - 10), int(self.y + self.height / 2 - 5)),
            (int(self.x + self.width - 10), int(self.y + self.height / 2 + 5))
        ]
        pygame.draw.polygon(surface, ORANGE, beak_points)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 60
        self.gap = 140
        self.top_height = random.randint(50, HEIGHT - GROUND_HEIGHT - self.gap - 50)
        self.bottom_y = self.top_height + self.gap
        self.speed = 3
        self.scored = False

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        pygame.draw.rect(surface, GREEN, top_rect)
        pygame.draw.rect(surface, DARK_GREEN, (self.x, self.top_height - 6, self.width, 6))
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, HEIGHT - GROUND_HEIGHT - self.bottom_y)
        pygame.draw.rect(surface, GREEN, bottom_rect)
        pygame.draw.rect(surface, DARK_GREEN, (self.x, self.bottom_y, self.width, 6))

    def collides(self, bird):
        bird_rect = pygame.Rect(bird.x, bird.y, bird.width, bird.height)
        top_pipe_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_pipe_rect = pygame.Rect(self.x, self.bottom_y, self.width, HEIGHT - GROUND_HEIGHT - self.bottom_y)
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)

def start_screen():
    waiting = True
    font_title = pygame.font.SysFont("Arial", 48, bold=True)
    font_instr = pygame.font.SysFont("Arial", 24)
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

        draw_background(window)
        window.blit(font_title.render("FlappyBird", True, BLACK), (90, HEIGHT // 2 - 50))
        window.blit(font_instr.render("Press SPACE to start", True, BLACK), (90, HEIGHT // 2 + 10))
        pygame.display.update()

def game_over_screen(score, high_score):
    waiting = True
    font_title = pygame.font.SysFont("Arial", 48, bold=True)
    font_instr = pygame.font.SysFont("Arial", 24)
    font_score = pygame.font.SysFont("Arial", 32)
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

        draw_background(window)
        window.blit(font_score.render(f"Score: {score}", True, BLACK), (120, HEIGHT // 2 - 60))
        window.blit(font_score.render(f"High Score: {high_score}", True, BLACK), (90, HEIGHT // 2 - 20))
        window.blit(font_instr.render("Game Over! Press SPACE to restart", True, BLACK), (35, HEIGHT // 2 + 30))
        pygame.display.update()

def game_loop():
    clock = pygame.time.Clock()
    score = 0
    bird = Bird()
    pipes = []
    pipe_interval = 1500
    last_pipe_time = pygame.time.get_ticks()
    ground_offset = 0
    ground_speed = 3
    font_score = pygame.font.SysFont("Arial", 32)
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.jump()

        bird.update()

        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > pipe_interval:
            pipes.append(Pipe(WIDTH))
            last_pipe_time = current_time

        for pipe in pipes:
            pipe.update()
            if pipe.collides(bird):
                running = False
            if not pipe.scored and (pipe.x + pipe.width < bird.x):
                score += 1
                pipe.scored = True

        pipes = [pipe for pipe in pipes if pipe.x + pipe.width > 0]

        if bird.y + bird.height >= HEIGHT - GROUND_HEIGHT:
            running = False

        ground_offset -= ground_speed
        if ground_offset <= -WIDTH:
            ground_offset = 0

        draw_background(window)
        for pipe in pipes:
            pipe.draw(window)
        bird.draw(window)
        draw_ground(window, ground_offset)
        window.blit(font_score.render(f"Score: {score}", True, BLACK), (10, 10))
        pygame.display.update()

    return score

def main():
    high_score = 0
    while True:
        start_screen()
        score = game_loop()
        high_score = max(high_score, score)
        game_over_screen(score, high_score)

if __name__ == "__main__":
    main()
