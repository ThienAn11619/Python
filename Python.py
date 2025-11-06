import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
PINK = (255, 192, 203)

# Game variables
base_health = 500
gold = 100  # For upgrades and summoning
wave = 0
enemies = []
units = []
bullets = []
selected_unit = None

# Unit types
UNIT_TYPES = {
    "Fire Snake": {"color": RED, "damage": 10, "range": 100, "cost": 50},
    "Water Snake": {"color": BLUE, "damage": 15, "range": 120, "cost": 60},
    "Dirt Snake": {"color": BROWN, "damage": 20, "range": 80, "cost": 70}
}

# Enemy types
ENEMY_TYPES = {
    "Diddy": {"color": WHITE, "health": 50, "speed": 2, "damage": 10},
    "Skibidi": {"color": GREEN, "health": 100, "speed": 1, "damage": 20},
    "BOSS": {"color": PINK, "health": 200, "speed": 1, "damage": 50}
}

# Modes
MODES = {
    "Easy": 10,
    "Hard": 25,
    "Extreme": 50,
    "Endless": -1  # Infinite
}

# Classes
class Unit:
    def __init__(self, x, y, unit_type):
        self.x = x
        self.y = y
        self.type = unit_type
        self.color = UNIT_TYPES[unit_type]["color"]
        self.damage = UNIT_TYPES[unit_type]["damage"]
        self.range = UNIT_TYPES[unit_type]["range"]
        self.last_shot = 0
        self.upgrade_level = 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 20)

    def shoot(self, enemies, bullets):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > 1000:  # Shoot every second
            for enemy in enemies:
                if ((enemy.x - self.x)**2 + (enemy.y - self.y)**2)**0.5 < self.range:
                    bullets.append(Bullet(self.x, self.y, enemy.x, enemy.y, self.damage))
                    self.last_shot = current_time
                    break

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.color = ENEMY_TYPES[enemy_type]["color"]
        self.health = ENEMY_TYPES[enemy_type]["health"]
        self.speed = ENEMY_TYPES[enemy_type]["speed"]
        self.damage = ENEMY_TYPES[enemy_type]["damage"]
        self.path = [(x, y + i*10) for i in range(60)]  # Simple path down
        self.path_index = 0

    def move(self):
        if self.path_index < len(self.path):
            self.x, self.y = self.path[self.path_index]
            self.path_index += 1
        else:
            global base_health
            base_health -= self.damage
            enemies.remove(self)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

class Bullet:
    def __init__(self, x, y, target_x, target_y, damage):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.damage = damage
        self.speed = 5

    def move(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 5)

