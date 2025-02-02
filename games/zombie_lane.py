#!/usr/bin/env python3
# libraries needed:
# pip install pygame
# to run in terminal: python zombie_lane_3d.py

import pygame
import random
import sys

# Screen dimensions
WIDTH = 600
HEIGHT = 800
FPS = 60

# Lane perspective settings (for 3D style)
LANE_BOTTOM_WIDTH = 400  # width of lane at the bottom
LANE_TOP_WIDTH = 200     # width of lane at the top (vanishing point)
LANE_TOP_Y = 150         # y-coordinate of the top of the lane

# Colors
BACKGROUND_COLOR = (30, 30, 30)    # dark background
LANE_COLOR = (50, 50, 50)          # lane color
PLAYER_COLOR = (0, 255, 0)         # green player
BULLET_COLOR = (255, 255, 0)       # yellow bullet
ZOMBIE_COLORS = [(255, 0, 0), (200, 0, 0), (255, 50, 50)]
UPGRADE_COLOR = (0, 255, 255)      # cyan for upgrades
INSTR_BG_COLOR = (0, 0, 0, 150)    # semi-transparent black for instructions overlay

# Speeds and timing
PLAYER_SPEED = 5
BULLET_SPEED = 10
ZOMBIE_SPEED = 3
SCROLL_SPEED = 2   # background scroll speed (simulated forward motion)
SPAWN_ZOMBIE_INTERVAL = 1500  # ms between zombie spawns
SPAWN_UPGRADE_INTERVAL = 5000  # ms between upgrade spawns
BULLET_COOLDOWN = 300  # ms between shots

# Gun appearance definitions by level
GUN_APPEARANCES = [
    {"color": (255, 255, 255), "thickness": 2},  # Level 1
    {"color": (0, 255, 255), "thickness": 4},      # Level 2
    {"color": (255, 0, 255), "thickness": 6},      # Level 3
    {"color": (255, 255, 0), "thickness": 8},      # Level 4
]
MAX_GUN_LEVEL = len(GUN_APPEARANCES)

def lerp(a, b, t):
    """Linear interpolation between a and b using t (0.0 to 1.0)."""
    return a + (b - a) * t

def get_lane_boundaries(y):
    """
    Compute the left and right x boundaries of the lane for a given y.
    The boundaries linearly interpolate between the top and bottom of the lane.
    """
    # Fraction from top to bottom
    t = (y - LANE_TOP_Y) / (HEIGHT - LANE_TOP_Y)
    t = max(0, min(t, 1))
    left_top = (WIDTH - LANE_TOP_WIDTH) // 2
    right_top = (WIDTH + LANE_TOP_WIDTH) // 2
    left_bottom = (WIDTH - LANE_BOTTOM_WIDTH) // 2
    right_bottom = (WIDTH + LANE_BOTTOM_WIDTH) // 2
    left = int(lerp(left_top, left_bottom, t))
    right = int(lerp(right_top, right_bottom, t))
    return left, right

class Player:
    """
    Represents the player. The player is drawn as a rectangle with a gun.
    The player's horizontal movement is constrained within the lane boundaries.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.gun_level = 0
        self.last_shot_time = 0

    def move(self, dx):
        """
        Move the player horizontally by dx pixels and clamp to lane boundaries.
        """
        self.x += dx
        left, right = get_lane_boundaries(self.y)
        # Clamp player's x so that the entire player rectangle stays within boundaries
        if self.x < left:
            self.x = left
        if self.x + self.width > right:
            self.x = right - self.width

    def shoot(self, current_time):
        """
        Shoot a bullet if cooldown allows.
        Returns a Bullet object or None.
        """
        if current_time - self.last_shot_time >= BULLET_COOLDOWN:
            self.last_shot_time = current_time
            bullet_x = self.x + self.width // 2
            bullet_y = self.y
            return Bullet(bullet_x, bullet_y, self.gun_level)
        return None

    def upgrade_gun(self):
        """
        Upgrade the gun if not at max level.
        """
        if self.gun_level < MAX_GUN_LEVEL - 1:
            self.gun_level += 1

    def draw(self, screen):
        """
        Draw the player and its gun.
        """
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))
        # Draw gun as a line above the player.
        gun_props = GUN_APPEARANCES[self.gun_level]
        start_pos = (self.x + self.width // 2, self.y)
        end_pos = (self.x + self.width // 2, self.y - 20)
        pygame.draw.line(screen, gun_props["color"], start_pos, end_pos, gun_props["thickness"])

class Bullet:
    """
    Represents a bullet fired by the player.
    """
    def __init__(self, x, y, gun_level):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = BULLET_SPEED
        self.gun_level = gun_level

    def update(self):
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, BULLET_COLOR, (self.x, self.y), self.radius)

    def off_screen(self):
        return self.y < 0

class Zombie:
    """
    Represents a zombie enemy.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.color = random.choice(ZOMBIE_COLORS)
        self.speed = ZOMBIE_SPEED

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def off_screen(self):
        return self.y > HEIGHT