# Functions
def draw_text(screen, text, x, y, color=BLACK, size=30):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def main_menu(screen):
    global mode, game_state
    while True:
        screen.fill(WHITE)
        draw_text(screen, "SNAKE TOWER DEFENSE", 200, 100, BLACK, 50)
        draw_text(screen, "Select Mode:", 300, 200)
        for i, m in enumerate(MODES.keys()):
            draw_text(screen, f"{i+1}. {m}", 300, 250 + i*50)
        draw_text(screen, "Press 1-4 to select", 300, 500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "Easy"
                    game_state = "playing"
                    return
                elif event.key == pygame.K_2:
                    mode = "Hard"
                    game_state = "playing"
                    return
                elif event.key == pygame.K_3:
                    mode = "Extreme"
                    game_state = "playing"
                    return
                elif event.key == pygame.K_4:
                    mode = "Endless"
                    game_state = "playing"
                    return

        pygame.display.flip()

def upgrade_menu(screen):
    global gold, units
    while True:
        screen.fill(WHITE)
        draw_text(screen, "Upgrade Menu", 300, 100, BLACK, 40)
        draw_text(screen, f"Gold: {gold}", 300, 150)
        draw_text(screen, "Select unit to upgrade (1-3)", 300, 200)
        for i, unit in enumerate(units):
            draw_text(screen, f"{i+1}. {unit.type} Level {unit.upgrade_level} (Cost: 50)", 300, 250 + i*50)
        draw_text(screen, "Press ESC to return", 300, 500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    idx = event.key - pygame.K_1
                    if idx < len(units) and gold >= 50:
                        units[idx].damage += 5
                        units[idx].upgrade_level += 1
                        gold -= 50

        pygame.display.flip()

def summon_shop(screen):
    global gold, units
    while True:
        screen.fill(WHITE)
        draw_text(screen, "Summon Shop", 300, 100, BLACK, 40)
        draw_text(screen, f"Gold: {gold}", 300, 150)
        draw_text(screen, "Select unit to summon:", 300, 200)
        for i, (name, data) in enumerate(UNIT_TYPES.items()):
            draw_text(screen, f"{i+1}. {name} (Cost: {data['cost']})", 300, 250 + i*50)
        draw_text(screen, "Press ESC to return", 300, 500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    idx = event.key - pygame.K_1
                    unit_name = list(UNIT_TYPES.keys())[idx]
                    cost = UNIT_TYPES[unit_name]["cost"]
                    if gold >= cost:
                        units.append(Unit(random.randint(100, 700), random.randint(100, 500), unit_name))
                        gold -= cost

        pygame.display.flip()

def game_loop(screen, clock):
    global wave, enemies, units, bullets, base_health, gold, game_state
    max_waves = MODES[mode]
    while game_state == "playing":
        screen.fill(WHITE)
        draw_text(screen, f"Wave: {wave}/{max_waves if max_waves != -1 else '∞'}", 10, 10)
        draw_text(screen, f"Base Health: {base_health}", 10, 40)
        draw_text(screen, f"Gold: {gold}", 10, 70)
        draw_text(screen, "Press U for Upgrades, S for Shop, ESC for Menu", 10, 100)

        # Spawn enemies
        if len(enemies) == 0 and (wave < max_waves or max_waves == -1):
            wave += 1
            for _ in range(5 + wave):  # More enemies per wave
                enemy_type = random.choice(list(ENEMY_TYPES.keys()))
                enemies.append(Enemy(random.randint(0, SCREEN_WIDTH), 0, enemy_type))
            gold += 10  # Reward per wave

        # Update and draw units
        for unit in units:
            unit.draw(screen)
            unit.shoot(enemies, bullets)

        # Update and draw enemies
        for enemy in enemies[:]:
            enemy.move()
            enemy.draw(screen)
            if enemy.health <= 0:
                enemies.remove(enemy)
                gold += 5

        # Update and draw bullets
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw(screen)
            for enemy in enemies:
                if ((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)**0.5 < 10:
                    enemy.health -= bullet.damage
                    bullets.remove(bullet)
                    break

        # Check win/lose
        if base_health <= 0:
            game_state = "lose"
            return
        if max_waves != -1 and wave >= max_waves and len(enemies) == 0:
            game_state = "win"
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    upgrade_menu(screen)
                elif event.key == pygame.K_s:
                    summon_shop(screen)
                elif event.key == pygame.K_ESCAPE:
                    game_state = "menu"

        pygame.display.flip()
        clock.tick(FPS)

def end_screen(screen, result):
    while True:
        screen.fill(WHITE)
        draw_text(screen, f"You {result}!", 300, 200, BLACK, 50)
        draw_text(screen, "Press R to restart, ESC to quit", 250, 300)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

# Main
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Tower Defense")
clock = pygame.time.Clock()
mode = None
game_state = "menu"

while True:
    if game_state == "menu":
        main_menu(screen)
    elif game_state == "playing":
        game_loop(screen, clock)
    elif game_state in ["win", "lose"]:
        if end_screen(screen, game_state):
            # Reset
            base_health = 500
            gold = 100
            wave = 0
            enemies = []
            units = []
            bullets = []
            game_state = "menu"