class Upgrade:
    """
    Represents a gun upgrade collectible.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20

    def update(self):
        self.y += SCROLL_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, UPGRADE_COLOR, (self.x, self.y, self.size, self.size))

    def off_screen(self):
        return self.y > HEIGHT

def draw_lane(screen):
    """
    Draw the lane as a trapezoid to simulate a 3D perspective.
    """
    bottom_left = ((WIDTH - LANE_BOTTOM_WIDTH) // 2, HEIGHT)
    bottom_right = ((WIDTH + LANE_BOTTOM_WIDTH) // 2, HEIGHT)
    top_left = ((WIDTH - LANE_TOP_WIDTH) // 2, LANE_TOP_Y)
    top_right = ((WIDTH + LANE_TOP_WIDTH) // 2, LANE_TOP_Y)
    pygame.draw.polygon(screen, LANE_COLOR, [top_left, top_right, bottom_right, bottom_left])

def draw_instructions(screen, font):
    """
    Draw instructions in the top left corner in a translucent box.
    """
    instructions = [
        "Controls:",
        "Left/Right arrows: Move",
        "Space: Shoot",
        "H: Toggle Instructions"
    ]
    # Create a surface with per-pixel alpha
    overlay = pygame.Surface((250, 100), pygame.SRCALPHA)
    overlay.fill(INSTR_BG_COLOR)
    screen.blit(overlay, (10, 10))
    for i, line in enumerate(instructions):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (20, 20 + i * 20))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zombie Lane")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    # Initialize player near bottom center of the lane.
    init_x = (WIDTH - LANE_BOTTOM_WIDTH) // 2 + (LANE_BOTTOM_WIDTH - 40) // 2
    player = Player(init_x, HEIGHT - 100)
    bullets = []
    zombies = []
    upgrades = []
    score = 0

    zombie_timer = 0
    upgrade_timer = 0
    show_instructions = True  # Toggle instructions display

    running = True
    while running:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Toggle instructions on/off with H key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-PLAYER_SPEED)
        if keys[pygame.K_RIGHT]:
            player.move(PLAYER_SPEED)
        if keys[pygame.K_SPACE]:
            bullet = player.shoot(current_time)
            if bullet:
                bullets.append(bullet)

        # Spawn zombies: use lane boundaries at LANE_TOP_Y
        if current_time - zombie_timer > SPAWN_ZOMBIE_INTERVAL:
            zombie_timer = current_time
            left_bound, right_bound = get_lane_boundaries(LANE_TOP_Y)
            z_x = random.randint(left_bound, right_bound - 30)
            z_y = LANE_TOP_Y - 30  # spawn just above lane top
            zombies.append(Zombie(z_x, z_y))

        # Spawn upgrades similarly
        if current_time - upgrade_timer > SPAWN_UPGRADE_INTERVAL:
            upgrade_timer = current_time
            left_bound, right_bound = get_lane_boundaries(LANE_TOP_Y)
            u_x = random.randint(left_bound, right_bound - 20)
            u_y = LANE_TOP_Y - 20
            upgrades.append(Upgrade(u_x, u_y))

        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.off_screen():
                bullets.remove(bullet)

        # Update zombies: check bullet collisions and collisions with player
        for zombie in zombies[:]:
            zombie.update()
            if zombie.off_screen():
                zombies.remove(zombie)
            else:
                # Check bullet collision (simple rectangle/circle collision)
                for bullet in bullets[:]:
                    if (zombie.x < bullet.x < zombie.x + zombie.width and
                        zombie.y < bullet.y < zombie.y + zombie.height):
                        zombies.remove(zombie)
                        bullets.remove(bullet)
                        score += 10
                        break
                # Check collision with player (game over)
                if (player.x < zombie.x + zombie.width and
                    player.x + player.width > zombie.x and
                    player.y < zombie.y + zombie.height and
                    player.y + player.height > zombie.y):
                    running = False

        # Update upgrades and check for collection
        for upgrade in upgrades[:]:
            upgrade.update()
            if upgrade.off_screen():
                upgrades.remove(upgrade)
            elif (player.x < upgrade.x + upgrade.size and
                  player.x + player.width > upgrade.x and
                  player.y < upgrade.y + upgrade.size and
                  player.y + player.height > upgrade.y):
                player.upgrade_gun()
                upgrades.remove(upgrade)

        # Drawing
        screen.fill(BACKGROUND_COLOR)
        draw_lane(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for zombie in zombies:
            zombie.draw(screen)
        for upgrade in upgrades:
            upgrade.draw(screen)
        player.draw(screen)

        # Display score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH - 150, 20))

        # Draw instructions overlay if enabled
        if show_instructions:
            draw_instructions(screen, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
